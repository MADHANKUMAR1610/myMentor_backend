"""Digipin Academy API — main FastAPI application."""
import io
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from starlette.middleware.cors import CORSMiddleware

from auth import (
    create_access_token,
    get_current_admin,
    get_current_user,
    hash_password,
    verify_password,
)
from database import client, db
from app.utils.executor import execute_code, normalize
from models import (
    Challenge,
    ChallengeCreate,
    Checkpoint,
    CheckpointCreate,
    Course,
    CourseCreate,
    Enrollment,
    Level,
    LevelCreate,
    LevelProgress,
    LoginRequest,
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
    TestCaseResult,
    TokenResponse,
    UserCreate,
    UserPublic,
    gen_id,
    utc_now_iso,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("digipin")

app = FastAPI(title="Digipin Academy API")
api = APIRouter(prefix="/api")


# ---------- Auth ----------
@api.post("/auth/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    if await db.users.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = gen_id()
    doc = {
        "id": user_id,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "name": payload.name,
        "role": payload.role,
        "xp": 0,
        "streak_count": 0,
        "avatar_url": None,
        "created_at": utc_now_iso(),
    }
    await db.users.insert_one(doc)
    public = {k: v for k, v in doc.items() if k not in ("hashed_password", "created_at")}
    token = create_access_token({"sub": user_id, "role": payload.role})
    return TokenResponse(access_token=token, user=UserPublic(**public))


@api.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    public = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "xp": user.get("xp", 0),
        "streak_count": user.get("streak_count", 0),
        "avatar_url": user.get("avatar_url"),
    }
    return TokenResponse(access_token=token, user=UserPublic(**public))


@api.get("/auth/me", response_model=UserPublic)
async def get_me(user: dict = Depends(get_current_user)):
    return UserPublic(**{k: user.get(k) for k in UserPublic.model_fields.keys()})


# ---------- Courses ----------
@api.get("/courses")
async def list_courses(user: dict = Depends(get_current_user)):
    courses = await db.courses.find({}, {"_id": 0}).to_list(500)
    enrollments = await db.enrollments.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).to_list(500)
    enrolled_ids = {e["course_id"] for e in enrollments}
    for c in courses:
        c["is_enrolled"] = c["id"] in enrolled_ids
    return courses


