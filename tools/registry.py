from typing import Any
from pathlib import Path

from tools.base import ToolInvocation, ToolResult, Tools
import logging

from tools.builtin import ReadFileTool, get_all_builtin_tools


logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tools] = {}
    
    def register(self, tool: Tools) -> None:
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool: {tool.name}")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        
        return False
    
    def get(self, name: str) -> Tools | None:
        if name in self._tools:
            return self._tools[name]
    
        return None

    def get_tools(self) -> list[Tools]:
        tools: list[Tools] = []

        for tool in self._tools.values():
            tools.append(tool)

        return tools

    def get_schemas(self) -> list[dict[str, Any]]:
        return [tool.to_openai_schema() for tool in self.get_tools()]

    async def invoke(self, 
            name: str, 
            params: dict[str, Any], 
            cwd: Path) -> ToolResult:
            tool = self.get(name)

            if tool is None:
                return ToolResult.error_result(
                    f"Unknown Tool: {name}",
                    metadata = {'tool_name' : name},
                )
            
            validation_errors = tool.validate_params(params)
            if validation_errors:
                return ToolResult.error_result(
                    f"Invalid Parameters: {'; '.join(validation_errors)}",
                    metadata = {'tool_name' : name, 'validation_errors' : validation_errors}
                )
            
            invocation = ToolInvocation(
                params= params,
                cwd = cwd,

            )
            try:
                result = await tool.execute(invocation)
            except Exception as e:
                logger.exception(f"Tool {name} raised an unexpected error")
                result = ToolResult.error_result(
                    f'Internal Error: {str(e)}',
                    metadata = {'tool_name': name}
                )
            
            return result
            
def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    for tool_class in get_all_builtin_tools():
        registry.register(tool_class())

    return registry