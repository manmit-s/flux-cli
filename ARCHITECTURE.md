## 🛠️ Architecture

### LLMClient Class
```
LLMClient
├── get_client()              # Lazy initialization of AsyncOpenAI
├── chat_completion()         # Main entry point with retry logic & tool support
│   ├── Builds kwargs with model, messages, stream, max_tokens
│   ├── Builds tool schemas if tools provided (tool_choice="auto")
│   ├── Retry on RateLimitError (exponential backoff: 2^attempt)
│   ├── Retry on APIConnectionError (exponential backoff)
│   └── Fail immediately on APIError
├── _stream_response()        # Yields TEXT_DELTA, TOOL_CALL_START/DELTA/COMPLETE, MESSAGE_COMPLETE
├── _non_stream_response()    # Returns complete response with tool calls at once
├── _build_tools()            # Converts tool schemas to OpenAI function-calling format
└── close()                   # Async cleanup
```

### Agent Class
```
Agent
├── __init__(config)                     # Creates Session
├── run(message)                         # Main entry point (async generator)
│   ├── Yields AGENT_START
│   ├── Adds user message to ContextManager
│   ├── Calls _agentic_loops()
│   │   └── Yields each event from loop
│   └── Yields AGENT_END with final_response
├── _agentic_loops()                     # Multi-turn agentic loop
│   ├── For turn in range(max_turns):
│   │   ├── Check context compression (triggers at 80% context window)
│   │   ├── Get tool schemas from registry
│   │   ├── Send messages + tools to LLMClient
│   │   ├── Stream TEXT_DELTA events
│   │   ├── Collect ToolCall events
│   │   ├── Add assistant message with tool calls to context
│   │   ├── If no tool calls → finalize (update usage, prune tool output)
│   │   ├── For each tool call:
│   │   │   ├── Yields TOOL_CALL_START
│   │   │   ├── Invoke tool via registry
│   │   │   └── Yields TOOL_CALL_COMPLETE with result
│   │   └── Add tool results to context
│   └── If max turns reached → AGENT_ERROR
├── __aenter__/__aexit__                 # Async context manager
│   ├── __aenter__: Session.initialize() → MCP, discovery, context
│   └── __aexit__: Close client, shutdown MCP
```

### Session Class
```
Session
├── __init__(config)                     # Initialize LLMClient, ToolRegistry, MCPManager, ChatCompactor
├── initialize()                         # Full lifecycle setup
│   ├── MCPManager.initialize()          # Connect to MCP servers
│   ├── ToolDiscoveryManager.discover_all()  # Find custom tools
│   ├── MCPManager.register_tools()      # Register MCP tools
│   └── ContextManager(config, memory, tools)  # Build context with system prompt
├── increment_turn()                     # Track turn count
└── _load_memory()                       # Load persistent user memory
```

### Event Types & Flow
```
AgentEventType (Enum)
├── AGENT_START          → Agent starting processing
├── TEXT_DELTA           → Chunk of streamed text
├── TEXT_COMPLETE        → Full response complete
├── TOOL_CALL_START      → Tool invocation beginning
├── TOOL_CALL_COMPLETE   → Tool execution finished (with result)
├── AGENT_ERROR          → Error occurred
└── AGENT_END            → Agent finished

AgentEvent (Data Container)
├── type: AgentEventType
└── data: dict[str, Any]

Event Creation (Factory Methods)
├── agent_start(message)                → {type: AGENT_START, data: {message}}
├── text_delta(content)                 → {type: TEXT_DELTA, data: {content}}
├── text_complete(content)              → {type: TEXT_COMPLETE, data: {content}}
├── tool_call_start(id, name, args)     → {type: TOOL_CALL_START, data: {call_id, name, arguments}}
├── tool_call_complete(id, name, result)→ {type: TOOL_CALL_COMPLETE, data: {call_id, name, success, output, ...}}
├── agent_error(error)                  → {type: AGENT_ERROR, data: {error}}
└── agent_end(response, usage)          → {type: AGENT_END, data: {response, usage}}
```

