"""Code execution engine.

Uses local subprocess-based execution for supported languages.

For a production deployment, untrusted code execution should be moved
to an isolated execution service such as Judge0.
"""

import asyncio
import os
import shutil
import sys
import tempfile
import time
from typing import Tuple


# Judge0 configuration
JUDGE0_API_KEY = os.environ.get("JUDGE0_API_KEY", "")
JUDGE0_HOST = os.environ.get(
    "JUDGE0_HOST",
    "judge0-ce.p.rapidapi.com",
)
JUDGE0_BASE = f"https://{JUDGE0_HOST}"

JUDGE0_LANG = {
    "python": 71,
    "javascript": 63,
    "java": 62,
    "cpp": 54,
}

LOCAL_TIMEOUT = 5


async def _run_local(
    cmd: list[str],
    stdin: str,
    cwd: str,
) -> Tuple[str, str, int]:
    """Run a local command with an execution timeout."""

    start = time.monotonic()
    process = None

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(
                input=(
                    stdin.encode("utf-8")
                    if stdin
                    else None
                )
            ),
            timeout=LOCAL_TIMEOUT,
        )

        elapsed_ms = int(
            (time.monotonic() - start) * 1000
        )

        stdout = stdout_bytes.decode(
            "utf-8",
            errors="replace",
        )

        stderr = stderr_bytes.decode(
            "utf-8",
            errors="replace",
        )

        return stdout, stderr, elapsed_ms

    except asyncio.TimeoutError:
        if process is not None:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass

        elapsed_ms = int(
            (time.monotonic() - start) * 1000
        )

        return (
            "",
            f"Time Limit Exceeded ({LOCAL_TIMEOUT}s)",
            elapsed_ms,
        )

    except FileNotFoundError as exc:
        elapsed_ms = int(
            (time.monotonic() - start) * 1000
        )

        return (
            "",
            f"Execution runtime not found: {exc}",
            elapsed_ms,
        )


async def execute_code(
    language: str,
    source_code: str,
    stdin: str = "",
) -> Tuple[str, str, int]:
    """Execute source code and return stdout, stderr, and time."""

    language = language.lower().strip()

    tmpdir = tempfile.mkdtemp(
        prefix="digipin_exec_"
    )

    try:
        if language == "python":
            src_path = os.path.join(
                tmpdir,
                "main.py",
            )

            with open(
                src_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(source_code)

            return await _run_local(
                [sys.executable, src_path],
                stdin or "",
                tmpdir,
            )

        if language == "javascript":
            src_path = os.path.join(
                tmpdir,
                "main.js",
            )

            with open(
                src_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(source_code)

            return await _run_local(
                ["node", src_path],
                stdin or "",
                tmpdir,
            )

        if language == "java":
            src_path = os.path.join(
                tmpdir,
                "Main.java",
            )

            with open(
                src_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(source_code)

            _, compile_error, compile_time = (
                await _run_local(
                    ["javac", src_path],
                    "",
                    tmpdir,
                )
            )

            if compile_error:
                return (
                    "",
                    compile_error,
                    compile_time,
                )

            return await _run_local(
                [
                    "java",
                    "-cp",
                    tmpdir,
                    "Main",
                ],
                stdin or "",
                tmpdir,
            )

        if language in ("cpp", "c++"):
            src_path = os.path.join(
                tmpdir,
                "main.cpp",
            )

            executable_name = (
                "main.exe"
                if os.name == "nt"
                else "main"
            )

            binary_path = os.path.join(
                tmpdir,
                executable_name,
            )

            with open(
                src_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(source_code)

            _, compile_error, compile_time = (
                await _run_local(
                    [
                        "g++",
                        "-O2",
                        "-std=c++17",
                        src_path,
                        "-o",
                        binary_path,
                    ],
                    "",
                    tmpdir,
                )
            )

            if compile_error:
                return (
                    "",
                    compile_error,
                    compile_time,
                )

            return await _run_local(
                [binary_path],
                stdin or "",
                tmpdir,
            )

        return (
            "",
            f"Unsupported language: {language}",
            0,
        )

    finally:
        shutil.rmtree(
            tmpdir,
            ignore_errors=True,
        )


def normalize(text: str) -> str:
    """Normalize code output for comparison."""

    return "\n".join(
        line.rstrip()
        for line in text.strip().splitlines()
    )