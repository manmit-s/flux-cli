from pathlib import Path
import sys
import textwrap
from typing import Any, Tuple

from rich.console import Console, Group, Theme
from rich.rule import Rule
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.live import Live

from config.config import Config
from tools.base import ToolConfirmation
from utils.paths import display_path_rel_to_cwd

import re
from tools.builtin.todo import ToDoTool
from utils.text import truncate_text

AGENT_THEME = Theme(
    {
        # General (pastel cool)
        "info": "deep_sky_blue1",
        "warning": "light_pink1",
        "error": "magenta3 bold",
        "success": "medium_turquoise",
        "dim": "grey50",
        "muted": "grey50",
        "border": "grey35",
        "highlight": "bold cyan1",

        # Roles
        # Use violet for user, soft white for assistant
        "user": "slate_blue1 bold",       # maps to ~#a191f8
        "assistant": "white",             # keep high contrast

        # Tools – grouped in the palette
        "tool": "orchid1 bold",           # ~lavender pink #e7aafb
        "tool.read": "deep_sky_blue1",    # ~#8bcefc
        "tool.write": "light_pink1",      # ~#e7aafb
        "tool.shell": "medium_purple",    # ~#a191f8
        "tool.network": "cyan1",          # ~#7fe4eb
        "tool.memory": "medium_turquoise",
        "tool.mcp": "cyan1 bold",

        # Code / blocks
        "code": "white",
    }
)

_console: Console | None = None

def get_console() -> Console:
    global _console
    if _console is None:
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        _console = Console(theme=AGENT_THEME, highlight=False, legacy_windows=False)
    return _console

FLUX_GRADIENT_COLORS = ["#e7aafb", "#a191f8", "#8bcefc", "#7fe4eb"]

FLUX_ASCII_ART = """
██╗    ███████╗██╗     ██╗   ██╗██╗  ██╗
╚██╗   ██╔════╝██║     ██║   ██║╚██╗██╔╝
 ╚██╗  █████╗  ██║     ██║   ██║ ╚███╔╝ 
 ██╔╝  ██╔══╝  ██║     ██║   ██║ ██╔██╗ 
██╔╝   ██║     ███████╗╚██████╔╝██╔╝ ██╗
╚═╝    ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝
"""


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _interpolate_color(colors: list[str], factor: float) -> str:
    if factor <= 0.0:
        return colors[0]
    if factor >= 1.0:
        return colors[-1]

    num_segments = len(colors) - 1
    segment = factor * num_segments
    idx = int(segment)
    if idx >= num_segments:
        return colors[-1]

    t = segment - idx
    r1, g1, b1 = _hex_to_rgb(colors[idx])
    r2, g2, b2 = _hex_to_rgb(colors[idx + 1])

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return _rgb_to_hex(r, g, b)


def render_gradient_ascii(ascii_art: str, colors: list[str]) -> Text:
    lines = [l for l in ascii_art.splitlines() if l.strip()]
    if not lines:
        return Text("")

    max_len = max(len(line) for line in lines)
    result = Text()

    for line in lines:
        for i, char in enumerate(line):
            factor = i / max(1, max_len - 1)
            color = _interpolate_color(colors, factor)
            result.append(char, style=f"bold {color}")
        result.append("\n")

    return result


