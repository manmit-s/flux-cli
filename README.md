# Flux-CLI

An AI coding agent built from scratch — inspired by Claude Code CLI — with full multi-tool orchestration, streaming responses, sub-agent delegation, MCP server integration, and an interactive terminal UI.

## 🎯 Project Aim

This project is a **learning initiative** designed to understand and implement core concepts behind intelligent coding agents:

- **How AI agents reason** about problems and select appropriate tools
- **Multi-tool orchestration** — deciding which tools to use and in what order
- **Iterative refinement** — analyzing code, identifying issues, and autonomously refactoring
- **Streaming capabilities** — real-time response generation and token consumption
- **Error handling & resilience** — retry logic, exponential backoff, graceful degradation
- **Async patterns** — non-blocking operations for API calls and task orchestration
- **Context management** — intelligent conversation history with automatic compression
- **Extensible tool system** — plugin architecture with built-in, sub-agent, and MCP tools

## 📋 Completed Features

### 1. **LLM Client (AsyncOpenAI Integration)**
- ✅ Async OpenAI client with lazy initialization
- ✅ Support for streaming and non-streaming responses
- ✅ Stream event architecture (`StreamEvent`, `TextDelta`, `TokenUsage`)
- ✅ Tool call streaming — incremental `TOOL_CALL_START`, `TOOL_CALL_DELTA`, `TOOL_CALL_COMPLETE` events
- ✅ Error handling with retry logic:
  - Rate limit handling with exponential backoff
  - Connection error recovery
  - API error catching and reporting
- ✅ Configurable API key via `.env` file
- ✅ Support for different LLM providers (configurable base URL)
- ✅ Tool schema building from tool definitions

### 2. **Response Event System**
- ✅ Event-based architecture for streaming responses
- ✅ Event types: `TEXT_DELTA`, `TOOL_CALL_START`, `TOOL_CALL_DELTA`, `TOOL_CALL_COMPLETE`, `MESSAGE_COMPLETE`, `ERROR`
- ✅ Type-safe response events with usage tracking
- ✅ Tool call delta tracking for incremental argument streaming
- ✅ Consistent interface for both streaming and non-streaming modes

### 3. **Async Generator Pattern**
- ✅ Unified caller interface using `async for`
- ✅ Generator-based streaming with `yield`
- ✅ Single entry point for different response modes

### 4. **Agent Core & Event System**
- ✅ `Agent` orchestrator with async context manager support
- ✅ Event-driven architecture with `AgentEvent` and `AgentEventType`
- ✅ Event lifecycle: `AGENT_START` → `TEXT_DELTA` × N → `TOOL_CALL_START/COMPLETE` × N → `TEXT_COMPLETE` → `AGENT_END`
- ✅ Error propagation through event system (`AGENT_ERROR`)
- ✅ Full agentic loop with multi-turn tool calling
- ✅ Message context storage via `ContextManager`
- ✅ Tool call event streaming with result tracking
- ✅ Maximum turns enforcement with graceful error reporting

### 5. **Session Management**
- ✅ `Session` class orchestrating lifecycle of client, tools, context, and MCP
- ✅ UUID-based session identification with timestamps
- ✅ Turn counting and tracking
- ✅ User memory persistence across sessions (JSON-based)
- ✅ Initialization lifecycle: MCP → Tool Discovery → Tool Registration → Context Setup

### 6. **Configuration System**
- ✅ Pydantic-based hierarchical configuration (`Config`, `ModelConfig`, `ShellEnvironmentPolicy`, `MCPServerConfig`)
- ✅ Multi-level config loading — system-level → project-level → CLI overrides
- ✅ TOML-based configuration files (`.flux-cli/config.toml`)
- ✅ Auto-detection of `AGENT.md` files for developer instructions
- ✅ Configurable model, temperature, context window, max turns
- ✅ Shell environment policy — secret masking, env variable setting
- ✅ MCP server configuration with stdio and HTTP/SSE transport
- ✅ Allowed tools restriction list
- ✅ `--cwd` CLI option for working directory
- ✅ Config validation on startup

