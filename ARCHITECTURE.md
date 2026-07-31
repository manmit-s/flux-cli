## System Architecture

### Overview
Flux-CLI is built using an event-driven, multi-tiered architecture that orchestrates LLM interactions, tool executions, background hook triggers, safety approval policies, and interactive terminal UI rendering.

---

### Component Overview

```
                      +------------------+
                      |     CLI REPL     |
                      |    (main.py)     |
                      +--------+---------+
                               |
                               v
                      +------------------+
                      |   Agent Engine   | <-----> [ Hook System ]
                      | (agent/agent.py) |
                      +--------+---------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
    +---------------+  +---------------+  +---------------+
    | Context Engine|  | Tool Registry |  |  LLM Client   |
    | (compaction & |  | (built-in &   |  | (AsyncOpenAI  |
    |  pruning)     |  |     MCP)      |  |   wrapper)    |
    +---------------+  +---------------+  +---------------+
```

---

### 1. LLMClient Class (`client/llm_client.py`)
```text
LLMClient
├── get_client()              # Lazy initialization of AsyncOpenAI
├── chat_completion()         # Main entry point with retry logic & tool support
│   ├── Builds kwargs with model, messages, stream, max_tokens
│   ├── Converts tools to OpenAI function schemas (tool_choice="auto")
│   ├── Retry on RateLimitError (exponential backoff: 2^attempt)
│   ├── Retry on APIConnectionError (exponential backoff)
│   └── Fail immediately on APIError
├── _stream_response()        # Yields TEXT_DELTA, TOOL_CALL_START/DELTA/COMPLETE, MESSAGE_COMPLETE
├── _non_stream_response()    # Returns complete response with tool calls at once
├── _build_tools()            # Converts tool schemas to OpenAI function-calling format
└── close()                   # Async cleanup
```

---

### 2. Agent Orchestrator (`agent/agent.py`)
```text
Agent
├── __init__(config)                     # Creates Session & HookManager
├── run(message)                         # Main entry point (async generator)
│   ├── Yields AGENT_START event & triggers 'on_start' hook
│   ├── Adds user message to ContextManager
│   ├── Calls _agentic_loop() inside try...except block
│   │   └── Yields each event from loop
│   ├── Triggers 'on_success' hook if turn finishes normally
│   ├── Triggers 'on_error' hook on exceptions / turn limits
│   └── Yields AGENT_END with final_response
├── _agentic_loop()                      # Multi-turn agentic loop
│   ├── For turn in range(max_turns):
│   │   ├── Check context compression (triggers at 80% context window & 'on_compaction' hook)
│   │   ├── Get tool schemas from registry
│   │   ├── Send messages + tools to LLMClient
│   │   ├── Stream TEXT_DELTA events
│   │   ├── Collect ToolCall events
│   │   ├── Add assistant message with tool calls to context
│   │   ├── If no tool calls -> finalize (update usage, prune tool output)
│   │   ├── For each tool call:
│   │   │   ├── Trigger 'pre_tool_use' hook
│   │   │   ├── Yields TOOL_CALL_START
│   │   │   ├── Check approval policy (on-request / auto / yolo)
│   │   │   ├── Invoke tool via registry
│   │   │   ├── Trigger 'post_tool_use' hook with results
│   │   │   └── Yields TOOL_CALL_COMPLETE with result
│   │   └── Add tool results to context
│   └── If max turns reached -> AGENT_ERROR
└── __aenter__/__aexit__                 # Async context manager
    ├── __aenter__: Session.initialize() -> MCP, discovery, context, hooks
    └── __aexit__: Close client, shutdown MCP
```

---