class TUI:
    def __init__(self, config: Config, console: Console | None = None,) -> None:
        self.console = console or get_console()
        self._assistant_stream_open = False
        self._tool_args_by_call_id: dict[str, dict[str, Any]] = {}
        self.config = config
        self.cwd = self.config.cwd
        self._max_block_tokens = 2500
    
    def begin_assistant(self) -> None:
        self.console.print()
        self.console.print(Rule(Text(" ✦ Assistant ", style="bold #e7aafb"), style="#374151"))
        self._assistant_stream_open = True

    def end_assistant(self) -> None:
        if self._assistant_stream_open:
            self.console.print()

        self._assistant_stream_open = False

    def begin_streaming_markdown(self) -> None:
        self.console.print()
        self.console.print(Rule(Text(" ✦ Assistant ", style="bold #e7aafb"), style="#374151"))
        self._markdown_buffer = ""
        self._live = Live(Markdown(""), console=self.console, refresh_per_second=10, transient=False)
        self._live.start()

    def stream_markdown_delta(self, content: str) -> None:
        self._markdown_buffer += content
        self._live.update(Markdown(self._markdown_buffer))

    def end_streaming_markdown(self) -> None:
        if hasattr(self, '_live') and self._live:
            self._live.stop()
            self._live = None
        self.console.print()

    def stream_assistant_delta(self, content: str) -> None:
        self.console.print(content, end="", markup=False)

    def render_assistant_markdown(self, content: str) -> None:
        self.console.print(Markdown(content))

    def _ordered_args(self, tool_name: str, args: dict[str, Any]) -> list[tuple]:
        _PREFERRED_ORDER = {
            'read_file' : ['path', 'offset', 'limit'],
            'write_file' : ['path', 'create_directories', 'content'],
            'edit' : ['path', 'replace_all', 'old_string', 'new_string'],
            'shell' : ['command', 'timeout', 'cwd'],
            'list_dir' : ['path', 'include_hidden'],
            'grep' : ["path", 'case_insensitive', 'pattern'],
            'glob' : ['path', 'pattern'],
            'todos' : ['id', 'action', 'content'],
            'memory' : ['action', 'key', 'value']
        }
        
        preferred = _PREFERRED_ORDER.get(tool_name, [])
        ordered: list[tuple[str, Any]] = []
        seen = set()

        for key in preferred:
            if key in args:
                ordered.append((key, args[key]))
                seen.add(key)

        remaining_keys = set(args.keys() - seen)
        ordered.extend((key, args[key]) for key in remaining_keys) 

        return ordered       

    def _render_args_table(self, tool_name: str, args: dict[str, Any]) -> Table:
        table = Table.grid(padding=(0,1))
        table.add_column(style="muted", justify='right', no_wrap=True)
        table.add_column(style="code", overflow="fold")

        for key, value in self._ordered_args(tool_name, args):
            if key in {'content', 'old_string', 'new_string'} and isinstance(value, str):
                line_count = len(value.splitlines()) or 0
                byte_count = len(value.encode('utf-8', errors='replace'))
                value = f"<{line_count} lines ⚬ {byte_count} bytes>"

            if not isinstance(value, str):
                value = str(value)

            table.add_row(key, value)

        return table

    def tool_call_start(self, 
                        call_id: str, 
                        name: str, 
                        tool_kind: str | None,
                        arguments: dict[str, Any],) -> None:

        self._tool_args_by_call_id[call_id] = arguments
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"

        title = Text.assemble(
            ("⚡ ", "bold #a191f8"),
            (name, f"tool.{tool_kind}" if tool_kind else "tool"),
            (" ", "muted"),
            (f"#{call_id[:8]}", "muted")
        )

        display_args = dict(arguments)
        for key in ('path', 'cwd'):
            val = display_args.get(key)
            if isinstance(val , str) and self.cwd:
                display_args[key] = str(display_path_rel_to_cwd(val, self.cwd))

        empty_args: dict[str, Any] = {}
        panel_args = display_args if isinstance(display_args, dict) and display_args else empty_args

        panel = Panel(
            self._render_args_table(name, panel_args),
            title = title,
            title_align='left',
            subtitle=Text('⚡ running', style="italic #8bcefc"),
            subtitle_align='right',
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)

    def _extract_read_file_code(self, text: str) -> tuple[int, str] | None:
        body = text
        header_match = re.match(r"^Showing Lines (\d+) - (\d+) of (\d+)\n\n", text)
        if header_match:
            body = text[header_match.end() :]

        code_lines: list[str] = []
        start_line: int | None = None
        
        for line in body.splitlines():
            m = re.match(r"^\s*(\d+)\s*\|(.*)$", line)
            if not m:
                continue
            
            line_no = int(m.group(1))
            if start_line is None:
                start_line = line_no    
            code_lines.append(m.group(2))

        if start_line is None or not code_lines:
            return None
        
        return start_line, "\n".join(code_lines)
        
    def _guess_language(self, path: str | None) -> str:
        if not path:
            return "text"
        suffix = Path(path).suffix.lower()
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".json": "json",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".kt": "kotlin",
            ".swift": "swift",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".css": "css",
            ".html": "html",
            ".xml": "xml",
            ".sql": "sql",
        }.get(suffix, "text")

    def print_welcome(self, title: str, lines: list[str]) -> None:
        self.console.print()
        banner = render_gradient_ascii(FLUX_ASCII_ART, FLUX_GRADIENT_COLORS)
        self.console.print(banner)

        content = Text()
        for i, line in enumerate(lines):
            if line.startswith("model:"):
                val = line[6:].strip()
                content.append("model: ", style="dim")
                content.append(val, style="bold #8bcefc")
            elif line.startswith("cwd:"):
                val = line[4:].strip()
                content.append("cwd: ", style="dim")
                content.append(val, style="bold #7fe4eb")
            elif line.startswith("commands:"):
                content.append("commands: ", style="dim")
                cmds = line[9:].strip().split()
                cmd_colors = ["#e7aafb", "#a191f8", "#8bcefc", "#7fe4eb", "#f43f5e", "#4ade80"]
                for c_idx, cmd in enumerate(cmds):
                    c_color = cmd_colors[c_idx % len(cmd_colors)]
                    content.append(cmd, style=f"bold {c_color}")
                    if c_idx < len(cmds) - 1:
                        content.append("  ", style="dim")
            else:
                content.append(line, style="code")

            if i < len(lines) - 1:
                content.append("\n")

        self.console.print(
            Panel(
                content,
                title=Text(f"✦ {title}", style="bold #7fe4eb"),
                title_align="left",
                border_style="#374151",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )


    def tool_call_complete(self, 
                        call_id: str, 
                        name: str, 
                        tool_kind: str | None,
                        success: bool,
                        output: str,
                        error: str | None,
                        metadata: dict[str, Any] | None,
                        diff: str | None,
                        truncated: bool,
                        exit_code: int | None,
                        ) -> None:

        border_style = f"tool.{tool_kind}" if tool_kind else "tool"
        status_icon = "✔" if success else "✘"
        status_style = 'success' if success else 'error'

        title = Text.assemble(
            (f"{status_icon} ", status_style),
            (name, "tool"),
            (" ", "muted"),
            (f"#{call_id[:8]}", "muted")
        )

        args = self._tool_args_by_call_id.get(call_id, {})
        primary_path = None
        blocks = []

        if isinstance(metadata, dict) and isinstance(metadata.get("path"), str):
            primary_path = metadata.get("path")

        if name == "read_file" and success:
            if primary_path:
                start_line, code = self._extract_read_file_code(output)

                shown_start = metadata.get('shown_start')
                shown_end = metadata.get('shown_end')
                total_lines = metadata.get('total_lines')

                pl = self._guess_language(primary_path)

                header_parts = [display_path_rel_to_cwd(primary_path, self.cwd)]
                header_parts.append(" ⚬ ")

                if shown_start and shown_end and total_lines:
                    header_parts.append(f"lines {shown_start}-{shown_end} of {total_lines}")

                header = "".join(header_parts)
                blocks.append(Text(header, style='muted'))
                blocks.append(Syntax(
                    code, 
                    pl,
                    theme='dracula',
                    line_numbers=True,
                    start_line=start_line,
                    word_wrap=False,
                    )
                )
            
            else:
                output_display = truncate_text(output, "", self._max_block_tokens, )
                blocks.append(Syntax(
                    output_display,
                    'text',
                    theme='dracula',
                    word_wrap=False,
                ))
        
        elif name in {'write_file', 'edit'} and success and diff: 
            output_line = output.strip() if output.strip() else 'Completed'
            blocks.append(Text(output_line, style='muted'))
            diff_text = diff
            diff_display = truncate_text(diff_text, self.config.model_name, self._max_block_tokens)
            
            blocks.append(Syntax(diff_display, 'diff', theme='dracula', word_wrap=True))

        elif name == 'shell' and success:
            command = args.get('command')
            if isinstance(command, str) and command.strip():
                blocks.append(Text(f'$ {command.strip()}', style='muted'))
            
            if exit_code is not None:
                blocks.append(Text(f'exit_code={exit_code}', style='muted'))

            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens,)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))

        elif name == 'list_dir' and success:
            entries = metadata.get('entries')
            path = metadata.get('path')
            summary = []
            if isinstance(path, str):
                summary.append(path)
            
            if isinstance(entries, int):
                summary.append(f"{entries} entries")

            if summary:
                blocks.append(Text(' ⦁ '.join(summary), style='muted'))

            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))

        elif name == "grep" and success:
            matches = metadata.get('matches')
            files_searched = metadata.get('files_searched')
            summary = []
            
            if isinstance(matches, int):
                summary.append(f"{matches} matches")
            if isinstance(files_searched, int):
                summary.append(f"searched {files_searched} files")
            
            if summary:
                blocks.append(Text(' ⦁ '.join(summary), style='muted'))

            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
        
        elif name == "glob" and success:
            matches = metadata.get('matches')
            
            if isinstance(matches, int):
                blocks.append(Text(f"{matches} matches", style='muted'),)
            
            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
            
        elif name == "web_search" and success:
            results = metadata.get('results')
            query = args.get('query')
            summary = []

            if isinstance(query, str):
                summary.append(query)
            if isinstance(results, int):
                summary.append(f"{results} results")
            
            if summary:
                blocks.append(Text(' ⦁ '.join(summary), style='muted'))
            
            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
        
        elif name == "web_fetch" and success:
            status_code = metadata.get('status_code')
            content_length = metadata.get('content_length')
            url = args.get('url')
            summary = []

            if isinstance(status_code, int):
                summary.append(str(status_code))
            if isinstance(content_length, int):
                summary.append(f"{content_length} bytes")
            if isinstance(url, str):
                summary.append(url)
            
            if summary:
                blocks.append(Text(' ⦁ '.join(summary), style='muted'))
            
            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))

        elif name.startswith('subagent_') and success:
            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
            
        
        elif name == "todos" and success:
            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
        
        elif name == "memory" and success:
            action = args.get('action')
            key = args.get('key')
            found = metadata.get('found')
            summary = []
            if isinstance(action, str) and action:
                summary.append(action)
            if isinstance(key, str) and key:
                summary.append(key)
            if isinstance(found, bool):
                summary.append('found' if found else 'missing')

            if summary:
                blocks.append(Text(' ⦁ '.join(summary), style='muted'))

            output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
            blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
            
        else:
            if not success:
                if error:
                    blocks.append(Text(error, style='error'))

                output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
                if output_display.strip():
                    blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
                elif not error:
                    blocks.append(Text('(no output)', style='muted'))
            else:
                output_display = truncate_text(output, self.config.model_name, self._max_block_tokens)
                if output_display.strip():
                    blocks.append(Syntax(output_display, 'text', theme='dracula', word_wrap=True))
                else:
                    blocks.append(Text('(no output)', style='muted'))

        if truncated:
            blocks.append(Text('note: tool output was truncated', style='warning'))

        panel = Panel(
            Group(
                *blocks
            ),
            
            title = title,
            title_align='left',
            subtitle=Text('done' if success else "failed", style=status_style),
            subtitle_align='right',
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)

    def handle_confirmation(self, confirmation: ToolConfirmation) -> bool:
        output = [
            Text(confirmation.tool_name, style="tool"),
            Text(confirmation.description, style="code"),
        ]

        if confirmation.command:
            output.append(Text(f"$ {confirmation.command}", style="warning"))

        if confirmation.diff:
            diff_text = confirmation.diff.to_diff()
            output.append(
                Syntax(
                    diff_text,
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                )
            )

        self.console.print()
        self.console.print(
            Panel(
                Group(*output),
                title=Text("Approval required", style="warning"),
                title_align="left",
                border_style="warning",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        response = Prompt.ask(
            "\nApprove?", choices=["y", "n", "yes", "no"], default="n"
        )

        return response.lower() in {"y", "yes"}

    def show_help(self) -> None:
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold #a191f8", justify="right", no_wrap=True)
        table.add_column(style="dim")

        table.add_row("/help", "Show this help dialog")
        table.add_row("/exit, /quit", "Exit the agent session")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/config", "Show active configuration")
        table.add_row("/model <name>", "Switch LLM model at runtime")
        table.add_row("/approval <mode>", "Set safety approval policy (on-request, auto, yolo)")
        table.add_row("/stats", "Display session token usage & turn stats")
        table.add_row("/tools", "List available tools")
        table.add_row("/mcp", "Show MCP server connection status")
        table.add_row("/save", "Save current session state")
        table.add_row("/checkpoint [name]", "Create a named checkpoint")
        table.add_row("/checkpoints", "List saved checkpoints")
        table.add_row("/restore <id>", "Restore session from a checkpoint")
        table.add_row("/sessions", "List all saved sessions")
        table.add_row("/resume <id>", "Resume a previously saved session")

        tips = Text()
        tips.append("\nPro Tips:\n", style="bold #e7aafb")
        tips.append(" ⦁ Type plain text to chat or request coding assistance\n", style="dim")
        tips.append(" ⦁ Reference workspace files directly in your prompts\n", style="dim")
        tips.append(" ⦁ Configure hooks in ", style="dim")
        tips.append(".flux-cli/config.toml", style="bold #8bcefc")
        tips.append(" for event triggers\n", style="dim")

        content = Group(table, tips)

        self.console.print()
        self.console.print(
            Panel(
                content,
                title=Text("✦ Flux-CLI Commands & Help", style="bold #7fe4eb"),
                title_align="left",
                border_style="#374151",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