### 7. **Context Management**
- ✅ `ContextManager` with full message history tracking
- ✅ Token counting per message
- ✅ System prompt construction with identity, environment, tool guidelines, security
- ✅ Automatic context compression trigger (80% of context window)
- ✅ Smart tool output pruning — protects recent outputs, prunes older ones
- ✅ Compression-aware continuation with context restoration
- ✅ Usage tracking (`latest_usage` + `total_usage`)

### 8. **Context Compression**
- ✅ `ChatCompactor` for summarizing conversation history
- ✅ Smart history formatting for compression (truncates long tool outputs, assistant responses)
- ✅ Structured compression output (original goal, completed actions, current state, remaining tasks)
- ✅ Seamless continuation with "don't repeat completed actions" guard
- ✅ Compression prompt with detailed template

### 9. **Tool System Architecture**
- ✅ Abstract `Tools` base class with Pydantic schema validation
- ✅ `ToolKind` enum — `READ`, `WRITE`, `SHELL`, `NETWORK`, `MEMORY`, `MCP`
- ✅ `ToolRegistry` with registration, lookup, MCP tool segregation
- ✅ `ToolInvocation` — parameter + cwd context for execution
- ✅ `ToolResult` — standardized result with output, error, metadata, diff, truncation flag
- ✅ `FileDiff` — unified diff generation for file operations
- ✅ `ToolConfirmation` — confirmation model for mutating operations
- ✅ Automatic OpenAI schema generation from Pydantic models (`to_openai_schema()`)
- ✅ `ToolDiscoveryManager` — auto-discovers custom tools from `.ai-agent/tools/` directories
- ✅ Parameter validation with descriptive error messages

### 10. **Built-in Tools (11 Tools)**

| Tool | Kind | Description |
|------|------|-------------|
| `read_file` | READ | Read text files with line numbers, offset/limit, binary detection |
| `write_file` | WRITE | Create/overwrite files with automatic parent directory creation |
| `edit` | WRITE | Precise surgical text replacement with uniqueness checks |
| `shell` | SHELL | Command execution with timeout, blocked command safety, environment control |
| `list_dir` | READ | Directory listing with hidden file toggle |
| `grep` | READ | Regex search across files with case-insensitive option |
| `glob` | READ | File pattern matching with recursive `**` support |
| `web_search` | NETWORK | DuckDuckGo web search integration |
| `web_fetch` | NETWORK | HTTP fetch with automatic fallback to proxy on 403/5xx |
| `todos` | MEMORY | Session-scoped task tracking (add/complete/list/clear) |
| `memory` | MEMORY | Persistent user memory stored across sessions |

### 11. **Sub-Agent System**
- ✅ `SubAgentTool` — spawns child agents for specialized tasks
- ✅ `SubAgentDefinition` — name, description, goal prompt, allowed tools, timeout
- ✅ `codebase_investigator` — explores code structure using read/grep/glob/list_dir (read-only)
- ✅ `code_reviewer` — reviews code changes for bugs, security, improvements
- ✅ Isolated context execution with turn and timeout limits
- ✅ Result aggregation — tool calls made, final response, termination reason

### 12. **MCP (Model Context Protocol) Integration**
- ✅ MCP server management with connect/disconnect lifecycle
- ✅ Support for stdio transport (local processes) and SSE transport (remote servers)
- ✅ Automatic tool registration from MCP server capabilities
- ✅ Configurable startup timeout and environment variables
- ✅ Health status tracking (disconnected/connecting/connected/error)
- ✅ Graceful shutdown with resource cleanup

### 13. **CLI & Terminal UI**
- ✅ Click-based CLI with command-line argument parsing
- ✅ Rich terminal output with custom theme styling (16+ semantic styles)
- ✅ Dual mode: single-prompt (`python main.py "prompt"`) and interactive mode
- ✅ Interactive commands: `/exit`, `/help` support
- ✅ Real-time streaming text display with `stream_assistant_delta()`
- ✅ **Tool call panels** — rich panels with tool name, call ID, arguments table, status
- ✅ **Tool result rendering** — syntax-highlighted code, diffs, shell output, search results
- ✅ Per-tool-kind border styling (read=cyan, write=yellow, shell=magenta, etc.)
- ✅ Welcome panel with model info, cwd, and available commands
- ✅ Error suppression for clean shutdown (unclosed resource warnings)