### Response Events (from LLMClient)
```
StreamEvent
├── type: StreamEventType               (TEXT_DELTA | TOOL_CALL_START | TOOL_CALL_DELTA | TOOL_CALL_COMPLETE | MESSAGE_COMPLETE | ERROR)
├── text_delta: TextDelta               (chunk of content)
├── tool_call_delta: ToolCallDelta      (incremental tool call data)
├── tool_call: ToolCall                 (complete tool call)
├── finish_reason: str                  ("stop", "length", etc.)
├── usage: TokenUsage                   (token counts)
└── error: str                          (error message)
```

### Tool Base Class Hierarchy
```
Tools (ABC)
├── name: str                           # Unique tool identifier
├── description: str                    # Human-readable description
├── kind: ToolKind                      # READ | WRITE | SHELL | NETWORK | MEMORY | MCP
├── schema: Pydantic Model | dict       # Parameter validation schema
├── execute(invocation) → ToolResult    # Main execution method (abstract)
├── validate_params(params) → [errors]  # Pydantic parameter validation
├── is_mutating(params) → bool          # Check if tool modifies state
├── get_confirmation(invocation)        # Generate confirmation request
└── to_openai_schema() → dict           # Generate OpenAI function-calling schema

├── Builtin Tools
│   ├── ReadFileTool                    # File reading with line numbers
│   ├── WriteFileTool                   # File creation/overwrite
│   ├── EditTool                        # Surgical text replacement
│   ├── ShellTool                       # Command execution
│   ├── ListDirTool                     # Directory listing
│   ├── GrepTool                        # Regex search
│   ├── GlobTool                        # File pattern matching
│   ├── WebSearchTool                   # DuckDuckGo search
│   ├── WebFetchTool                    # HTTP fetch with proxy fallback
│   ├── ToDoTool                        # Task tracking
│   └── MemoryTool                      # Persistent user memory
│
├── SubAgentTool                        # Spawns child agent with isolated context
│   ├── codebase_investigator           # Code exploration (read-only)
│   └── code_reviewer                   # Code review (read-only)
│
└── MCPTool                             # Adapter for MCP server tools
```

### ToolRegistry
```
ToolRegistry
├── register(tool)                      # Register a built-in/discovered tool
├── register_mcp_tool(tool)             # Register an MCP tool (separate namespace)
├── unregister(name)                    # Remove a tool
├── get(name)                           # Look up tool by name (builtin → MCP fallback)
├── get_tools()                         # Get all tools (with allowed_tools filtering)
├── get_schemas()                       # Get OpenAI schemas for all tools
└── invoke(name, params, cwd)           # Validate + execute tool with error handling
```

### Configuration Loading
```
load_config(cwd)
├── 1. Load system config              (~/.config/flux-cli/config.toml)
├── 2. Load project config             (.flux-cli/config.toml in CWD)
├── 3. Merge (project overrides system)
├── 4. Detect AGENT.md files           (.flux-cli/AGENT.md for developer instructions)
└── 5. Construct Config                (Pydantic validation)
```

### Context Management Flow
```
ContextManager
├── System Prompt                       # Generated from identity, environment, tools, security, etc.
├── Messages List                       # [system] + [user, assistant, tool] × N
├── add_user_message(content)           # Track user input with token count
├── add_assistant_message(content, tc)  # Track assistant response + tool calls
├── add_tool_result(id, content)        # Track tool execution results
├── get_messages()                      # Serialize to OpenAI-compatible format
├── needs_compression()                 # Check if >80% of context window used
├── replace_with_summary(summary)       # Compact with continuation prompt
├── prune_tool_output()                 # Remove old tool results to save space
├── set_latest_usage(usage)             # Track current turn's token usage
└── add_usage(usage)                    # Accumulate total session token usage
```