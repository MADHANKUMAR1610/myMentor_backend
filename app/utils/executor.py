"""Code execution engine."""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Tuple

LOCAL_TIMEOUT = 5


async def _run_local(
    cmd: list[str],
    stdin: str,
    cwd: str,
) -> Tuple[str, str, int]:
    """Run a local command."""

    start = time.monotonic()

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(
                input=stdin.encode() if stdin else None
            ),
            timeout=LOCAL_TIMEOUT,
        )

        elapsed = int(
            (time.monotonic() - start) * 1000
        )

        return (
            stdout.decode(errors="replace"),
            stderr.decode(errors="replace"),
            elapsed,
        )

    except asyncio.TimeoutError:
        process.kill()
        await process.wait()

        return (
            "",
            f"Time Limit Exceeded ({LOCAL_TIMEOUT}s)",
            LOCAL_TIMEOUT * 1000,
        )

    except FileNotFoundError as exc:
        return (
            "",
            str(exc),
            0,
        )

    except NotImplementedError:
        # Windows fallback
        try:
            result = subprocess.run(
                cmd,
                input=stdin,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=LOCAL_TIMEOUT,
            )

            elapsed = int(
                (time.monotonic() - start) * 1000
            )

            return (
                result.stdout,
                result.stderr,
                elapsed,
            )

        except subprocess.TimeoutExpired:
            return (
                "",
                f"Time Limit Exceeded ({LOCAL_TIMEOUT}s)",
                LOCAL_TIMEOUT * 1000,
            )

        except Exception as exc:
            return (
                "",
                str(exc),
                0,
            )

    except Exception as exc:
        return (
            "",
            str(exc),
            0,
        )


async def execute_code(
    language: str,
    source_code: str,
    stdin: str = "",
) -> Tuple[str, str, int]:
    """Execute source code."""

    language = language.lower().strip()

    tmpdir = tempfile.mkdtemp(
        prefix="digipin_exec_"
    )

    try:

        if language == "python":
            file = os.path.join(
                tmpdir,
                "main.py",
            )

            with open(
                file,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(source_code)

            return await _run_local(
                [sys.executable, file],
                stdin,
                tmpdir,
            )

        elif language == "javascript":
            file = os.path.join(
                tmpdir,
                "main.js",
            )

            with open(
                file,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(source_code)

            return await _run_local(
                ["node", file],
                stdin,
                tmpdir,
            )

        elif language == "java":
            file = os.path.join(
                tmpdir,
                "Main.java",
            )

            with open(
                file,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(source_code)

            _, err, t = await _run_local(
                ["javac", file],
                "",
                tmpdir,
            )

            if err:
                return "", err, t

            return await _run_local(
                [
                    "java",
                    "-cp",
                    tmpdir,
                    "Main",
                ],
                stdin,
                tmpdir,
            )

        elif language in (
            "cpp",
            "c++",
        ):
            src = os.path.join(
                tmpdir,
                "main.cpp",
            )

            exe = os.path.join(
                tmpdir,
                "main.exe"
                if os.name == "nt"
                else "main",
            )

            with open(
                src,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(source_code)

            _, err, t = await _run_local(
                [
                    "g++",
                    src,
                    "-std=c++17",
                    "-O2",
                    "-o",
                    exe,
                ],
                "",
                tmpdir,
            )

            if err:
                return "", err, t

            return await _run_local(
                [exe],
                stdin,
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
    """Normalize output."""

    return "\n".join(
        line.rstrip()
        for line in text.strip().splitlines()
    )