### 14. **Prompt System**
- ✅ Comprehensive system prompt generation with multiple sections
- ✅ Identity & role definition
- ✅ Environment context (date, OS, working directory, shell)
- ✅ Tool usage guidelines with best practices
- ✅ AGENTS.md specification integration
- ✅ Security guidelines (secrets, path validation, prompt injection defense)
- ✅ Operational guidelines (tone, primary workflows, error recovery)
- ✅ Developer instructions (from config/AGENT.md)
- ✅ User instructions support
- ✅ User memory injection
- ✅ Tool list auto-generation with descriptions

### 15. **Utility Modules**
- ✅ `utils/paths.py` — path resolution, relative display, parent directory creation, binary file detection
- ✅ `utils/text.py` — token counting (tiktoken), text truncation by tokens/lines/characters
- ✅ `utils/errors.py` — `AgentError` and `ConfigError` with structured error details

## 📁 Project Structure

```
flux/
├── main.py                      # CLI entry point with Click, interactive/single modes
├── agent/
│   ├── agent.py                # Agent orchestrator with multi-turn agentic loops
│   ├── events.py               # AgentEvent, AgentEventType (lifecycle + tool call events)
│   └── session.py              # Session: client + registry + context + MCP lifecycle
├── client/
│   ├── llm_client.py           # AsyncOpenAI wrapper with streaming, retry, tool call support
│   └── response.py             # StreamEvent, TextDelta, TokenUsage, ToolCall types
├── config/
│   ├── __init__.py
│   ├── config.py               # Pydantic Config, ModelConfig, ShellEnvironmentPolicy, MCPServerConfig
│   └── loader.py               # TOML config loading, multi-level merge, AGENT.md detection
├── context/
│   ├── compaction.py           # ChatCompactor — context summarization when limit is hit
│   └── manager.py              # ContextManager — message history, tokens, pruning, compression
├── prompts/
│   └── system.py               # System prompt generation (identity, tools, security, guidelines)
├── tools/
│   ├── base.py                 # Tools ABC, ToolInvocation, ToolResult, FileDiff, ToolKind
│   ├── registry.py             # ToolRegistry, create_default_registry
│   ├── discovery.py            # ToolDiscoveryManager — custom tool auto-discovery
│   ├── subagent.py             # SubAgentTool, SubAgentDefinition, default definitions
│   ├── builtin/
│   │   ├── __init__.py         # Tool exports and get_all_builtin_tools()
│   │   ├── read_file.py        # File reading with line numbers, offset, binary detection
│   │   ├── write_file.py       # File creation/overwrite with diff tracking
│   │   ├── edit_file.py        # Surgical text replacement with uniqueness validation
│   │   ├── shell.py            # Command execution with timeout, safety blocks
│   │   ├── list_dir.py         # Directory listing
│   │   ├── grep.py             # Regex file search
│   │   ├── glob.py             # Glob pattern file matching
│   │   ├── web_search.py       # DuckDuckGo search integration
│   │   ├── web_fetch.py        # HTTP fetch with proxy fallback
│   │   ├── todo.py             # Session-scoped task tracking
│   │   └── memory.py           # Persistent user memory
│   └── mcp/
│       ├── client.py           # MCPClient — stdio/SSE transport, tool listing, invocation
│       ├── mcp_manager.py      # MCPManager — server lifecycle, tool registration
│       └── mcp_tool.py         # MCPTool adapter — wraps MCP tools in Tool interface
├── ui/
│   └── tui.py                  # TUI with Rich themes, tool panels, streaming, syntax highlighting
├── utils/
│   ├── errors.py               # AgentError, ConfigError
│   ├── paths.py                # Path resolution, binary detection, directory creation
│   └── text.py                 # Token counting, text truncation
├── .env                        # API keys and configuration (git-ignored)
├── .gitignore
└── README.md
```
---

## See the [Architecture Documentation](ARCHITECTURE.md).

## 🔧 Setup & Usage

