import asyncio
import json
import logging
import os
import shlex
import signal
import sys
import tempfile
from typing import Any
from flux_cli.config.config import Config, HookConfig, HookTrigger
from flux_cli.tools.base import ToolResult

logger = logging.getLogger(__name__)


class HookSystem:
    def __init__(self, config: Config):
        self.config = config
        self.hooks: list[HookConfig] = []
        if self.config.hooks_enabled:
            self.hooks = [hook for hook in self.config.hooks if hook.enabled]

    async def _run_hook(self, hook: HookConfig, env: dict[str, str]) -> None:
        try:
            if hook.command:
                await self._run_command(hook.command, hook.timeout_sec, env)
            elif hook.script:
                if sys.platform == "win32":
                    cmd = f'bash -c {shlex.quote(hook.script)}'
                    await self._run_command(cmd, hook.timeout_sec, env)
                else:
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".sh", delete=False, newline="\n"
                    ) as f:
                        f.write("#!/bin/bash\n")
                        f.write(hook.script)
                        script_path = f.name
                    try:
                        os.chmod(script_path, 0o755)
                        await self._run_command(f'"{script_path}"', hook.timeout_sec, env)
                    finally:
                        if os.path.exists(script_path):
                            os.unlink(script_path)
        except Exception as e:
            logger.exception(f"Error executing hook '{hook.name}': {e}")

    async def _run_command(
        self,
        command: str,
        timeout: float,
        env: dict[str, str],
    ) -> None:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.config.cwd,
            env=env,
            start_new_session=True,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            stdout_str = stdout.decode(errors="replace").strip()
            stderr_str = stderr.decode(errors="replace").strip()

            if stdout_str:
                logger.debug(f"Hook stdout: {stdout_str}")
            if stderr_str:
                logger.warning(f"Hook stderr: {stderr_str}")

            if process.returncode != 0:
                logger.warning(
                    f"Hook command '{command}' failed with exit code {process.returncode}"
                )
        except asyncio.TimeoutError:
            logger.warning(
                f"Hook command '{command}' timed out after {timeout} seconds"
            )
            if sys.platform != "win32":
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except Exception:
                    process.kill()
            else:
                try:
                    await asyncio.create_subprocess_shell(
                        f"taskkill /F /T /PID {process.pid}",
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                except Exception:
                    process.kill()
            await process.wait()

    def _build_env(
        self,
        trigger: HookTrigger,
        tool_name: str | None = None,
        user_message: str | None = None,
        error: Exception | None = None,
    ) -> dict[str, str]:
        env = os.environ.copy()
        env["AI_AGENT_TRIGGER"] = str(trigger.value)
        env["AI_AGENT_CWD"] = str(self.config.cwd)

        if tool_name is not None:
            env["AI_AGENT_TOOL_NAME"] = str(tool_name)

        if user_message is not None:
            env["AI_AGENT_USER_MESSAGE"] = str(user_message)

        if error is not None:
            env["AI_AGENT_ERROR"] = str(error)

        return env

    async def trigger_before_agent(self, user_message: str) -> None:
        env = self._build_env(
            HookTrigger.BEFORE_AGENT,
            user_message=user_message,
        )

        for hook in self.hooks:
            if hook.trigger == HookTrigger.BEFORE_AGENT:
                await self._run_hook(hook, env)

    async def trigger_after_agent(
        self,
        user_message: str,
        agent_response: str | None = None,
    ) -> None:
        env = self._build_env(
            HookTrigger.AFTER_AGENT,
            user_message=user_message,
        )
        env["AI_AGENT_RESPONSE"] = str(agent_response) if agent_response is not None else ""

        for hook in self.hooks:
            if hook.trigger == HookTrigger.AFTER_AGENT:
                await self._run_hook(hook, env)

    async def trigger_before_tool(
        self,
        tool_name: str,
        tool_params: dict[str, Any],
    ) -> None:
        env = self._build_env(HookTrigger.BEFORE_TOOL, tool_name=tool_name)
        env["AI_AGENT_TOOL_PARAMS"] = json.dumps(tool_params)

        for hook in self.hooks:
            if hook.trigger == HookTrigger.BEFORE_TOOL:
                await self._run_hook(hook, env)

    async def trigger_after_tool(
        self,
        tool_name: str,
        tool_params: dict[str, Any],
        tool_result: ToolResult,
    ) -> None:
        env = self._build_env(HookTrigger.AFTER_TOOL, tool_name=tool_name)
        env["AI_AGENT_TOOL_PARAMS"] = json.dumps(tool_params)
        env["AI_AGENT_TOOL_RESULT"] = str(tool_result.to_model_output())

        for hook in self.hooks:
            if hook.trigger == HookTrigger.AFTER_TOOL:
                await self._run_hook(hook, env)

    async def trigger_on_error(self, error: Exception) -> None:
        env = self._build_env(HookTrigger.ON_ERROR, error=error)

        for hook in self.hooks:
            if hook.trigger == HookTrigger.ON_ERROR:
                await self._run_hook(hook, env)
