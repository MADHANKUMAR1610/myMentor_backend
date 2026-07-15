"""Idempotent seed script: demo accounts + sample course/levels/challenges."""
import asyncio
from datetime import datetime, timezone

from auth import hash_password
from database import db
from models import (
    Course,
    Level,
    Challenge,
    Checkpoint,
    Enrollment,
    TestCase,
    gen_id,
    utc_now_iso,
)

ADMIN_EMAIL = "admin@digipin.dev"
ADMIN_PASSWORD = "AdminPass123!"
STUDENT_EMAIL = "student@digipin.dev"
STUDENT_PASSWORD = "StudentPass123!"


async def upsert_user(email: str, password: str, name: str, role: str) -> str:
    existing = await db.users.find_one({"email": email})
    if existing:
        return existing["id"]
    user_id = gen_id()
    await db.users.insert_one(
        {
            "id": user_id,
            "email": email,
            "hashed_password": hash_password(password),
            "name": name,
            "role": role,
            "xp": 0,
            "streak_count": 0,
            "avatar_url": None,
            "created_at": utc_now_iso(),
        }
    )
    return user_id


def make_challenge(order: int, level_slug: str) -> Challenge:
    if order == 1:
        return Challenge(
            title="Print Your Name",
            business_scenario="Every program begins with a greeting.",
            problem_statement=(
                "Create a variable named `student_name` set to `Alex`. "
                "Print exactly: Hello, Alex!"
            ),
            difficulty="Easy",
            language="python",
            starter_code='student_name = "Alex"\n# print the greeting below\n',
            expected_output="Hello, Alex!",
            marks=10,
            xp=25,
            test_cases=[TestCase(input="", expected_output="Hello, Alex!")],
            hints=["Use Python's print() function", "String formatting: f'Hello, {name}!'"],
        )
    if order == 2:
        return Challenge(
            title="Employee Information",
            business_scenario=(
                "You're building an HR tool. Store an employee's details "
                "and print them in a formatted way."
            ),
            problem_statement=(
                "Given hardcoded values: name='Priya', department='Engineering', "
                "salary=85000. Print exactly three lines:\n"
                "Name: Priya\nDepartment: Engineering\nSalary: 85000"
            ),
            difficulty="Easy",
            language="python",
            starter_code=(
                "name = 'Priya'\n"
                "department = 'Engineering'\n"
                "salary = 85000\n"
                "# print three lines here\n"
            ),
            expected_output="Name: Priya\nDepartment: Engineering\nSalary: 85000",
            marks=15,
            xp=40,
            test_cases=[
                TestCase(
                    input="",
                    expected_output="Name: Priya\nDepartment: Engineering\nSalary: 85000",
                )
            ],
        )
    if order == 3:
        return Challenge(
            title="GST Calculator",
            business_scenario=(
                "A retailer needs to bill customers with GST and discount applied."
            ),
            problem_statement=(
                "Read three integers from stdin (space-separated on one line): "
                "price gst_percent discount_percent.\n"
                "Compute: final = price - (price*discount/100) + (price*gst/100)\n"
                "Print the final amount as an integer."
            ),
            difficulty="Medium",
            language="python",
            starter_code=(
                "price, gst, disc = map(int, input().split())\n"
                "# compute and print the final amount as int\n"
            ),
            expected_output="1080",
            marks=20,
            xp=60,
            test_cases=[
                TestCase(input="1000 18 10", expected_output="1080"),
                TestCase(input="500 18 0", expected_output="590", is_hidden=True),
                TestCase(input="2000 12 25", expected_output="1740", is_hidden=True),
            ],
        )
    # order 4
    return Challenge(
        title="Student Management",
        business_scenario=(
            "Build a mini student record system that receives info and "
            "outputs a report card."
        ),
        problem_statement=(
            "Read four lines from stdin: name, age, department, cgpa.\n"
            "Print exactly four lines:\n"
            "Name: <name>\nAge: <age>\nDept: <department>\nCGPA: <cgpa>"
        ),
        difficulty="Medium",
        language="python",
        starter_code=(
            "name = input()\n"
            "age = input()\n"
            "dept = input()\n"
            "cgpa = input()\n"
            "# print the four lines here\n"
        ),
        expected_output="Name: Rahul\nAge: 21\nDept: CSE\nCGPA: 8.7",
        marks=25,
        xp=100,
        test_cases=[
            TestCase(
                input="Rahul\n21\nCSE\n8.7",
                expected_output="Name: Rahul\nAge: 21\nDept: CSE\nCGPA: 8.7",
            ),
            TestCase(
                input="Ananya\n19\nECE\n9.1",
                expected_output="Name: Ananya\nAge: 19\nDept: ECE\nCGPA: 9.1",
                is_hidden=True,
            ),
        ],
    )


