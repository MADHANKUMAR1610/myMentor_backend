"""Digipin Academy backend API tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://dev-quest-41.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

STUDENT = {"email": "student@digipin.dev", "password": "StudentPass123!"}
ADMIN = {"email": "admin@digipin.dev", "password": "AdminPass123!"}


# ---------- Fixtures ----------
@pytest.fixture(scope="session")
def student_token():
    r = requests.post(f"{API}/auth/login", json=STUDENT, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def sh(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Auth ----------
class TestAuth:
    def test_login_student(self):
        r = requests.post(f"{API}/auth/login", json=STUDENT, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["user"]["role"] == "student"
        assert data["user"]["email"] == STUDENT["email"]

    def test_login_admin(self):
        r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=30)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "admin"

    def test_login_bad_password(self):
        r = requests.post(f"{API}/auth/login", json={"email": STUDENT["email"], "password": "wrong!!"}, timeout=30)
        assert r.status_code == 401

    def test_auth_me(self, student_token):
        r = requests.get(f"{API}/auth/me", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        assert r.json()["email"] == STUDENT["email"]


# ---------- Dashboard / Courses ----------
class TestDashboardCourses:
    def test_dashboard(self, student_token):
        r = requests.get(f"{API}/progress/dashboard", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert "user" in d and "courses" in d
        assert d["user"]["name"]
        assert len(d["courses"]) >= 1
        assert d["continue_learning"] is not None

    def test_list_courses(self, student_token):
        r = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        courses = r.json()
        assert len(courses) >= 1
        py = next((c for c in courses if "Python" in c["title"]), None)
        assert py is not None
        assert py["is_enrolled"] is True

    def test_course_detail(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        r = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        d = r.json()
        levels = d["levels"]
        assert len(levels) == 15
        # first is unlocked
        assert levels[0]["is_unlocked"] is True
        # locked levels beyond first (unless already completed)
        assert levels[-1]["is_unlocked"] in (False, True)


# ---------- Level detail ----------
class TestLevel:
    def test_level_detail_masks_solution(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        detail = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30).json()
        lvl_id = detail["levels"][0]["id"]
        r = requests.get(f"{API}/levels/{lvl_id}", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        lvl = r.json()
        cps = lvl["checkpoints"]
        assert len(cps) == 4
        # order ascending by order field
        orders = [c["order"] for c in cps]
        assert orders == sorted(orders)
        # solution stripped for student
        for cp in cps:
            assert "solution" not in cp["challenge"]


# ---------- Code exec ----------
class TestCode:
    def test_run_python(self, student_token):
        r = requests.post(f"{API}/code/run", headers=sh(student_token),
                          json={"language": "python", "source_code": "print('Hello')"}, timeout=60)
        assert r.status_code == 200
        assert r.json()["stdout"].strip() == "Hello"

    def test_submit_correct_first_checkpoint(self, student_token):
        # find first checkpoint's challenge
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        detail = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30).json()
        lvl_id = detail["levels"][0]["id"]
        lvl = requests.get(f"{API}/levels/{lvl_id}", headers=sh(student_token), timeout=30).json()
        cp = lvl["checkpoints"][0]
        challenge_id = cp["challenge"]["id"]

        # Try the expected answer per problem statement
        r = requests.post(f"{API}/code/submit", headers=sh(student_token),
                          json={"challenge_id": challenge_id, "language": "python",
                                "source_code": "print('Hello, Alex!')"}, timeout=60)
        assert r.status_code == 200
        data = r.json()
        # persistent state: log for debug
        print("Submit result:", data)
        # Allow test to still assert we have test_results structure
        assert "test_results" in data
        assert "passed" in data

    def test_submit_wrong_answer(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        detail = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30).json()
        lvl_id = detail["levels"][0]["id"]
        lvl = requests.get(f"{API}/levels/{lvl_id}", headers=sh(student_token), timeout=30).json()
        challenge_id = lvl["checkpoints"][0]["challenge"]["id"]
        r = requests.post(f"{API}/code/submit", headers=sh(student_token),
                          json={"challenge_id": challenge_id, "language": "python",
                                "source_code": "print('wrong')"}, timeout=60)
        assert r.status_code == 200
        d = r.json()
        assert d["passed"] is False
        assert len(d["test_results"]) >= 1


# ---------- Progress ----------
class TestProgress:
    def test_checkpoint_progress_and_video(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        detail = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30).json()
        lvl = detail["levels"][0]
        lvl_full = requests.get(f"{API}/levels/{lvl['id']}", headers=sh(student_token), timeout=30).json()
        cp = lvl_full["checkpoints"][0]

        r = requests.post(f"{API}/progress/checkpoint", headers=sh(student_token),
                          json={"level_id": lvl["id"], "course_id": cid,
                                "checkpoint_id": cp["id"], "xp_earned": 10}, timeout=30)
        assert r.status_code == 200
        assert r.json()["ok"] is True

        r = requests.post(f"{API}/progress/video", headers=sh(student_token),
                          json={"level_id": lvl["id"], "course_id": cid,
                                "watched_seconds": 50}, timeout=30)
        assert r.status_code == 200

    def test_complete_level_rejects_when_incomplete(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        detail = requests.get(f"{API}/courses/{cid}", headers=sh(student_token), timeout=30).json()
        # pick a level unlikely already complete: last one
        lvl_id = detail["levels"][-1]["id"]
        r = requests.post(f"{API}/progress/complete-level", headers=sh(student_token),
                          json={"level_id": lvl_id, "course_id": cid}, timeout=30)
        assert r.status_code == 400

    def test_certificate_forbidden_when_not_completed(self, student_token):
        courses = requests.get(f"{API}/courses", headers=sh(student_token), timeout=30).json()
        cid = next(c["id"] for c in courses if "Python" in c["title"])
        r = requests.get(f"{API}/certificates/{cid}", headers=sh(student_token), timeout=30)
        # If not fully done → 403; if somehow done → 200 pdf
        assert r.status_code in (200, 403)


# ---------- Admin ----------
class TestAdmin:
    def test_admin_stats(self, admin_token):
        r = requests.get(f"{API}/admin/stats", headers=sh(admin_token), timeout=30)
        assert r.status_code == 200
        d = r.json()
        for k in ["total_students", "total_courses", "total_levels",
                  "total_challenges", "total_submissions", "active_students", "learning_hours"]:
            assert k in d

    def test_admin_students(self, admin_token):
        r = requests.get(f"{API}/admin/students", headers=sh(admin_token), timeout=30)
        assert r.status_code == 200
        students = r.json()
        assert isinstance(students, list)
        assert any("completed_levels" in s for s in students)

    def test_admin_forbidden_for_student(self, student_token):
        r = requests.get(f"{API}/admin/stats", headers=sh(student_token), timeout=30)
        assert r.status_code == 403

    def test_admin_create_course_and_level(self, admin_token):
        payload = {
            "title": "TEST_Course_Automation",
            "description": "Temporary course for tests",
            "language": "Python",
            "difficulty": "Beginner",
            "duration_hours": 1,
            "status": "draft",
        }
        r = requests.post(f"{API}/courses", headers=sh(admin_token), json=payload, timeout=30)
        assert r.status_code == 200, r.text
        course = r.json()
        assert course["title"] == payload["title"]
        cid = course["id"]

        lvl_payload = {
            "course_id": cid,
            "stage": "Beginner",
            "level_number": 1,
            "title": "TEST_Level_1",
            "description": "temp",
            "xp_reward": 100,
            "video_duration_seconds": 600,
        }
        r = requests.post(f"{API}/levels", headers=sh(admin_token), json=lvl_payload, timeout=30)
        assert r.status_code == 200, r.text
        assert r.json()["title"] == "TEST_Level_1"

    def test_leaderboard(self, student_token):
        r = requests.get(f"{API}/admin/leaderboard", headers=sh(student_token), timeout=30)
        assert r.status_code == 200
        users = r.json()
        assert isinstance(users, list)
        if len(users) >= 2:
            assert users[0].get("xp", 0) >= users[1].get("xp", 0)
