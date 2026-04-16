from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render

from main.help_content import HELP_TOPICS


def _help_role(user) -> str | None:
    if not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return "admin"
    if getattr(user, "is_professor", False):
        return "professor"
    return "student"


def _allowed_audiences(user) -> list[str]:
    role = _help_role(user)
    if role == "admin":
        return ["student", "professor", "admin"]
    if role == "professor":
        return ["professor"]
    if role == "student":
        return ["student"]
    return []


def _allowed_topics(user) -> list[dict]:
    allowed = set(_allowed_audiences(user))
    return [topic for topic in HELP_TOPICS if topic.get("audience") in allowed]


def _print_guide_context(user) -> dict:
    role = _help_role(user)
    if role == "student":
        return {
            "help_role": role,
            "guide_title": "TA Connect - Student Help Guide",
            "guide_summary": "Printable version of the student workflows. Use your browser Print dialog to save as PDF.",
            "topics": [t for t in HELP_TOPICS if t.get("audience") == "student"],
        }
    if role == "professor":
        return {
            "help_role": role,
            "guide_title": "TA Connect - Professor Help Guide",
            "guide_summary": "Printable version of the professor workflows for staffing, applications, offers, and evaluations.",
            "topics": [t for t in HELP_TOPICS if t.get("audience") == "professor"],
        }
    if role == "admin":
        return {
            "help_role": role,
            "guide_title": "TA Connect - Admin Help Guide",
            "guide_summary": "Printable admin guide with workflows for students, professors, and admins.",
            "topics": [t for t in HELP_TOPICS if t.get("audience") in {"student", "professor", "admin"}],
        }
    return {
        "help_role": None,
        "guide_title": "TA Connect - Help Guide",
        "guide_summary": "Printable help guide.",
        "topics": [],
    }


@login_required
def help_home(request):
    role = _help_role(request.user)
    topics = _allowed_topics(request.user)
    return render(
        request,
        "help/help_home.html",
        {
            "help_role": role,
            "is_student_help_user": role == "student",
            "topics": topics,
        },
    )


@login_required
def help_print(request):
    return render(
        request,
        "help/help_print.html",
        _print_guide_context(request.user),
    )


@login_required
def help_students_print(request):
    if _help_role(request.user) != "student":
        return HttpResponseForbidden("Student help is restricted.")
    return help_print(request)


@login_required
def help_student_topic(request, topic_id: str):
    topics = _allowed_topics(request.user)

    topic = next((t for t in topics if t.get("id") == topic_id), None)
    if topic is None:
        raise Http404("Help topic not found.")

    return render(
        request,
        "help/help_student_topic.html",
        {
            "topic": topic,
            "topics": topics,
            "help_role": _help_role(request.user),
        },
    )


@login_required
def help_students_search(request):
    topics = _allowed_topics(request.user)

    raw_q = (request.GET.get("q") or "").strip()
    q = raw_q.lower()

    if not q:
        matched_topics = topics
    else:
        def _haystack(topic: dict) -> str:
            parts = [
                topic.get("audience", ""),
                topic.get("title", ""),
                topic.get("summary", ""),
                " ".join(topic.get("prerequisites", []) or []),
                " ".join(topic.get("steps", []) or []),
                " ".join(topic.get("what_to_know", []) or []),
                " ".join(topic.get("troubleshooting", []) or []),
            ]
            return " ".join(parts).lower()

        matched_topics = [
            t for t in topics if q in _haystack(t)
        ]

    return render(
        request,
        "help/help_students_search.html",
        {
            "query": raw_q,
            "topics": matched_topics,
            "help_role": _help_role(request.user),
        },
    )

