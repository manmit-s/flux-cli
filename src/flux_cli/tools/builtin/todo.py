import uuid

from pydantic import BaseModel, Field, field_validator
from flux_cli.config.config import Config
from flux_cli.tools.base import ToolInvocation, ToolKind, ToolResult, Tools
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED


class ToDoParams(BaseModel):
    action: str = Field(
        ..., description="Action: 'add', 'complete', 'list', 'clear'"
    )
    id: str | None = Field(None, description='Todo ID (for complete)')
    content: str | None = Field(None, description='Todo content (for add)')

    @field_validator('id', mode='before')
    @classmethod
    def coerce_id_to_str(cls, v):
        if v is None or isinstance(v, str):
            return v
        return str(v)

class ToDoTool(Tools):
    name = 'todos'
    description = 'Manage a task list for current session. Use this to track progress on multi-step tasks'
    kind = ToolKind.MEMORY
    schema = ToDoParams

    def __init__(self, config: Config):
        super().__init__(config)
        self._todos: dict[str, str] = {}
     
    def _display_todos(self) -> str:
        console = Console()
        table = Table(title="Todo List", box=ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Content", style="green")

        for todo_id, content in self._todos.items():
            table.add_row(todo_id, content)

        # Fix #14: removed console.print(table) — it caused duplicate display
        # (once from the direct print, once from the caller rendering the returned string)
        return str(table)

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = ToDoParams(**invocation.params)

        if params.action.lower() == 'add':
            if not params.content:
                return ToolResult.error_result("`content` required for 'add' action")

            todo_id = str(uuid.uuid4())[:8]
            self._todos[todo_id] = params.content

            return ToolResult.success_result(f"Added todo [{todo_id}] : {params.content}")
        elif params.action.lower() == 'complete':
            if not params.id:
                return ToolResult.error_result("`id` required for 'complete' action")
            if params.id not in self._todos:
                return ToolResult.error_result(f"Todo not found: {params.id}")
            
            content = self._todos.pop(params.id)
            return ToolResult.success_result(f"Completed todo [{params.id}] : {content}")
        
        elif params.action.lower() == 'list':
            if not self._todos:
                return ToolResult.success_result("No todos left!")
            
            return ToolResult.success_result(self._display_todos())
        elif params.action.lower() == 'clear':
            count = len(self._todos)
            self._todos.clear()
            return ToolResult.success_result(f"Cleared {count} todos")
        else:
            return ToolResult.error_result(f"Unknown Action: {params.action}")