### 3. Hook System (`hooks/hook_system.py` & `hooks/manager.py`)
```text
HookManager
├── trigger_on_start(model, cwd)               # Executes shell command for on_start
├── trigger_on_success(response)               # Executes shell command for on_success
├── trigger_on_error(error_msg)                # Executes shell command for on_error
├── trigger_pre_tool_use(name, args)           # Executes shell command for pre_tool_use
├── trigger_post_tool_use(name, args, res)     # Executes shell command for post_tool_use
└── trigger_on_compaction(stats)               # Executes shell command for on_compaction

Execution Engine (_run_cmd)
├── Environment Injection: FLUX_HOOK_EVENT, FLUX_MODEL, FLUX_CWD, FLUX_TOOL_NAME, etc.
├── Windows Support: Wrap command using shlex.quote with `bash -c` / `cmd.exe /c`
├── Timeout Enforcement: Subprocess timeout with process tree cleanup (taskkill /F /T /PID)
└── Standard Streams: Captures stdout/stderr logging & exit codes
```

---

### 4. Safety & Approval Policy (`safety/policy.py`)
```text
ApprovalPolicy (Enum)
├── ON_REQUEST   # Prompts user confirmation before executing mutating tools (write_file, edit, shell)
├── AUTO         # Automatically executes safe operations, prompts for high-risk operations
└── YOLO         # Auto-approves all tool executions without interactive prompts
```

---

### 5. Tool Registry & Discovery (`tools/`)
```text
ToolRegistry
├── register(tool)                      # Register built-in or custom discovered tool
├── register_mcp_tool(tool)             # Register external MCP server tool
├── unregister(name)                    # Remove a tool
├── get(name)                           # Look up tool by name (builtin -> MCP fallback)
├── get_tools()                         # Get all tools (with allowed_tools filtering)
├── get_schemas()                       # Get OpenAI function schemas for all tools
└── invoke(name, params, cwd)           # Validate + execute tool with exception handling

ToolDiscoveryManager
├── discover_from_directory(path)       # Dynamically loads custom python tools from .flux-cli/tools/*.py
└── discover_all()                      # Scans CWD and system config directory
```

---

### 6. Event Lifecycle & Flow
```text
AgentEventType (Enum)
├── AGENT_START          -> Agent starting processing
├── TEXT_DELTA           -> Chunk of streamed response text
├── TEXT_COMPLETE        -> Full response turn complete
├── TOOL_CALL_START      -> Tool invocation beginning
├── TOOL_CALL_COMPLETE   -> Tool execution finished (with result)
├── AGENT_ERROR          -> Error occurred
└── AGENT_END            -> Agent turn finished

Event Data Container (AgentEvent)
├── type: AgentEventType
└── data: dict[str, Any]
```

---

### 7. Configuration Loading Pipeline (`config/loader.py`)
```text
load_config(cwd)
├── 1. Load System Config              (~/.config/flux-cli/config.toml or %APPDATA%\flux-cli\config.toml)
├── 2. Load Project Config             (.flux-cli/config.toml in CWD)
├── 3. Merge Configs                   (Project settings override System settings)
├── 4. Detect Developer Instructions   (.flux-cli/AGENT.md or local AGENT.md)
└── 5. Construct Pydantic Config       (Strict validation & default fallbacks)
```

---

### 8. Terminal UI Engine (`ui/tui.py`)
```text
TUI Engine
├── get_console()                      # UTF-8 stdout reconfiguration & VT100/ANSI rendering
├── render_gradient_ascii()            # Multi-stop horizontal color gradient generator for logo
├── AGENT_THEME                        # Unified Rich color palette (#e7aafb, #a191f8, #8bcefc, #7fe4eb)
├── print_welcome()                    # Styled welcome box with model, cwd, and accented slash commands
├── begin_streaming_markdown()         # Live streaming markdown display with styled Assistant dividers
├── tool_call_start()                  # Tool card with parameter grid & running status indicator
├── tool_call_complete()               # Results card with syntax highlighting, diffs & status icons
├── handle_confirmation()              # Interactive diff preview & user confirmation prompt
└── show_help()                        # Styled Rich Panel with interactive slash commands dashboard
```