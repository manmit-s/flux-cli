# Flux-CLI

> 🚧 **Work In Progress** — Actively being developed as a learning project. APIs and architecture may change.

An AI agent project built from scratch to understand how Claude Code CLI works, including multi-tool selection, reasoning, and iterative file editing capabilities.

## 🎯 Project Aim

This project is a **learning initiative** designed to understand and implement core concepts behind intelligent coding agents:

- **How AI agents reason** about problems and select appropriate tools
- **Multi-tool orchestration** — deciding which tools to use and in what order
- **Iterative refinement** — analyzing code, identifying issues, and autonomously refactoring
- **Streaming capabilities** — real-time response generation and token consumption
- **Error handling & resilience** — retry logic, exponential backoff, graceful degradation
- **Async patterns** — non-blocking operations for API calls and task orchestration

## 📋 Completed Features

### 1. **LLM Client (AsyncOpenAI Integration)**
- ✅ Async OpenAI client with lazy initialization
- ✅ Support for streaming and non-streaming responses
- ✅ Stream event architecture (`StreamEvent`, `TextDelta`, `TokenUsage`)
- ✅ Error handling with retry logic:
  - Rate limit handling with exponential backoff
  - Connection error recovery
  - API error catching and reporting
- ✅ Configurable API key via `.env` file
- ✅ Support for different LLM providers (OpenRouter base URL)

### 2. **Response Event System**
- ✅ Event-based architecture for streaming responses
- ✅ Event types: `TEXT_DELTA`, `MESSAGE_COMPLETE`, `ERROR`, `TOKEN_RECEIVED`
- ✅ Type-safe response events with usage tracking
- ✅ Consistent interface for both streaming and non-streaming modes

### 3. **Async Generator Pattern**
- ✅ Unified caller interface using `async for`
- ✅ Generator-based streaming with `yield`
- ✅ Single entry point for different response modes

### 4. **Agent Core & Event System** (May 24)
- ✅ `Agent` orchestrator with async context manager support
- ✅ Event-driven architecture with `AgentEvent` and `AgentEventType`
- ✅ Event lifecycle: `AGENT_START` → `TEXT_DELTA` × N → `TEXT_COMPLETE` → `AGENT_END`
- ✅ Error propagation through event system (`AGENT_ERROR`)
- ✅ Agentic loop that processes LLM responses and yields events
- ✅ Message context storage for multi-turn conversations (foundation)

### 5. **CLI & Terminal UI** (May 24)
- ✅ Click-based CLI with command-line argument parsing
- ✅ Rich terminal output with custom theme styling
- ✅ Real-time streaming text display with `stream_assistant_delta()`
- ✅ Assistant response formatting with rule separators
- ✅ Error handling and display with `style="error"`
- ✅ Async context manager integration for clean resource management

## 🚀 In Progress / Future Features

### Phase 2: Advanced Agent Features *(Next)*
- [ ] Multi-turn conversation context (remember previous messages)
- [ ] Tool registry system (define available tools)
- [ ] Tool selection logic (LLM decides which tool to use)
- [ ] Function calling from LLM responses
- [ ] Multi-step task orchestration

### Phase 3: Code Manipulation
- [ ] File reading and analysis
- [ ] AST parsing for understanding code structure
- [ ] Automated refactoring suggestions
- [ ] Multi-file editing capabilities
- [ ] Dependency analysis

### Phase 4: Reasoning & Iteration
- [ ] Multi-turn reasoning loops
- [ ] Self-correction based on execution results
- [ ] Plan generation and execution
- [ ] Context management for complex tasks

## 📁 Project Structure

```
flux/
├── main.py                  # CLI entry point with Click integration
├── client/
│   ├── llm_client.py       # AsyncOpenAI wrapper with streaming, retry logic
│   └── response.py         # StreamEvent, TextDelta, TokenUsage types
├── agent/
│   ├── agent.py            # Agent orchestrator with agentic loops
│   └── events.py           # AgentEvent, AgentEventType definitions
├── ui/
│   └── tui.py              # Terminal UI with Rich library (themes, formatting)
├── .env                    # API keys and configuration (git-ignored)
├── .gitignore
└── README.md
```

## 🛠️ Current Architecture

### LLMClient Class
```
LLMClient
├── get_client()           # Lazy initialization of AsyncOpenAI
├── chat_completion()      # Main entry point with retry logic
│   ├── Retry on RateLimitError (exponential backoff)
│   ├── Retry on APIConnectionError (exponential backoff)
│   └── Fail immediately on APIError
├── _stream_response()     # Yields TEXT_DELTA events in real-time
├── _non_stream_response() # Returns complete response at once
└── close()                # Async cleanup
```

