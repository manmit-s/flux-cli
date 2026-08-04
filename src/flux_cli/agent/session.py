from datetime import datetime
import json
from typing import Any
import uuid

from flux_cli.client.llm_client import LLMClient
from flux_cli.config.config import Config
from flux_cli.config.loader import get_data_dir
from flux_cli.context.compaction import ChatCompactor
from flux_cli.context.loop_detector import LoopDetector
from flux_cli.context.manager import ContextManager
from flux_cli.hooks.hook_system import HookSystem
from flux_cli.tools.discovery import ToolDiscoveryManager
from flux_cli.tools.mcp.mcp_manager import MCPManager
from flux_cli.tools.registry import create_default_registry
from flux_cli.safety.approval import ApprovalManager


class Session:
    def __init__(self, config: Config):
        self.config = config
        self.client = LLMClient(config=config)
        self.tool_registry = create_default_registry(config)
        self.context_manager: ContextManager | None = None
        self.discovery_manager = ToolDiscoveryManager(self.config, self.tool_registry)
        self.mcp_manager = MCPManager(config=self.config)
        self.chat_compactor = ChatCompactor(self.client)
        self.approval_manager = ApprovalManager(self.config.approval, self.config.cwd,)
        self.loop_detector = LoopDetector()
        self.hook_system = HookSystem(self.config)
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        self.turn_count = 0

    async def initialize(self) -> None:
        await self.mcp_manager.initialize()
        self.discovery_manager.discover_all()
        self.mcp_manager.register_tools(self.tool_registry)
        self.context_manager = ContextManager(config=self.config, user_memory=self._load_memory(), tools=self.tool_registry.get_tools())
    
    def _load_memory(self) -> str | None:
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = data_dir / "user_memory.json"

        if not path.exists():
            return {'entries': {}}
        
        try:
            content = path.read_text(encoding='utf-8')
            data = json.loads(content)
            entries = data.get('entries')
            if not entries:
                return None
            
            lines = ["User preferences and notes:"]
            for key, value in entries.items():
                lines.append(f"{key} : {value}")
            return "\n".join(lines)

        except:
            return None



    def increment_turn(self) -> int:
        self.turn_count += 1
        self.updated_at = datetime.now()

        return self.turn_count

    def get_stats(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "turn_count": self.turn_count,
            "message_count": self.context_manager.message_count,
            "token_usage": self.context_manager.total_usage,
            "tools_count": len(self.tool_registry.get_tools()),
            "mcp_servers": len(self.tool_registry.connected_mcp_servers),
        }