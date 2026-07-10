from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from config.config import Config
from tools.base import Tools

class SubAgentParams(BaseModel):
    goal: str


@dataclass
class SubAgentDefinition:
    name: str
    description: str
    goal_prompt: str
    allowed_tools: list[str] | None = None
    max_turns: int = 20
    timeout_seconds: float = 600

class SubAgentTool(Tools):
    def __init__(self, config: Config, definition: SubAgentDefinition):
        super().__init__(config)
        self.definition = definition
    
    @property
    def name(self) -> str:
        return f"subagent_{self.definition.name}"
    
    @property
    def description(self) -> str:
        return f"description_{self.definition.description}"
    
    schema = SubAgentParams

    def is_mutating(self, params: dict[str, Any]):
        return super().is_mutating(params)

    #BOOKMARK