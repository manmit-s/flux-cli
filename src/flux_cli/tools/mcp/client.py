from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport, SSETransport

from flux_cli.config.config import MCPServerConfig

class MCPServerStatus(str, Enum):
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    ERROR = 'error'


@dataclass
class MCPToolInfo:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    server_name: str = ""


class MCPClient:
    def __init__(self, name: str, config: MCPServerConfig, cwd: Path) -> None:
        self.name = name
        self.config = config
        self.cwd = cwd
        self.status = MCPServerStatus.DISCONNECTED
        self._client: Client | None = None

        self._tools: dict[str, MCPToolInfo] = dict()

    @property
    def tools(self) -> list[MCPToolInfo]:
        return list(self._tools.values())
    
    def _create_transport(self) -> StdioTransport | SSETransport:
        if self.config.command:
            env = os.environ.copy()
            env.update(self.config.env)
            cwd_str = str(self.config.cwd) if self.config.cwd else str(self.cwd)
            return StdioTransport(
                command=self.config.command,
                args = list(self.config.args),
                env=env,
                cwd = cwd_str,
            )
        else:
            return SSETransport(url = self.config.url)

    async def connect(self) -> None:
        if self.status == MCPServerStatus.CONNECTED:
            return

        self.status = MCPServerStatus.CONNECTING

        try:
            self._client = Client(transport=self._create_transport())
            await self._client.__aenter__()
            tool_result = await self._client.list_tools()
            for tool in tool_result:
                self._tools[tool.name] = MCPToolInfo(
                    name=tool.name,
                    description=tool.description if hasattr(tool, "description") else "",
                    input_schema=tool.inputSchema if hasattr(tool, "inputSchema") else {},
                    server_name=self.name,
                )
            self.status = MCPServerStatus.CONNECTED
        except Exception as e:
            self.status = MCPServerStatus.ERROR
            raise

    async def disconnect(self) -> None:
        if self._client:
            try:
                transport = getattr(self._client, 'transport', None)
                await self._client.__aexit__(None, None, None)
                if transport and hasattr(transport, '_process') and transport._process:
                    proc = transport._process
                    if proc and hasattr(proc, '_transport') and proc._transport:
                        proc._transport._closed = True
                        for p in (getattr(proc._transport, '_stdin', None), getattr(proc._transport, '_stdout', None), getattr(proc._transport, '_stderr', None)):
                            if p:
                                p._closed = True
            except Exception:
                pass
            self._client = None

        self._tools.clear()
        self.status = MCPServerStatus.DISCONNECTED

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]):
        if not self._client or self.status != MCPServerStatus.CONNECTED:
            raise RuntimeError(f"Not connected to the server {self.name}")

        result = await self._client.call_tool(tool_name, arguments)

        output = []
        for item in result.content:
            if hasattr(item, 'text'):
                output.append(item.text)
            else:
                output.append(str(item))

        return {'output' : '\n'.join(output), 
                'is_error' : result.is_error,}