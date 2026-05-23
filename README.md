# Flux-CLI

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

## 🚀 In Progress / Future Features

### Phase 2: Agent Core
- [ ] Tool registry system (define available tools)
- [ ] Tool selection logic (reasoning about which tool to use)
- [ ] Function calling from LLM responses
- [ ] Multi-step orchestration

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
├── main.py                  # Entry point
├── client/
│   ├── llm_client.py       # AsyncOpenAI wrapper with streaming support
│   └── response.py         # Response event types and structures
├── agent/
│   └── agent.py            # (Coming soon) Core agent orchestration
├── tools/                  # (Coming soon) Tool registry and execution
├── .env                    # API keys and configuration (not committed)
└── README.md
```

## 🛠️ Current Architecture

### LLMClient Class
```
LLMClient
├── get_client()           # Lazy initialization of AsyncOpenAI
├── chat_completion()      # Main entry point (streaming/non-streaming)
├── _stream_response()     # Yields tokens in real-time
├── _non_stream_response() # Yields complete response
└── close()                # Cleanup
```

### Response Events
```
StreamEvent
├── type: EventType (TEXT_DELTA, MESSAGE_COMPLETE, ERROR, etc.)
├── text_delta: TextDelta (contains content chunks)
├── finish_reason: str (stop, length, etc.)
├── usage: TokenUsage (prompt/completion/cache tokens)
└── error: str (for error events)
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
python main.py
```

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

## 🤝 Contributing

This is a personal learning project, but feel free to fork and experiment!

## 📄 License

MIT

---

**Note**: This project is actively being developed as a learning exercise. Expect API changes and refactoring as new features are added.