@api.get("/courses/{course_id}")
async def get_course(course_id: str, user: dict = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    levels = await db.levels.find({"course_id": course_id}, {"_id": 0}).to_list(1000)
    levels.sort(key=lambda x: (["Beginner", "Intermediate", "Expert"].index(x["stage"]), x["level_number"]))

    # attach progress
    prog_docs = await db.progress.find(
        {"user_id": user["id"], "course_id": course_id}, {"_id": 0}
    ).to_list(1000)
    prog_by_level = {p["level_id"]: p for p in prog_docs}

    # Determine unlocking: first level unlocked; next unlocks after previous is completed
    prev_completed = True
    for lvl in levels:
        p = prog_by_level.get(lvl["id"])
        lvl["progress"] = p or {"completed": False, "video_watched_seconds": 0, "checkpoints": []}
        lvl["is_unlocked"] = prev_completed
        lvl["is_completed"] = bool(p and p.get("completed"))
        prev_completed = lvl["is_completed"]

    course["levels"] = levels
    return course


@api.post("/courses", response_model=Course)
async def create_course(payload: CourseCreate, _admin: dict = Depends(get_current_admin)):
    course = Course(**payload.model_dump())
    await db.courses.insert_one(course.model_dump())
    return course


@api.post("/courses/{course_id}/enroll")
async def enroll(course_id: str, user: dict = Depends(get_current_user)):
    if await db.enrollments.find_one({"user_id": user["id"], "course_id": course_id}):
        return {"enrolled": True}
    enr = Enrollment(user_id=user["id"], course_id=course_id)
    await db.enrollments.insert_one(enr.model_dump())
    return {"enrolled": True}


# ---------- Levels ----------
@api.get("/levels/{level_id}")
async def get_level(level_id: str, user: dict = Depends(get_current_user)):
    level = await db.levels.find_one({"id": level_id}, {"_id": 0})
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    checkpoints = await db.checkpoints.find(
        {"level_id": level_id}, {"_id": 0}
    ).to_list(20)
    checkpoints.sort(key=lambda c: c["order"])
    challenge_ids = [c["challenge_id"] for c in checkpoints]
    challenges = await db.challenges.find(
        {"id": {"$in": challenge_ids}}, {"_id": 0}
    ).to_list(20)
    ch_by_id = {c["id"]: c for c in challenges}
    for cp in checkpoints:
        # hide hidden test cases & solution from student
        challenge = ch_by_id.get(cp["challenge_id"], {}).copy()
        if user["role"] != "admin":
            challenge.pop("solution", None)
            challenge["test_cases"] = [
                {k: v for k, v in tc.items() if k != "expected_output"} if tc.get("is_hidden") else tc
                for tc in challenge.get("test_cases", [])
            ]
        cp["challenge"] = challenge
    level["checkpoints"] = checkpoints

    progress = await db.progress.find_one(
        {"user_id": user["id"], "level_id": level_id}, {"_id": 0}
    )
    level["progress"] = progress or None
    return level


@api.post("/levels", response_model=Level)
async def create_level(payload: LevelCreate, _admin: dict = Depends(get_current_admin)):
    level = Level(**payload.model_dump())
    await db.levels.insert_one(level.model_dump())
    return level


# ---------- Challenges & Checkpoints ----------
@api.post("/challenges", response_model=Challenge)
async def create_challenge(payload: ChallengeCreate, _admin: dict = Depends(get_current_admin)):
    challenge = Challenge(**payload.model_dump())
    await db.challenges.insert_one(challenge.model_dump())
    return challenge


@api.post("/checkpoints", response_model=Checkpoint)
async def create_checkpoint(payload: CheckpointCreate, _admin: dict = Depends(get_current_admin)):
    cp = Checkpoint(**payload.model_dump())
    await db.checkpoints.insert_one(cp.model_dump())
    return cp


# ---------- Code execution ----------
@api.post("/code/run", response_model=RunResult)
async def run_code(req: RunRequest, _user: dict = Depends(get_current_user)):
    stdout, stderr, ms = await execute_code(req.language, req.source_code, req.stdin or "")
    return RunResult(stdout=stdout, stderr=stderr, time_ms=ms)


@api.post("/code/submit", response_model=SubmissionResult)
async def submit_code(req: SubmissionRequest, user: dict = Depends(get_current_user)):
    challenge = await db.challenges.find_one({"id": req.challenge_id}, {"_id": 0})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    test_cases = challenge.get("test_cases", []) or [
        {"input": "", "expected_output": challenge.get("expected_output", ""), "is_hidden": False}
    ]
    results: List[TestCaseResult] = []
    total_time = 0
    for tc in test_cases:
        stdout, stderr, ms = await execute_code(req.language, req.source_code, tc.get("input", ""))
        total_time += ms
        actual = stdout
        expected = tc["expected_output"]
        passed = normalize(actual) == normalize(expected) and not stderr.strip()
        results.append(
            TestCaseResult(
                input="(hidden)" if tc.get("is_hidden") else tc.get("input", ""),
                expected="(hidden)" if tc.get("is_hidden") else expected,
                actual=actual if not tc.get("is_hidden") else ("passed" if passed else "failed"),
                passed=passed,
                is_hidden=tc.get("is_hidden", False),
            )
        )
    passed_count = sum(1 for r in results if r.passed)
    total = len(results)
    all_passed = passed_count == total
    xp_earned = challenge.get("xp", 0) if all_passed else 0

    # persist submission
    await db.submissions.insert_one(
        {
            "id": gen_id(),
            "user_id": user["id"],
            "challenge_id": req.challenge_id,
            "language": req.language,
            "source_code": req.source_code,
            "passed": all_passed,
            "passed_count": passed_count,
            "total_count": total,
            "time_ms": total_time,
            "created_at": utc_now_iso(),
        }
    )
    return SubmissionResult(
        passed=all_passed,
        stdout="",
        stderr="",
        time_ms=total_time,
        test_results=results,
        passed_count=passed_count,
        total_count=total,
        xp_earned=xp_earned,
    )


# ---------- Progress ----------
@api.post("/progress/checkpoint")
async def complete_checkpoint(
    body: dict, user: dict = Depends(get_current_user)
):
    """body: { level_id, course_id, checkpoint_id, xp_earned }"""
    level_id = body["level_id"]
    course_id = body["course_id"]
    checkpoint_id = body["checkpoint_id"]
    xp = int(body.get("xp_earned", 0))

    prog = await db.progress.find_one({"user_id": user["id"], "level_id": level_id}, {"_id": 0})
    if not prog:
        prog = LevelProgress(
            user_id=user["id"], level_id=level_id, course_id=course_id
        ).model_dump()
    cps = prog.get("checkpoints", [])
    existing = next((c for c in cps if c["checkpoint_id"] == checkpoint_id), None)
    if existing:
        if not existing["completed"]:
            existing["completed"] = True
            existing["completed_at"] = utc_now_iso()
            existing["submissions"] = existing.get("submissions", 0) + 1
            prog["xp_earned"] = prog.get("xp_earned", 0) + xp
    else:
        cps.append(
            {
                "checkpoint_id": checkpoint_id,
                "completed": True,
                "submissions": 1,
                "completed_at": utc_now_iso(),
            }
        )
        prog["xp_earned"] = prog.get("xp_earned", 0) + xp
    prog["checkpoints"] = cps
    prog["updated_at"] = utc_now_iso()
    await db.progress.update_one(
        {"user_id": user["id"], "level_id": level_id},
        {"$set": prog},
        upsert=True,
    )
    if xp:
        await db.users.update_one({"id": user["id"]}, {"$inc": {"xp": xp}})
    return {"ok": True, "progress": prog}


@api.post("/progress/video")
async def update_video_progress(body: dict, user: dict = Depends(get_current_user)):
    """body: { level_id, course_id, watched_seconds }"""
    level_id = body["level_id"]
    course_id = body["course_id"]
    watched = int(body.get("watched_seconds", 0))

    prog = await db.progress.find_one({"user_id": user["id"], "level_id": level_id}, {"_id": 0})
    if not prog:
        prog = LevelProgress(user_id=user["id"], level_id=level_id, course_id=course_id).model_dump()
    prog["video_watched_seconds"] = max(prog.get("video_watched_seconds", 0), watched)

    level = await db.levels.find_one({"id": level_id}, {"_id": 0})
    if level and prog["video_watched_seconds"] >= level.get("video_duration_seconds", 0) - 5:
        prog["video_completed"] = True
    prog["updated_at"] = utc_now_iso()
    await db.progress.update_one(
        {"user_id": user["id"], "level_id": level_id},
        {"$set": prog},
        upsert=True,
    )
    return {"ok": True}


@api.post("/progress/complete-level")
async def complete_level(body: dict, user: dict = Depends(get_current_user)):
    """body: { level_id, course_id }"""
    level_id = body["level_id"]

    level = await db.levels.find_one({"id": level_id}, {"_id": 0})
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    checkpoints = await db.checkpoints.find({"level_id": level_id}, {"_id": 0}).to_list(20)
    cp_ids = {c["id"] for c in checkpoints}

    prog = await db.progress.find_one({"user_id": user["id"], "level_id": level_id}, {"_id": 0})
    if not prog:
        raise HTTPException(status_code=400, detail="No progress yet")

    completed_cps = {c["checkpoint_id"] for c in prog.get("checkpoints", []) if c.get("completed")}
    if not cp_ids.issubset(completed_cps):
        raise HTTPException(status_code=400, detail="Complete all checkpoints first")
    if not prog.get("video_completed"):
        # allow finishing when video watched > 90%
        if prog.get("video_watched_seconds", 0) < level.get("video_duration_seconds", 0) * 0.85:
            raise HTTPException(status_code=400, detail="Watch the full video first")

    prog["completed"] = True
    prog["completed_at"] = utc_now_iso()
    xp_reward = level.get("xp_reward", 100)
    prog["xp_earned"] = prog.get("xp_earned", 0) + xp_reward
    prog["updated_at"] = utc_now_iso()
    await db.progress.update_one(
        {"user_id": user["id"], "level_id": level_id},
        {"$set": prog},
        upsert=True,
    )
    await db.users.update_one(
        {"id": user["id"]},
        {"$inc": {"xp": xp_reward, "streak_count": 1}},
    )
    return {"ok": True, "xp_earned": xp_reward}


@api.get("/progress/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    enrollments = await db.enrollments.find({"user_id": user["id"]}, {"_id": 0}).to_list(100)
    course_ids = [e["course_id"] for e in enrollments]
    courses = await db.courses.find({"id": {"$in": course_ids}}, {"_id": 0}).to_list(100)
    prog_docs = await db.progress.find({"user_id": user["id"]}, {"_id": 0}).to_list(1000)
    prog_by_course = {}
    for p in prog_docs:
        prog_by_course.setdefault(p["course_id"], []).append(p)

    course_summaries = []
    continue_learning = None
    for c in courses:
        levels = await db.levels.find({"course_id": c["id"]}, {"_id": 0}).to_list(200)
        levels.sort(key=lambda x: (["Beginner", "Intermediate", "Expert"].index(x["stage"]), x["level_number"]))
        total = len(levels)
        cprog = prog_by_course.get(c["id"], [])
        completed = sum(1 for p in cprog if p.get("completed"))
        pct = int((completed / total) * 100) if total else 0
        # find next incomplete level in linear order
        next_lvl = None
        for lvl in levels:
            p = next((p for p in cprog if p["level_id"] == lvl["id"]), None)
            if not p or not p.get("completed"):
                next_lvl = lvl
                break
        summary = {
            "course_id": c["id"],
            "title": c["title"],
            "thumbnail_url": c.get("thumbnail_url"),
            "language": c.get("language"),
            "completed_levels": completed,
            "total_levels": total,
            "progress_pct": pct,
            "current_level": next_lvl,
        }
        course_summaries.append(summary)
        if next_lvl and continue_learning is None:
            continue_learning = summary

    recent = sorted(
        [p for p in prog_docs if p.get("completed")],
        key=lambda p: p.get("completed_at", ""),
        reverse=True,
    )[:5]
    recent_levels = []
    for r in recent:
        lvl = await db.levels.find_one({"id": r["level_id"]}, {"_id": 0})
        if lvl:
            recent_levels.append({
                "level_id": lvl["id"], "title": lvl["title"],
                "stage": lvl["stage"], "completed_at": r.get("completed_at"),
            })

    return {
        "user": {
            "name": user["name"],
            "xp": user.get("xp", 0),
            "streak_count": user.get("streak_count", 0),
        },
        "courses": course_summaries,
        "continue_learning": continue_learning,
        "recent_levels": recent_levels,
    }


# ---------- Admin ----------
@api.get("/admin/stats")
async def admin_stats(_admin: dict = Depends(get_current_admin)):
    total_students = await db.users.count_documents({"role": "student"})
    total_courses = await db.courses.count_documents({})
    total_levels = await db.levels.count_documents({})
    total_challenges = await db.challenges.count_documents({})
    completed_levels = await db.progress.count_documents({"completed": True})
    total_submissions = await db.submissions.count_documents({})
    # active last 7 days
    from datetime import timedelta
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_ids = await db.progress.distinct("user_id", {"updated_at": {"$gte": week_ago}})
    return {
        "total_students": total_students,
        "active_students": len(active_ids),
        "total_courses": total_courses,
        "total_levels": total_levels,
        "total_challenges": total_challenges,
        "completed_levels": completed_levels,
        "total_submissions": total_submissions,
        "learning_hours": total_submissions * 5 // 60,  # rough estimate
    }


@api.get("/admin/students")
async def admin_students(_admin: dict = Depends(get_current_admin)):
    users = await db.users.find(
        {"role": "student"},
        {"_id": 0, "hashed_password": 0},
    ).to_list(500)
    for u in users:
        u["completed_levels"] = await db.progress.count_documents(
            {"user_id": u["id"], "completed": True}
        )
    return users


@api.get("/admin/leaderboard")
async def leaderboard(_user: dict = Depends(get_current_user)):
    users = await db.users.find(
        {"role": "student"},
        {"_id": 0, "hashed_password": 0},
    ).sort("xp", -1).limit(20).to_list(20)
    return users


# ---------- Certificate ----------
@api.get("/certificates/{course_id}")
async def download_certificate(course_id: str, user: dict = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    total = await db.levels.count_documents({"course_id": course_id})
    completed = await db.progress.count_documents(
        {"user_id": user["id"], "course_id": course_id, "completed": True}
    )
    if total == 0 or completed < total:
        raise HTTPException(
            status_code=403,
            detail=f"Course not completed ({completed}/{total} levels)",
        )

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    w, h = landscape(A4)
    # background
    c.setFillColorRGB(0.035, 0.035, 0.043)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    # border
    c.setStrokeColorRGB(0.23, 0.51, 0.96)
    c.setLineWidth(3)
    c.rect(30, 30, w - 60, h - 60, fill=0)
    # title
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(w / 2, h - 130, "Certificate of Completion")
    c.setFont("Helvetica", 18)
    c.setFillColorRGB(0.63, 0.63, 0.7)
    c.drawCentredString(w / 2, h - 170, "DIGIPIN ACADEMY")
    # student name
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w / 2, h - 260, user["name"])
    c.setFont("Helvetica", 16)
    c.setFillColorRGB(0.85, 0.85, 0.88)
    c.drawCentredString(
        w / 2, h - 300,
        "has successfully completed the course",
    )
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.23, 0.51, 0.96)
    c.drawCentredString(w / 2, h - 340, course["title"])
    # footer
    c.setFillColorRGB(0.63, 0.63, 0.7)
    c.setFont("Helvetica", 12)
    c.drawString(70, 70, f"Issued: {datetime.now(timezone.utc).strftime('%B %d, %Y')}")
    c.drawRightString(w - 70, 70, "Digipin Academy · https://digipin.academy")
    c.showPage()
    c.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="digipin-certificate-{course_id}.pdf"'
        },
    )


# ---------- Health ----------
@api.get("/")
async def root():
    return {"service": "Digipin Academy API", "status": "ok"}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("Starting Digipin Academy API")
    try:
        # Run seed on startup (idempotent)
        import seed as seed_mod
        await seed_mod.main()
    except Exception as e:
        logger.exception(f"Seed failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    client.close()
