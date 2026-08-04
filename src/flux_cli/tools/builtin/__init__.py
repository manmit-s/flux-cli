from flux_cli.tools.builtin.edit_file import EditTool
from flux_cli.tools.builtin.glob import GlobTool
from flux_cli.tools.builtin.grep import GrepTool
from flux_cli.tools.builtin.list_dir import ListDirTool
from flux_cli.tools.builtin.memory import MemoryTool
from flux_cli.tools.builtin.read_file import ReadFileTool
from flux_cli.tools.builtin.shell import ShellTool
from flux_cli.tools.builtin.todo import ToDoTool
from flux_cli.tools.builtin.web_fetch import WebFetchTool
from flux_cli.tools.builtin.web_search import WebSearchTool
from flux_cli.tools.builtin.write_file import WriteFileTool

__all__ = [
    "ReadFileTool",
    "WriteFileTool",
    "EditTool",
    "ShellTool",
    "ListDirTool",
    "GrepTool",
    "GlobTool",
    "WebSearchTool",
    "WebFetchTool",
    "ToDoTool",
    "MemoryTool",
    ]

def get_all_builtin_tools() -> list[type]:
    return[
        ReadFileTool,
        WriteFileTool,
        EditTool,
        ShellTool,
        ListDirTool,
        GrepTool,
        GlobTool,
        WebSearchTool,
        WebFetchTool,
        ToDoTool,
        MemoryTool,

    ]