async def seed_course(admin_id: str, student_id: str) -> None:
    if await db.courses.find_one({"title": "Python Fundamentals"}):
        return
    course = Course(
        title="Python Fundamentals",
        description=(
            "Master Python from zero to hero — variables, loops, functions, "
            "and real-world programs. Play through 45 hands-on levels."
        ),
        thumbnail_url="https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800",
        language="Python",
        difficulty="Beginner",
        duration_hours=25,
    )
    await db.courses.insert_one(course.model_dump())

    stages = ["Beginner", "Intermediate", "Expert"]
    sample_video = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

    for stage in stages:
        for lvl_num in range(1, 6):  # 5 levels per stage for demo
            level = Level(
                course_id=course.id,
                stage=stage,
                level_number=lvl_num,
                title=f"{stage} · Level {lvl_num}: {['Variables','Control Flow','Functions','Data Structures','Mini Project'][lvl_num-1]}",
                description=(
                    f"Learn {stage.lower()} level Python concepts with interactive "
                    "checkpoints and a real coding challenge."
                ),
                learning_objectives=[
                    "Understand the concept end-to-end",
                    "Solve four progressive coding checkpoints",
                    "Build and submit a working mini-project",
                ],
                xp_reward=100 + (stages.index(stage) * 50) + (lvl_num * 10),
                video_url=sample_video,
                video_duration_seconds=1200,
                theory_html=(
                    "<h3>Learning Objectives</h3><ul>"
                    "<li>Grasp core Python syntax for this topic.</li>"
                    "<li>Apply it in a real business scenario.</li>"
                    "<li>Solve edge cases with hidden test cases.</li></ul>"
                    "<h3>Explanation</h3><p>Every level has one 20-minute lesson "
                    "and four checkpoints spaced every 5 minutes. The video pauses "
                    "automatically — you must solve the challenge to continue.</p>"
                    "<h3>Best Practices</h3><ul><li>Read the problem twice.</li>"
                    "<li>Trace your logic on paper for tricky cases.</li>"
                    "<li>Handle inputs carefully with strip().</li></ul>"
                ),
                resources=[
                    {"label": "Python Docs", "url": "https://docs.python.org/3/"},
                    {"label": "Learning Notes (PDF)", "url": "#"},
                ],
            )
            await db.levels.insert_one(level.model_dump())

            # 4 checkpoints
            timestamps = [300, 600, 900, 1200]
            for i in range(4):
                ch = make_challenge(i + 1, f"{stage}-{lvl_num}")
                await db.challenges.insert_one(ch.model_dump())
                cp = Checkpoint(
                    level_id=level.id,
                    order=i + 1,
                    timestamp_seconds=timestamps[i],
                    challenge_id=ch.id,
                )
                await db.checkpoints.insert_one(cp.model_dump())

    # Enroll student
    if not await db.enrollments.find_one({"user_id": student_id, "course_id": course.id}):
        await db.enrollments.insert_one(
            Enrollment(user_id=student_id, course_id=course.id).model_dump()
        )


async def main():
    await db.users.create_index("email", unique=True)
    await db.levels.create_index([("course_id", 1), ("stage", 1), ("level_number", 1)])
    await db.checkpoints.create_index("level_id")
    await db.progress.create_index([("user_id", 1), ("level_id", 1)])

    admin_id = await upsert_user(ADMIN_EMAIL, ADMIN_PASSWORD, "Digipin Admin", "admin")
    student_id = await upsert_user(
        STUDENT_EMAIL, STUDENT_PASSWORD, "Demo Student", "student"
    )
    await seed_course(admin_id, student_id)
    print("Seed complete.")
    print(f"  Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"  Student: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
