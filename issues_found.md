# Flux-CLI Audit: Issues Found

> **Audit Date:** 2025-07-16  
> **Scope:** All source files in `c:/NEW/PROGRAMMING/PROJECTS/flux-cli-ai-agent/` and its `flux_cli/` installable package duplicate.

---

## 1. CRITICAL: `todos` Tool Schema Bug (Required Field Prevents `add` Action)

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/todo.py:12`, `flux_cli/tools/builtin/todo.py:12` |
| **Issue** | `id: str \| None = Field(...)` — `id` is declared **required** (no default) even though it's only needed for the `complete` action. The JSON schema marks `id` as required, so the LLM is forced to pass `id` for every action including `add`. |
| **Breakage** | The `todos` tool **always fails** when the LLM tries to add a todo because the model sends `id: 1` (as an integer), and Pydantic v2 won't coerce `int → str`. |
| **Error** | `Parameter 'id' : Input should be a valid string` |
| **Fix** | Make `id` optional: `Field(None, ...)`. Add a `field_validator('id', mode='before')` to coerce numeric ids to strings. |

---

## 2. CRITICAL: `memory` Tool Schema Bug (Same Pattern as `todos`)

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/memory.py:8`, `flux_cli/tools/builtin/memory.py:8` |
| **Issue** | `key: str \| None = Field(...)` — `key` is required in the schema even though it's only needed for `set`, `get`, `delete`. The `list` and `clear` actions will fail if the LLM is forced to send a `key`. |
| **Breakage** | `memory list` and `memory clear` will fail with `Input should be a valid string` if the LLM sends `key: 1` (integer) or doesn't send a key at all. |
| **Fix** | Same as `todos` — make `key` optional with `Field(None)`. |

---

## 3. CRITICAL: Duplicate `flux_cli/` Package (Root Fixes Don't Apply)

