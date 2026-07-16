"""Code execution business logic."""

import logging

from app.core.exceptions import NotFoundException
from app.repositories import (
    challenge_repository,
    progress_repository,
)
from app.schemas import (
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
    TestCaseResult,
    gen_id,
    utc_now_iso,
)
from app.utils.executor import (
    execute_code,
    normalize,
)

logger = logging.getLogger(__name__)


class CodeExecutionService:
    """Handle code execution and submission evaluation."""

    def __init__(self) -> None:
        self.challenge_repository = challenge_repository
        self.progress_repository = progress_repository

    async def run_code(
        self,
        request: RunRequest,
    ) -> RunResult:
        """Execute code without evaluation."""

        logger.info(
            "Running %s code",
            request.language,
        )

        stdout, stderr, execution_time = await execute_code(
            request.language,
            request.source_code,
            request.stdin or "",
        )

        logger.info(
            "Code execution completed in %sms",
            execution_time,
        )

        return RunResult(
            stdout=stdout,
            stderr=stderr,
            time_ms=execution_time,
        )

    async def submit_code(
        self,
        request: SubmissionRequest,
        user_id: str,
    ) -> SubmissionResult:
        """Evaluate code against challenge test cases."""

        logger.info(
            "User %s submitted challenge %s",
            user_id,
            request.challenge_id,
        )

        challenge = (
            await self.challenge_repository.get_challenge_by_id(
                request.challenge_id
            )
        )

        if not challenge:
            logger.warning(
                "Challenge not found: %s",
                request.challenge_id,
            )

            raise NotFoundException(
                "Challenge not found"
            )

        test_cases = challenge.get(
            "test_cases",
            [],
        )

        if not test_cases:
            test_cases = [
                {
                    "input": "",
                    "expected_output": challenge.get(
                        "expected_output",
                        "",
                    ),
                    "is_hidden": False,
                }
            ]

        test_results: list[TestCaseResult] = []
        total_time = 0

        for test_case in test_cases:
            result, execution_time = (
                await self._execute_test_case(
                    request,
                    test_case,
                )
            )

            test_results.append(result)
            total_time += execution_time

        passed_count = sum(
            result.passed
            for result in test_results
        )

        total_count = len(test_results)

        all_passed = (
            passed_count == total_count
        )

        xp_earned = (
            challenge.get(
                "xp",
                0,
            )
            if all_passed
            else 0
        )

        submission_document = {
            "id": gen_id(),
            "user_id": user_id,
            "challenge_id": request.challenge_id,
            "language": request.language,
            "source_code": request.source_code,
            "passed": all_passed,
            "passed_count": passed_count,
            "total_count": total_count,
            "xp_earned": xp_earned,
            "time_ms": total_time,
            "created_at": utc_now_iso(),
        }

        await self.progress_repository.create_submission(
            submission_document
        )

        logger.info(
            "Submission completed. Passed=%s (%s/%s)",
            all_passed,
            passed_count,
            total_count,
        )

        return SubmissionResult(
            passed=all_passed,
            stdout="",
            stderr="",
            time_ms=total_time,
            test_results=test_results,
            passed_count=passed_count,
            total_count=total_count,
            xp_earned=xp_earned,
        )

    async def _execute_test_case(
        self,
        request: SubmissionRequest,
        test_case: dict,
    ) -> tuple[TestCaseResult, int]:
        """Execute and evaluate a single test case."""

        stdout, stderr, execution_time = await execute_code(
            request.language,
            request.source_code,
            test_case.get(
                "input",
                "",
            ),
        )

        expected_output = test_case[
            "expected_output"
        ]

        passed = (
            normalize(stdout)
            == normalize(expected_output)
            and not stderr.strip()
        )

        is_hidden = test_case.get(
            "is_hidden",
            False,
        )

        result = TestCaseResult(
            input=(
                "(hidden)"
                if is_hidden
                else test_case.get(
                    "input",
                    "",
                )
            ),
            expected=(
                "(hidden)"
                if is_hidden
                else expected_output
            ),
            actual=(
                (
                    "passed"
                    if passed
                    else "failed"
                )
                if is_hidden
                else stdout
            ),
            passed=passed,
            is_hidden=is_hidden,
        )

        return result, execution_time


code_execution_service = CodeExecutionService()