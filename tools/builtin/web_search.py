from pydantic import BaseModel, Field
from tools.base import ToolInvocation, ToolKind, ToolResult, Tools
from ddgs import DDGS

class WebSearchParams(BaseModel):
    query: str = Field(
        ..., description="Search query"
    )
    max_results: int = Field(10, ge=1, le=20, description='Maximum results to return (default is 10)',)

class WebSearchTool(Tools):
    name = 'web_search'
    description = 'Search the web for information. Returns search results with titles, URLs and snippets'
    kind = ToolKind.NETWORK
    schema = WebSearchParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = WebSearchParams(**invocation.params)

        try:
            results = list(DDGS().text(params.query, max_results=params.max_results))
            if not results and ('-' in params.query or '_' in params.query):
                cleaned_query = params.query.replace('-', ' ').replace('_', ' ')
                results = list(DDGS().text(cleaned_query, max_results=params.max_results))
        except Exception as e:
            return ToolResult.error_result(f"Search failed: {e}")
        
        limited_results = list(results)[:params.max_results]

        if not limited_results:
            return ToolResult.success_result(
                f"No results found for: {params.query}", 
                metadata={
                'results' : 0,
            })
        

        output_lines = [f"Search results for: {params.query}"]

        for i, result in enumerate(limited_results, start=1):
            output_lines.append(f"{i}. Title: {result.get('title', '(untitled)')}")
            output_lines.append(f"   URL: {result.get('href', '')}")
            if result.get('body'):
                output_lines.append(f"   Snippet: {result['body']}")

            output_lines.append("")
        
        return ToolResult.success_result(
            '\n'.join(output_lines), 
            metadata={
                'results': len(limited_results),
            }
        )