### Agent Class
```
Agent
├── __init__()             # Initializes LLMClient
├── run(message)           # Main entry point (async generator)
│   ├── Yields AGENT_START
│   ├── Calls _agentic_loops()
│   ├── Yields each event from loop
│   └── Yields AGENT_END with final_response
├── _agentic_loops()       # Processes LLM response stream
│   ├── Sends message to LLMClient
│   ├── Yields TEXT_DELTA for each chunk
│   ├── Handles ERROR events
│   └── Yields TEXT_COMPLETE when done
├── __aenter__/__aexit__   # Async context manager for cleanup
└── current_message        # Stores user input for agentic loop
```

### Event Types & Flow
```
AgentEventType (Enum)
├── AGENT_START      → Agent starting processing
├── TEXT_DELTA       → Chunk of streamed text
├── TEXT_COMPLETE    → Full response complete
├── AGENT_ERROR      → Error occurred
└── AGENT_END        → Agent finished

AgentEvent (Data Container)
├── type: AgentEventType
└── data: dict[str, Any]

Event Creation (Factory Methods)
├── agent_start(message)          → {type: AGENT_START, data: {message}}
├── text_delta(content)           → {type: TEXT_DELTA, data: {content}}
├── text_complete(content)        → {type: TEXT_COMPLETE, data: {content}}
├── agent_error(error)            → {type: AGENT_ERROR, data: {error}}
└── agent_end(response, usage)    → {type: AGENT_END, data: {response, usage}}
```

### Response Events (from LLMClient)
```
StreamEvent
├── type: StreamEventType
├── text_delta: TextDelta (chunk of content)
├── finish_reason: str ("stop", "length", etc.)
├── usage: TokenUsage (token counts)
└── error: str (error message)
```

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
pip install openai python-dotenv
```

### Configuration
Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_api_key_here
```

### Running
```bash
# Basic usage
python main.py "Hello, how are you?"

# Works with streaming and real-time display
python main.py "Write a 250 character line about Python"
```

## 📝 Recent Updates (May 24, 2026)

### Agent Orchestration System
- Built the `Agent` class that orchestrates conversations
- Implemented event-driven communication through `AgentEvent` system
- Created agentic loops that process LLM responses
- Integrated async context managers for resource cleanup

### Terminal UI
- Added Rich library integration for styled terminal output
- Built custom theme with assistant/user/error/success colors
- Real-time text streaming display
- Proper error handling and display

### Debugging & Fixes
- Fixed import issues (Rich Text from correct module)
- Resolved unbound variable errors with proper initialization
- Implemented proper markup-safe error printing
- Added exponential backoff for API retries

## 📚 Learning Resources Referenced

- **Async patterns**: Python `asyncio`, async generators with `yield`
- **Type hints**: Union types, `AsyncGenerator[T, None]`
- **Error handling**: Retry logic with exponential backoff
- **Streaming**: Async iteration over streamed responses
- **Design patterns**: Lazy initialization, event-driven architecture

## 🔍 Key Concepts Explored

### 1. Async Generators
Why use `yield` in async functions? Creates a consistent interface where callers always use `async for`, regardless of streaming mode.

### 2. Error Resilience
Implemented retry logic with exponential backoff for:
- Rate limiting (429 errors)
- Connection issues
- API errors

### 3. Type Safety
Using Python type hints throughout to catch issues early:
- `AsyncGenerator[StreamEvent, None]`
- `AsyncOpenAI | None`
- Union types for flexible responses

### 4. Lazy Initialization
API client is only created when first needed, reducing startup overhead.

## 📝 Next Steps

1. **Tool System**: Design and implement a registry of available tools
2. **Reasoning Loop**: Create logic for agent to reason about which tools to use
3. **Code Analysis**: Implement AST-based code parsing and analysis
4. **Multi-turn Conversation**: Support context across multiple messages
5. **File Operations**: Safe read/write operations with diff generation

## 👨‍🏫 Credits & Learning Resources

**Inspired by and learning from:**
- **[Rivaan Ranawat](https://github.com/RivaanRanawat)** — Tutor and educational content creator

## 🤝 Contributing

This is a personal learning project, but feel free to fork and experiment!

## 📄 License

MIT

---

**Note**: This project is actively being developed as a learning exercise. Expect API changes and refactoring as new features are added.
