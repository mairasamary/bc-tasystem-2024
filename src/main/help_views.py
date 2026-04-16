from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render

from main.help_content import HELP_TOPICS

import re
from difflib import SequenceMatcher


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

    def _normalize_text(s: str) -> str:
        s = (s or "").lower()
        s = re.sub(r"[^a-z0-9\s]+", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _tokens(s: str) -> set[str]:
        s = _normalize_text(s)
        if not s:
            return set()
        toks = [t for t in s.split(" ") if len(t) >= 2]
        # tiny stopword set just to reduce noise in overlap scoring
        stop = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "your"}
        return {t for t in toks if t not in stop}

    def _expand_query_terms(q_raw: str) -> str:
        """
        Lightweight synonym/alias expansion for common help-center phrasing.
        Keep this small and safe: add only terms that are near-equivalent in-app.
        """
        base = _normalize_text(q_raw)
        if not base:
            return ""
        synonyms = {
            "sign up": "welcome",
            "signup": "welcome",
            "get started": "welcome",
            "set up": "getting started profile",
            "setup": "getting started profile",
            "log in": "sign in",
            "login": "sign in",
            "ta": "teaching assistant",
            "hire": "offer",
        }
        expanded = [base]
        for k, v in synonyms.items():
            if k in base:
                expanded.append(v)
        return " ".join(expanded)

    def _sequence_ratio(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    def _topic_fields(topic: dict) -> dict[str, str]:
        return {
            "title": topic.get("title", "") or "",
            "summary": topic.get("summary", "") or "",
            "prerequisites": " ".join(topic.get("prerequisites", []) or []),
            "steps": " ".join(topic.get("steps", []) or []),
            "what_to_know": " ".join(topic.get("what_to_know", []) or []),
            "troubleshooting": " ".join(topic.get("troubleshooting", []) or []),
        }

    def _score_topic(topic: dict, query_raw: str) -> float:
        """
        Score relevance for a help topic. Higher is better.

        Goals:
        - Let partial / out-of-order matches rank well ("resume upload" should match profile setup).
        - Prefer title/summary matches over deep body matches.
        - Still allow broad matches in steps/troubleshooting.
        """
        fields = _topic_fields(topic)

        q_expanded = _expand_query_terms(query_raw)
        q_norm = _normalize_text(q_expanded)
        q_toks = _tokens(q_expanded)
        if not q_norm:
            return 0.0

        title = _normalize_text(fields["title"])
        summary = _normalize_text(fields["summary"])
        steps = _normalize_text(fields["steps"])
        prereq = _normalize_text(fields["prerequisites"])
        what_to_know = _normalize_text(fields["what_to_know"])
        troubleshooting = _normalize_text(fields["troubleshooting"])
        all_text = " ".join([title, summary, prereq, steps, what_to_know, troubleshooting]).strip()

        # Fast path: exact substring hits get a strong boost.
        score = 0.0
        if q_norm in title:
            score += 120
        if q_norm in summary:
            score += 80
        if q_norm and q_norm in all_text:
            score += 40

        # Token overlap: rewards out-of-order matches.
        if q_toks:
            all_toks = _tokens(all_text)
            overlap = len(q_toks & all_toks)
            coverage = overlap / max(1, len(q_toks))
            score += coverage * 90
            if coverage >= 0.85:
                score += 15

        # Fuzzy similarity: compare query to title + summary primarily.
        score += _sequence_ratio(q_norm, title) * 70
        score += _sequence_ratio(q_norm, summary) * 45
        score += _sequence_ratio(q_norm, all_text) * 20

        # Small preference: shorter, more “direct” articles win ties.
        score -= len(all_text) / 2000.0

        return score

    def _search_topics(topics_in: list[dict], query_raw: str) -> list[dict]:
        scored: list[tuple[float, dict]] = []
        for t in topics_in:
            s = _score_topic(t, query_raw)
            if s > 15:
                scored.append((s, t))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    if not q:
        matched_topics = topics
    else:
        matched_topics = _search_topics(topics, raw_q)

    return render(
        request,
        "help/help_students_search.html",
        {
            "query": raw_q,
            "topics": matched_topics,
            "help_role": _help_role(request.user),
        },
    )

