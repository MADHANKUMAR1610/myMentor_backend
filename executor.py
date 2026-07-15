"""Code execution engine.

Uses local subprocess-based sandbox for Python & JavaScript.
For a production deployment, switch `execute_code` to Judge0 CE via RapidAPI —
the interface (language, source_code, stdin) matches Judge0's payload.
"""
import asyncio
import os
import shutil
import tempfile
import time
from typing import Tuple

# Judge0 config (used when JUDGE0_API_KEY is set)
JUDGE0_API_KEY = os.environ.get("JUDGE0_API_KEY", "")
JUDGE0_HOST = os.environ.get("JUDGE0_HOST", "judge0-ce.p.rapidapi.com")
JUDGE0_BASE = f"https://{JUDGE0_HOST}"

JUDGE0_LANG = {"python": 71, "javascript": 63, "java": 62, "cpp": 54}
LOCAL_TIMEOUT = 5  # seconds


async def _run_local(cmd: list, stdin: str, cwd: str) -> Tuple[str, str, int]:
    """Run a command locally with timeout."""
    start = time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(input=stdin.encode("utf-8") if stdin else None),
            timeout=LOCAL_TIMEOUT,
        )
        elapsed_ms = int((time.time() - start) * 1000)
        return stdout_b.decode("utf-8", errors="replace"), stderr_b.decode(
            "utf-8", errors="replace"
        ), elapsed_ms
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        elapsed_ms = int((time.time() - start) * 1000)
        return "", f"Time Limit Exceeded ({LOCAL_TIMEOUT}s)", elapsed_ms


async def execute_code(
    language: str, source_code: str, stdin: str = ""
) -> Tuple[str, str, int]:
    """Return (stdout, stderr, elapsed_ms)."""
    language = language.lower()
    tmpdir = tempfile.mkdtemp(prefix="digipin_exec_")
    try:
        if language == "python":
            src_path = os.path.join(tmpdir, "main.py")
            with open(src_path, "w") as f:
                f.write(source_code)
            return await _run_local(["python3", src_path], stdin or "", tmpdir)
        if language == "javascript":
            src_path = os.path.join(tmpdir, "main.js")
            with open(src_path, "w") as f:
                f.write(source_code)
            return await _run_local(["node", src_path], stdin or "", tmpdir)
        if language == "java":
            src_path = os.path.join(tmpdir, "Main.java")
            with open(src_path, "w") as f:
                f.write(source_code)
            compile_out, compile_err, _ = await _run_local(
                ["javac", src_path], "", tmpdir
            )
            if compile_err:
                return "", compile_err, 0
            return await _run_local(["java", "-cp", tmpdir, "Main"], stdin or "", tmpdir)
        if language in ("cpp", "c++"):
            src_path = os.path.join(tmpdir, "main.cpp")
            bin_path = os.path.join(tmpdir, "main")
            with open(src_path, "w") as f:
                f.write(source_code)
            _, compile_err, _ = await _run_local(
                ["g++", "-O2", "-std=c++17", src_path, "-o", bin_path], "", tmpdir
            )
            if compile_err:
                return "", compile_err, 0
            return await _run_local([bin_path], stdin or "", tmpdir)
        return "", f"Unsupported language: {language}", 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())
