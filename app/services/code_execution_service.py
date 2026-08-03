"""Code execution business logic."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas import (
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
    TestCaseResult,
)
from app.schemas.common import gen_id
from app.utils.executor import execute_code, normalize

logger = logging.getLogger(__name__)


class CodeExecutionService:
    """Handle code execution and submission evaluation."""

    def __init__(self, db: AsyncSession):
        self.challenge_repository = ChallengeRepository(db)
        self.progress_repository = ProgressRepository(db)

    async def run_code(
        self,
        request: RunRequest,
    ) -> RunResult:
        """Execute code without evaluation."""

        stdout, stderr, execution_time = await execute_code(
            request.language,
            request.source_code,
            request.stdin or "",
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
        """Evaluate submitted code."""
        try:
            print("========== STEP 1 ==========")

            challenge = await self.challenge_repository.get_challenge_by_id(
                request.challenge_id
            )

            print("Challenge:", challenge)

            if challenge is None:
                raise Exception("Challenge not found")

            test_cases = challenge.test_cases or []

            if not test_cases:
                test_cases = [
                    {
                        "input": "",
                        "expected_output": challenge.expected_output,
                        "is_hidden": False,
                    }
                ]

            test_results = []
            total_time = 0

            for test_case in test_cases:

                stdout, stderr, execution_time = await execute_code(
                    request.language,
                    request.source_code,
                    test_case.get("input", ""),
                )

                total_time += execution_time

                passed = (
                    normalize(stdout)
                    == normalize(test_case["expected_output"])
                    and not stderr.strip()
                )

                test_results.append(
                    TestCaseResult(
                        input=(
                            "(hidden)"
                            if test_case.get("is_hidden")
                            else test_case.get("input", "")
                        ),
                        expected=(
                            "(hidden)"
                            if test_case.get("is_hidden")
                            else test_case["expected_output"]
                        ),
                        actual=(
                            "passed"
                            if test_case.get("is_hidden") and passed
                            else (
                                "failed"
                                if test_case.get("is_hidden")
                                else stdout
                            )
                        ),
                        passed=passed,
                        is_hidden=test_case.get(
                            "is_hidden",
                            False,
                        ),
                    )
                )

            passed_count = sum(
                result.passed
                for result in test_results
            )

            total_count = len(test_results)

            all_passed = (
                passed_count == total_count
            )

            xp_earned = (
                challenge.xp
                if all_passed
                else 0
            )

            print("========== STEP 2 ==========")

            submission = Submission(
                id=gen_id(),
                user_id=user_id,
                challenge_id=request.challenge_id,
                source_code=request.source_code,
                language=request.language,
                stdout="",
                stderr="",
                passed=all_passed,
                passed_count=passed_count,
                total_count=total_count,
                xp_earned=xp_earned,
                time_ms=total_time,
            )

            print("Saving submission...")

            await self.progress_repository.create_submission(
                submission
            )

            print("Submission saved")

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

        except Exception as e:
            import traceback

            print("\n========== SERVICE ERROR ==========")
            traceback.print_exc()
            print(repr(e))
            print("===================================\n")

            raise