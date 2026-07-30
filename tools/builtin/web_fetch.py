import ipaddress
from urllib.parse import urljoin, urlparse
import httpx
from pydantic import BaseModel, Field
from tools.base import ToolInvocation, ToolKind, ToolResult, Tools


DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/126.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


class WebFetchParams(BaseModel):
    url: str = Field(
        ..., description="URL to fetch (must be http:// or https://)')"
    )
    timeout: int = Field(30, ge=5, le=120, description='Request timeout in seconds (default: 120s)',)

class WebFetchTool(Tools):
    name = 'web_fetch'
    description = 'Fetch content from a URL. Returns the response body as text'
    kind = ToolKind.NETWORK
    schema = WebFetchParams

    def _proxy_url(self, url: str) -> str:
        parsed = urlparse(url)
        target = parsed.netloc + parsed.path
        if parsed.query:
            target += f"?{parsed.query}"
        return f'https://r.jina.ai/http://{target}'

    def _is_blocked_host(self, host: str | None) -> bool:
        if not host:
            return True

        normalized = host.strip().lower().rstrip(".")
        if normalized in {"localhost"} or normalized.endswith(".localhost"):
            return True

        try:
            ip = ipaddress.ip_address(normalized)
        except ValueError:
            return False

        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> tuple[str, int]:
        current_url = url
        for _ in range(5):
            parsed = urlparse(current_url)
            if self._is_blocked_host(parsed.hostname):
                raise ValueError("Refusing to fetch localhost, private, or reserved network address")

            response = await client.get(current_url)
            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    break
                current_url = urljoin(current_url, location)
                continue

            response.raise_for_status()
            return response.text, response.status_code

        raise ValueError("Too many redirects")

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = WebFetchParams(**invocation.params)

        parsed = urlparse(params.url)
        if not parsed.scheme or parsed.scheme not in ('http', 'https'):
            return ToolResult.error_result(f"Url must be http:// or https://")
        if self._is_blocked_host(parsed.hostname):
            return ToolResult.error_result("Refusing to fetch localhost, private, or reserved network address")

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(params.timeout),
                follow_redirects=False,
                headers=DEFAULT_HEADERS,

            ) as client:
                try:
                    text, status_code = await self._fetch(client, params.url)
                    fetched_via_proxy = False
                    source_url = params.url
                except httpx.HTTPStatusError as direct_error:
                    if direct_error.response.status_code not in {403, 429, 500, 502, 503, 504}:
                        raise

                    proxy_url = self._proxy_url(params.url)
                    text, status_code = await self._fetch(client, proxy_url)
                    fetched_via_proxy = True
                    source_url = proxy_url
        except httpx.HTTPStatusError as e:
            return ToolResult.error_result(
                f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            )
        except ValueError as e:
            return ToolResult.error_result(str(e))
        except Exception as e:
            return ToolResult.error_result(f"Fetch failed: {e}")

        if len(text) > 100*1024:
            text = text[:100*1024] + '\n.... [content truncated]'
        
        return ToolResult.success_result(
            text, 
            metadata={
                'status_code': status_code,
                'content_length' : len(text),
                'source_url': source_url,
                'used_proxy': fetched_via_proxy,
            }
        )