### Prerequisites
- Python 3.10+
- OpenRouter API key (or other OpenAI-compatible API)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/flux.git
cd flux

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install openai python-dotenv pydantic httpx rich click tiktoken platformdirs tomli duckduckgo-search fastmcp
```

### Configuration
Create a `.env` file in the project root:
```env
API_KEY=your_api_key_here
BASE_URL=https://openrouter.ai/api/v1  # Optional, default for OpenRouter
```

Or use a TOML config file at `~/.config/flux-cli/config.toml`:
```toml
[model]
name = "mistralai/mistral-small-2603"
temperature = 1.0
context_window = 256000

max_turns = 100

[shell_environment]
exclude_patterns = ["*KEY", "*TOKEN", "*SECRET"]
```

Project-level config goes in `.flux-cli/config.toml` relative to CWD.

### Running
```bash
# Single prompt mode
python main.py "Find all Python files and count the lines"

# Interactive mode (REPL)
python main.py

# Specify working directory
python main.py --cwd /path/to/project "Analyze this codebase"

# Interactive commands:
#   /help     - Show help
#   /exit     - Exit the CLI
```

## 🎨 Terminal UI Highlights

The TUI (`ui/tui.py`) provides a rich terminal experience:

- **Welcome Panel**: Contextual startup info with model, CWD, and available commands
- **Streaming Text**: Real-time assistant response display
- **Tool Call Panels**: Each tool invocation gets a styled panel with:
  - Tool name and short call ID
  - Arguments table (ordered by most important params)
  - Running/done status indicators
  - Kind-based border styling (read=cyan, write=yellow, shell=magenta, network=blue, memory=green, mcp=cyan)
- **Result Rendering**:
  - `read_file` → Syntax-highlighted code with line numbers
  - `write_file`/`edit` → Unified diff display
  - `shell` → Command echo + output with exit code
  - `grep` → Match count summary + results
  - `web_search`/`web_fetch` → Summary with status, results count
- **Truncation Warnings**: When tool output exceeds token limits

## 📚 Key Concepts Explored

### 1. Async Generators
Why use `yield` in async functions? Creates a consistent interface where callers always use `async for`, regardless of streaming mode. Both streaming and non-streaming LLM responses yield events through the same channel.

### 2. Error Resilience
Implemented retry logic with exponential backoff for:
- Rate limiting (429 errors)
- Connection issues
- API errors

### 3. Type Safety
Using Python type hints and Pydantic throughout to catch issues early:
- `AsyncGenerator[StreamEvent, None]`
- `AsyncOpenAI | None`
- Pydantic `BaseModel` for all tool parameters
- Strict validation with descriptive error messages

### 4. Lazy Initialization
API client is only created when first needed, reducing startup overhead.

### 5. Context Compression
Automatic conversation summarization when approaching context window limits. Uses a child LLM call to create a structured continuation prompt that preserves goal, completed actions, and remaining tasks.

### 6. Plugin Architecture
Three-tier tool system:
- **Built-in** — core tools for file operations, code search, web access
- **Sub-agents** — spawned child agents with isolated context for specialized tasks
- **MCP** — external tool servers via Model Context Protocol

### 7. Config Layering
Configuration is merged from multiple sources with increasing priority:
`System config → Project config → CLI arguments`

## 📋 Next Steps

1. **User Approval System**: Implement tool call approval workflow for mutating operations
2. **Multi-turn Conversation Persistence**: Full conversation history across CLI sessions
3. **Code-aware Editing**: AST-based code operations for safer refactoring
4. **Plugin Hot-Reloading**: Dynamic tool registration without restart
5. **Performance Optimizations**: Token caching, response caching, parallel tool execution
6. **Testing Suite**: Comprehensive unit and integration tests
7. **Configuration UI**: Interactive config wizard for first-time setup
8. **Documentation Site**: Full API docs with examples

## 👨‍🏫 Credits 
**Inspired by and learning from:**
- **[Rivaan Ranawat](https://github.com/RivaanRanawat)** — Tutor and educational content creator

## 🤝 Contributing

This is a personal learning project, but feel free to fork and experiment!

---
> **Note**: This project is actively being developed as a learning exercise. Expect API changes and refactoring as new features are added.