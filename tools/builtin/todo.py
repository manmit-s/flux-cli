from pydantic import BaseModel, Field
from tools.base import ToolInvocation, ToolKind, ToolResult, Tools


class ToDoParams(BaseModel):
    action: str = Field(
        ..., description="Action: 'add', 'complete', 'list', 'clear'"
    )
    id: str | None = Field(..., description='Todo ID (for complete)')
    content: str | None = Field(None, description='Todo content (for add)')

class ToDoTool(Tools):
    name = 'todos'
    description = 'Manage a task list for current session. Use this to track progress on multi-step tasks'
    kind = ToolKind.MEMORY
    schema = ToDoParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = ToDoParams(**invocation.params)
        ###BOOKMARK###
        try:
            results = DDGS().text(
                params.query,
                region='us-en',
                safesearch='off',
                timelimit='y',
                page=1,
                backend='auto'
            )
        except Exception as e:
            return ToolResult.error_result(f"Search failed: {e}")
        
        if not results:
            return ToolResult.success_result(
                f"No results found for: {params.query}", 
                metadata={
                'results' : 0,
            })
        

        output_lines = [f"Search results for: {params.query}"]

        for i, result in enumerate(results, start=1):
            output_lines.append(f"{i}. Title: {result['title']}")
            output_lines.append(f"   URL: {result['href']}")
            if result.get('body'):
                output_lines.append(f"   Snippet: {result['body']}")

            output_lines.append("")
        
        return ToolResult.success_result(
            '\n'.join(output_lines), 
            metadata={
                'results': len(results),
            }
        )