| Property | Detail |
|---|---|
| **Files** | `flux_cli/` (entire directory) |
| **Issue** | The project has a **complete duplicate** of the codebase inside `flux_cli/`. The `pyproject.toml:34` entry point is `flux = "flux_cli.main:main"` and `pyproject.toml:38` includes `flux_cli*`. The `flux_cli/` directory has NO `__init__.py` at the package root, but has `config/__init__.py` and `tools/builtin/__init__.py`. |
| **Breakage** | Any fixes made to the root `tools/builtin/todo.py` (issues #1, #2) **won't take effect** when the user runs `flux` because the installed package runs from `flux_cli/`. The fixes must be applied to **both copies** and the package must be reinstalled. |
| **Fix** | Either symlink the root `flux_cli/` to be a proper package with `__init__.py`, or better — remove the duplicate and make the root the package. |

---

## 4. BUG: `__all__` Missing Commas in `tools/builtin/__init__.py`

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/__init__.py:21-24`, `flux_cli/tools/builtin/__init__.py:21-24` |
| **Issue** | Python's implicit string concatenation is causing `__all__` to have incorrect entries: |
| | `"WebSearchTool"` + `"WebFetchTool"` → `"WebSearchToolWebFetchTool"` |
| | `"WebFetchTool"` + `"ToDoTool"` → `"WebFetchToolToDoTool"` |
| | `"ToDoTool"` + `"MemoryTool"` → `"ToDoToolMemoryTool"` |
| **Breakage** | `get_all_builtin_tools()` may return wrong tools or fail to import if the concatenated names don't match actual classes. This is a silent import-time bug. |
| **Fix** | Add missing commas: `"WebSearchTool",` etc. |

---

## 5. BUG: `temperature` Setter Uses Wrong Decorator

| Property | Detail |
|---|---|
| **Files** | `config/config.py:129-131`, `flux_cli/config/config.py:129-131` |
| **Issue** | The `temperature` setter is decorated with `@model_name.setter` instead of `@temperature.setter`: |
| | ```python
| | @model_name.setter  # BUG: should be @temperature.setter
| | def temperature(self, value: str) -> None:
| |     self.model.temperature = value
| | ``` |
| **Breakage** | `config.temperature = 0.8` silently does nothing (creates a new attribute `temperature` on the instance instead of calling the setter). The `/model` command and any runtime temperature changes are ineffective. |
| **Fix** | Change to `@temperature.setter`. |

---

## 6. BUG: `is_mutating` Has Duplicate `ToolKind.SHELL` in Set

| Property | Detail |
|---|---|
| **Files** | `tools/base.py:152` |
| **Issue** | `return self.kind in {ToolKind.WRITE, ToolKind.SHELL, ToolKind.SHELL, ToolKind.MEMORY}` — `ToolKind.SHELL` appears twice. This is a minor code smell, but the real issue is that `ToolKind.MCP` is **missing** from the set, so MCP tools are never considered mutating and will never trigger approval. |
| **Breakage** | MCP tools that modify state will bypass approval checks entirely. |
| **Fix** | Add `ToolKind.MCP` to the set. |

---

## 7. BUG: Hardcoded `max_tokens=4000` in LLM Client

| Property | Detail |
|---|---|
| **Files** | `client/llm_client.py:67` |
| **Issue** | `"max_tokens": 4000` is hardcoded regardless of the model's actual context window. For models with smaller context windows, this may cause truncation. For models with larger context, this wastes potential. |
| **Breakage** | The model may stop generating mid-response for complex tasks. The user cannot configure this. |
| **Fix** | Derive from `config.model.context_window` or make it configurable. |

---

## 8. BUG: `command` Comparisons in `main.py` Use Raw Variable (Case-Sensitivity)

| Property | Detail |
|---|---|
| **Files** | `main.py:159,161,165`, `flux_cli/main.py:159,161,165` |
| **Issue** | `/help`, `/clear`, `/config` are compared using `command == "/help"` (the raw user input, not `cmd` which is `.lower().strip()`). Other commands like `/Model`, `/CLEAR` won't work for these specific commands, while `/model` and `/clear` do work. |
| **Breakage** | Inconsistent behavior — some commands are case-insensitive, others are case-sensitive. User confusion. |
| **Fix** | Change to `cmd == "/help"` etc. |

---

## 9. BUG: `/restore` Command References Undefined Variable `checkpoint_id`

| Property | Detail |
|---|---|
| **Files** | `main.py:330`, `flux_cli/main.py:330` |
| **Issue** | The `/restore` handler prints: `f"[success]Resumed session: {session.session_id}, checkpoint: {checkpoint_id}[/success]"` — but `checkpoint_id` is the **argument** to `/restore`, not a variable. This references `checkpoint_id` from the `/checkpoint` handler's scope, which won't exist or will be stale. |
| **Breakage** | Will raise `NameError` or print the wrong value at runtime. |
| **Fix** | Use `cmd_args` instead of `checkpoint_id`. |

---

## 10. BUG: `_get_agent_md_files` Checks Wrong Directory

| Property | Detail |
|---|---|
| **Files** | `config/loader.py:50-60` |
| **Issue** | The function checks `agent_dir = current / '.flux-cli'` but then looks for `AGENT.md` in `current / AGENT_MD_FILE` (= `current / 'AGENT.md'`), not inside `.flux-cli/`. The `agent_dir` variable is never used. |
| **Breakage** | `AGENT.md` files are never discovered. The `developer_instructions` config field is never populated from the project. |
| **Fix** | Either look for `AGENT.md` inside `.flux-cli/` or check the project root correctly. |

---

## 11. BUG: `_load_memory` Returns Wrong Type in `session.py`

| Property | Detail |
|---|---|
| **Files** | `agent/session.py:49` |
| **Issue** | When the memory file doesn't exist, `_load_memory` returns `{'entries': {}}` (a dict) instead of `None` (a string or None). The return type annotation says `str \| None`. The caller `ContextManager.__init__` expects `str \| None` and passes it to the system prompt builder. |
| **Breakage** | The system prompt will receive a dict instead of a formatted string, potentially causing `str` method errors or printing `{'entries': {}}` in the prompt. |
| **Fix** | Return `None` instead of `{'entries': {}}`. |

---

## 12. BUG: `read_file` Error Message Missing Space

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/read_file.py:64-65` |
| **Issue** | `f"File too large ({file_size / (1024*1024):.1f})MB" f"Maximum is ({self.MAX_FILE_SIZE/(1024*1024):.1f})MB"` — Python implicit string concatenation produces `"...MBMaximum is..."` with no space between `MB` and `Maximum`. |
| **Breakage** | User sees confusing error message like `File too large (15.2MBMaximum is (10.0)MB)`. |
| **Fix** | Add a space at the end of the first string or use `\n`. |

---

## 13. BUG: `grep` Tool `_find_files` Ignores Hidden Files but Not Directories

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/grep.py:107-108` |
| **Issue** | `dirs[:] = [d for d in dirs if d not in {...}]` and `if filename.startswith('.'): continue` — the code skips hidden files but does NOT skip hidden directories (like `.git`). The filter list `{'node_modules', '__pycache__', '.venv', '.git', 'venv'}` is a **partial** list of common dirs to exclude, but `.git` is actually in it. However, hidden directories that aren't in the list (like `.hg`, `.svn`, `.idea`, `.vscode`) will be entered. |
| **Breakage** | `grep` may search into hidden directories, causing noise or performance issues. The `glob` tool has the same pattern. |
| **Fix** | Also skip directories starting with `.`. |

---

## 14. BUG: `todos._display_todos` Prints to Console AND Returns String

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/todo.py:44-45` |
| **Issue** | `_display_todos()` calls `console.print(table)` AND returns `str(table)`. The Rich table is printed directly to the console (side effect) and also returned as a string for the tool output. This causes the table to appear twice in the user's terminal. |
| **Breakage** | Users see duplicate todo list displays. |
| **Fix** | Remove the `console.print(table)` line, only return the string. |

---

## 15. BUG: Unused Import `ToDoTool` in `ui/tui.py`

| Property | Detail |
|---|---|
| **Files** | `ui/tui.py:22` |
| **Issue** | `from tools.builtin.todo import ToDoTool` is imported but never used anywhere in the file. |
| **Breakage** | None directly, but it adds unnecessary import overhead and may trigger circular import issues if the dependency chain changes. |
| **Fix** | Remove the unused import. |

---

## 16. BUG: MCP Client `disconnect()` Accesses Private Attributes

| Property | Detail |
|---|---|
| **Files** | `tools/mcp/client.py:82-88` |
| **Issue** | The disconnect method accesses `transport._process`, `proc._transport`, `proc._transport._closed`, `proc._transport._stdin._closed`, etc. These are all private/underscored attributes of the `fastmcp` library. The library may change these internals without notice in any version update. |
| **Breakage** | On `fastmcp` library update, the disconnect method may fail silently (wrapped in `except Exception: pass`), leaving stale subprocesses. |
| **Fix** | Use the library's public API only. The `with` context manager should handle cleanup. |

---

## 17. BUG: `tui.py` Imports `ToDoTool` But Never Uses It

| Property | Detail |
|---|---|
| **Files** | `ui/tui.py:22` |
| **Issue** | `from tools.builtin.todo import ToDoTool` is imported but never referenced. |
| **Breakage** | None directly, but wastes import time and can cause circular import issues. |
| **Fix** | Remove the unused import. |

---

## 18. BUG: `_find_files` in `glob` and `grep` Ignores Hidden Files but Not `.git` Contents

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/glob.py:78-79`, `tools/builtin/grep.py:107-108` |
| **Issue** | Same issue as #13 but in `glob` too. The `_find_files` method in both tools has the same logic. |
| **Breakage** | Both tools may traverse into hidden directories. |
| **Fix** | Skip all directories starting with `.`. |

---

## 19. BUG: `web_fetch` Proxy URL Construction is Brittle

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/web_fetch.py:31-36` |
| **Issue** | `_proxy_url` constructs `https://r.jina.ai/http://{target}` where `target = parsed.netloc + parsed.path`. This re-adds `http://` prefix even for `https://` URLs, and query parameters are prepended differently. The fallback proxy may fail for many URLs. |
| **Breakage** | When direct fetch fails (403/429/5xx), the proxy fallback may also fail due to malformed URL, making the tool unusable for many sites. |
| **Fix** | Use `urljoin` or a proper URL rewriting approach. |

---

## 20. BUG: `approval.py` `check_approval` Returns Inconsistent Decision

| Property | Detail |
|---|---|
| **Files** | `safety/approval.py:126-129` |
| **Issue** | The loop iterates over `context.affected_paths` and returns `path_decision` (which is `NEEDS_CONFIRMATION`) for the first path that is outside the cwd. But if there are multiple paths, only the first one is checked. Additionally, `path_decision` is always `NEEDS_CONFIRMATION` — the `APPROVED` branch sets `path_decision = APPROVED` but then never returns it, falling through to the final `return APPROVED`. |
| **Breakage** | Path-based approval decisions are not properly evaluated. All paths outside the cwd get `NEEDS_CONFIRMATION` regardless of the actual policy. |
| **Fix** | Properly evaluate each path and return the strictest decision. |

---

## 21. BUG: `approval.py` `request_confirmation` Defaults to `True` When No Callback

| Property | Detail |
|---|---|
| **Files** | `safety/approval.py:141-145` |
| **Issue** | `if self.confirmation_callback:` — if no callback is set (which is the case for `Agent.run_single`), `request_confirmation` returns `True`, meaning **all operations are auto-approved** in single-shot mode, regardless of the approval policy. |
| **Breakage** | When running `flux "some prompt"` (single mode), the approval system is completely bypassed. Dangerous commands can be executed without user confirmation. |
| **Fix** | Default to `False` (reject) when no callback is provided, or prompt via stdin. |

---

## 22. BUG: `subagent.py` Creates New `Config` from `to_dict()` Which May Lose Fields

| Property | Detail |
|---|---|
| **Files** | `tools/subagent.py:51-56` |
| **Issue** | `config_dict = self.config.to_dict()` then `Config(**config_dict)`. The `to_dict()` method uses `model_dump(mode="json")`, which serializes to JSON-compatible types. Complex fields like `Path` objects become strings, and the `Config` model's `cwd` field expects a `Path`. This may cause validation errors. |
| **Breakage** | Creating a sub-agent may fail with Pydantic validation errors if the config has non-serializable types. |
| **Fix** | Use `model_copy(update={...})` or proper deserialization. |

---

## 23. BUG: `hook_system.py` Ignores Hook Return Codes (No Failure Propagation)

| Property | Detail |
|---|---|
| **Files** | `hooks/hook_system.py:38-48` |
| **Issue** | All hook executions are wrapped in `except Exception: pass` (in `_run_hook`). If a hook command fails, it's only logged at warning level. The agent continues regardless. |
| **Breakage** | Users cannot create "enforcement" hooks (e.g., pre-commit checks that must pass). Hook failures are silent. |
| **Fix** | Optionally propagate hook failures or make them configurable. |

---

## 24. BUG: `shell.py` Orphan Process Risk on Timeout

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/shell.py:119-121` |
| **Issue** | On timeout, `process.kill()` is called on Windows, but the `stdout_task` and `stderr_task` are cancelled. However, the stream readers may have already buffered data that is lost. On non-Windows, `os.killpg(os.getpgid(process.pid), signal.SIGKILL)` is used, but the process group ID may not be set correctly with `start_new_session=True` on all platforms. |
| **Breakage** | Subprocesses may become orphaned, especially on Windows. |
| **Fix** | Use `taskkill /F /T /PID` on Windows consistently (as done in `hook_system.py`). |

---

## 25. BUG: `persistence.py` `os.chmod` on Windows Has No Effect

| Property | Detail |
|---|---|
| **Files** | `agent/persistence.py:50-51,63` |
| **Issue** | `os.chmod` with Unix permission bits (0o700, 0o600) on Windows does not actually restrict access. Windows uses ACLs, not POSIX permissions. |
| **Breakage** | Session files and checkpoints containing potentially sensitive data (conversations, code) are not actually protected on Windows. |
| **Fix** | Use Windows-specific ACLs or document that this only works on Unix. |

---

## 26. BUG: `config/setup.py` Writes API Key to Plain TOML File

| Property | Detail |
|---|---|
| **Files** | `config/setup.py:56-66` |
| **Issue** | The config wizard writes the API key in plaintext to `config.toml`: `api_key = "{api_key}"`. The file has no restrictive permissions set. |
| **Breakage** | API keys are stored insecurely on disk. Any process on the same machine can read the key. |
| **Fix** | Set file permissions to 0o600 (owner-only), or use the system keychain. |

---

## 27. BUG: `get_tokenizer` Has Dead Code Path

| Property | Detail |
|---|---|
| **Files** | `utils/text.py:3-8` |
| **Issue** | `def get_tokenizer(model: str):` — if `tiktoken.encoding_for_model(model)` succeeds, the function returns `None` implicitly (no return statement). If it raises `Exception`, the `except` block returns `encoding.encode` (a bound method). This means the function **always returns `None`** for known models, and only returns a tokenizer for unknown models. |
| **Breakage** | `count_tokens` always falls back to `estimate_tokens` (character count / 4), which is inaccurate. Token counting for compression and truncation is wrong. |
| **Fix** | Return `encoding.encode` for the success case too. |

---

## 28. BUG: `ToolCall.arguments` Type is `str` But Should Be `dict`

| Property | Detail |
|---|---|
| **Files** | `client/response.py:50` |
| **Issue** | `class ToolCall: arguments: str = ""` — the type annotation says `str`, but the field is assigned `parse_tool_call_arguments(tc['arguments'])` which returns `dict[str, Any]`. The dataclass field type is misleading and the downstream code in `agent.py` does `json.dumps(tc.arguments)` which would double-encode if it's already a dict. |
| **Breakage** | Tool call arguments to the LLM may be double-encoded (`{"key": "value"}` → `"{\"key\": \"value\"}"`), causing the LLM to receive malformed JSON. |
| **Fix** | Change type to `dict[str, Any]` or keep as `str` and don't parse it. |

---

## 29. BUG: `agent.py` Loop Detection `response_text` Check Logic

| Property | Detail |
|---|---|
| **Files** | `agent/agent.py:104` |
| **Issue** | `if response_text:` — this only checks the text from the current turn. If the LLM responds with only tool calls (no text), `response_text` is empty, and `yield AgentEvent.text_complete(response_text)` is skipped. Then `if not tool_calls:` at line 112 checks if there are no tool calls, and if there are, it loops. But `text_complete` is never yielded for tool-only responses. |
| **Breakage** | The TUI may not display the assistant's text completion for tool-only responses. The `TEXT_COMPLETE` event is never emitted, so the UI stays in a blank state. |
| **Fix** | Always yield `text_complete` even if response_text is empty. |

---

## 30. BUG: `compaction.py` Hardcoded Truncation Limits

| Property | Detail |
|---|---|
| **Files** | `context/compaction.py:39-71` |
| **Issue** | Hardcoded truncation limits: `content[:2000]` for tool results, `content[:3000]` for assistant responses, `content[:1500]` for user messages, `args[:500]` for tool call arguments. These are arbitrary and not configurable. |
| **Breakage** | Important context may be lost during compaction, causing the agent to lose track of the task. |
| **Fix** | Make limits configurable or relative to the model's context window. |

---

## 31. BUG: `prune_tool_outputs` Logic Error — `pruned_tokens` Counts Messages, Not Tokens

| Property | Detail |
|---|---|
| **Files** | `context/manager.py:167-188` |
| **Issue** | `pruned_tokens` is incremented by `1` for each message added to the prune list (line 185: `pruned_tokens += 1`), but it's compared against `PRUNE_MINIMUM_TOKENS = 20_000` (line 187). This means at least 20,000 tool messages must be collected before pruning happens, which will never happen in practice. |
| **Breakage** | Tool output pruning is effectively **never triggered** (unless there are 20,000+ tool messages). Context keeps growing unbounded, causing eventual OOM or context overflow. |
| **Fix** | Rename to `pruned_count` and compare against a reasonable minimum count (e.g., 5). |

---

## 32. BUG: `prune_tool_outputs` Iterates in Reverse But Breaks on First Pruned Message

| Property | Detail |
|---|---|
| **Files** | `context/manager.py:175-178` |
| **Issue** | The loop iterates `for msg in reversed(self._messages)` and `if msg.pruned_at: break`. This means once it finds a message that was already pruned, it stops looking at older messages. But because it's iterating in reverse (newest first), this only prevents pruning the newest messages. The logic is confusing and may lead to unexpected behavior. |
| **Breakage** | Older tool outputs may not be pruned if any newer one was already pruned. |
| **Fix** | Clarify the intent and simplify the logic. |

---

## 33. BUG: `MCPManager.initialize()` Returns Early Without Error When No MCP Servers

| Property | Detail |
|---|---|
| **Files** | `tools/mcp/mcp_manager.py:26-27` |
| **Issue** | `if not mcp_configs: return` — if no MCP servers are configured, this is fine. But the method also doesn't set `self._initialized = True` in this case, so it will be called again on every `initialize()` call. The `if self._initialized: return` check at line 17 prevents re-initialization, but not in this case. |
| **Breakage** | None immediately, but repeated calls to `initialize()` (if `_initialized` is False) will recreate connection tasks unnecessarily. |
| **Fix** | Set `self._initialized = True` in the early return too. |

---

## 34. BUG: `config/__init__.py` Is Empty — Missing Module Exports

| Property | Detail |
|---|---|
| **Files** | `config/__init__.py` (and `flux_cli/config/__init__.py`) |
| **Issue** | Both `config/__init__.py` files are empty. They should export the public API (e.g., `Config`, `ApprovalPolicy`, `ModelConfig`, etc.). |
| **Breakage** | `from config import Config` works because Python's import system still finds the module, but the intent of the package (`__init__.py`) is not clear. Not a runtime bug, but a code organization issue. |
| **Fix** | Add proper exports. |

---

## 35. BUG: `main.py` Dead Code — `async def run(messages: dict[str, Any]): pass`

| Property | Detail |
|---|---|
| **Files** | `main.py:337-338`, `flux_cli/main.py:337-338` |
| **Issue** | There's a dangling async function `run(messages)` that does nothing (`pass`). It's never called anywhere. |
| **Breakage** | None, but it's dead code that could confuse developers. |
| **Fix** | Remove it. |

---

## 36. BUG: `memory.py` Action Comparisons Not `.lower()` for `list` and `clear`

| Property | Detail |
|---|---|
| **Files** | `tools/builtin/memory.py:81,90`, `flux_cli/tools/builtin/memory.py:81,90` |
| **Issue** | `elif params.action == 'list':` and `elif params.action == 'clear':` use exact match, while `set`, `get`, `delete` use `params.action.lower()`. If the LLM sends `LIST` or `Clear`, those actions will fall through to the `else: Unknown Action` error. |
| **Breakage** | Inconsistent case handling — same tool, different behavior depending on the action. |
| **Fix** | Use `.lower()` for all action comparisons. |

---

## 37. BUG: `LLMClient.get_client()` Reads `API_KEY` from Env on Every Call

| Property | Detail |
|---|---|
| **Files** | `client/llm_client.py:20` |
| **Issue** | `api_key = self.config.api_key or os.getenv("API_KEY")` — if `config.api_key` is `None` (because the environment variable isn't set yet), it falls back to `os.getenv("API_KEY")` at call time. The `load_config` function sets `os.environ["API_KEY"]` from the config file, but this is a side effect that may not have happened yet if the `LLMClient` is created before `load_config` finishes. |
| **Breakage** | Rare race condition where the API key is not found. |
| **Fix** | Pass the resolved key explicitly. |

---

## 38. BUG: `tool_call_complete` in `events.py` Calls `result.diff.to_diff()` Without Null Check

| Property | Detail |
|---|---|
| **Files** | `agent/events.py:85` |
| **Issue** | `'diff' : result.diff.to_diff() if result.diff else None` — this is correct, but the surrounding code in `main.py` that calls `tool_call_complete` may pass `event.data.get('diff')` which could be `None`, and the TUI code checks for `if diff:` before using it. However, if `result.diff` is a `FileDiff` object, `to_diff()` could raise an error if the dataclass fields are not properly initialized. |
| **Breakage** | If `FileDiff` has invalid content, the tool call display will crash. |
| **Fix** | Add try/except in `to_diff()`. |

---

## Summary

| Severity | Count | Key Issues |
|---|---|---|
| **CRITICAL** | 3 | #1 (todos blocked), #2 (memory blocked), #3 (duplicate package prevents fixes from taking effect) |
| **BUG** | 28 | #4-#38: broken __all__, wrong setter decorator, missing approval for MCP, hardcoded limits, string comparison bugs, wrong variable references, dead code, logic errors, etc. |
| **SECURITY** | 3 | #21 (auto-approve on single mode), #25 (chmod ineffective on Windows), #26 (API key in plaintext) |
| **PERFORMANCE** | 2 | #13/#18 (hidden directory traversal), #31 (pruning never triggers) |
| **MAINTENANCE** | 2 | #34 (empty __init__.py), #35 (dead code) |
