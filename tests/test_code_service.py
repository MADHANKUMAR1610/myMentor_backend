"""Manual test for the code execution service."""

import asyncio

from app.schemas import RunRequest
from app.services import code_execution_service


async def main() -> None:
    request = RunRequest(
        language="python",
        source_code="print(123)",
    )

    result = await code_execution_service.run_code(request)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())