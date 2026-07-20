from config.config import Config
from tools.base import ToolInvocation, ToolKind, ToolResult, Tools
from tools.mcp.client import MCPClient, MCPToolInfo
from utils.paths import resolve_path

class MCPTool(Tools):
    def __init__(self, config: Config, client: MCPClient, tool_info: MCPToolInfo, name: str) -> None:
        super().__init__(config)
        self._tool_info = tool_info
        self._client = client
        self.name = name
        self.description = self._tool_info.description
        input_schema = self._tool_info.input_schema or {}
        self.schema = {
            'type' : 'object',
            'properties' :  input_schema.get('properties', {}),
            'required' : input_schema.get('required', []),
        }

    def is_mutating(self, params) -> bool:
        return True

    description = 'List content of directory'
    kind = ToolKind.MCP
    schema = ListDirParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = ListDirParams(**invocation.params)

        dir_path = resolve_path(invocation.cwd, params.path)

        if not dir_path.exists() or not dir_path.is_dir():
            return ToolResult.error_result(f"Directory does not exist: {dir_path}")
        
        try:
            items = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except Exception as e:
            return ToolResult.error_result(
                f"Error listing directory: {e}"
            )

        if not params.include_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        if not items:
            return ToolResult.success_result(
                'Directory is empty', 
                metadata = {
                    'path' : str(dir_path),
                    'entries' : 0
                },
                )
        
        lines = []

        for item in items:
            if item.is_dir():
                lines.append(f"{item.name}/")
            else:
                lines.append(item.name)
        
        return ToolResult.success_result(
            '\n'.join(lines),
            metadata = {
                'path' : str(dir_path),
                'entries' : len(items)
            },
            )
        
