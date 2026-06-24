from pydantic import BaseModel, Field

from tools.base import ToolInvocation, ToolKind, ToolResult, Tools
from utils.paths import ensure_parent_directory, resolve_path


class EditParams(BaseModel):
    path: str = Field(
        ..., description="Path to the file to edit (relative to working directory or absolute path)",
    )
    old_string: str = Field(
        "", description="The exact text to find and replace. Must match exactly including all whitespaces and indentation. For new files, leave this empty.",
    )
    new_string: str = Field(
        ..., description="The text to replace old_string with. Can be empty to delete text" ,
    )
    replace_all: bool = Field(
        False, description="Replace all occurences of old_string (default: false)",
    )

class EditTool(Tools):
    name = 'edit'
    description = (
         "Edit a file by replacing text. The old_string must match exactly "
        "(including whitespace and indentation) and must be unique in the file "
        "unless replace_all is true. Use this for precise, surgical edits. "
        "For creating new files or complete rewrites, use write_file instead."
    )
    kind = ToolKind.WRITE
    schema = EditParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = EditParams(**invocation.params)
        path =  resolve_path(invocation.cwd, params.path)

        if not path.exists():
            if params.old_string:
                return ToolResult.error_result(f"File doesn't exists: {path}. To create a new file, use an empty old string."
                                               )
            ensure_parent_directory(path)
            path.write_text(params.new_string, encoding='utf-8')

            ###BOOKMARK####