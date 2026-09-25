import re

SEASONS = {
    "spring": 0,
    "summer": 1,
    "fall": 2,
    "autumn": 2,
    "winter": -1,
    "intersession": -1,
}

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")


def normalize_term(term):
    """
    Casefold and collapse all whitespace.
    """
    return " ".join((term or "").split()).lower()


def parse_term(term):
    """
    A sort key for a free-text term: (year, season_index, normalized).
    """
    normalized = normalize_term(term)
    match = _YEAR.search(normalized)
    year = int(match.group()) if match else -1
    season = next(
        (index for word, index in SEASONS.items() if word in normalized), -2
    )
    return (year, season, normalized)


def default_term(terms):
    """
    The term to show when the user has not picked one: the chronologically latest
    one that exists.
    """
    candidates = [term for term in terms if normalize_term(term)]
    if not candidates:
        return ""
    return max(candidates, key=parse_term)


def available_terms():
    """
    Distinct terms, newest first, de-duplicated by normalized form.
    """
    from courses.models import Course

    seen = {}
    for term in Course.objects.values_list("term", flat=True):
        key = normalize_term(term)
        if key and key not in seen:
            seen[key] = (term or "").strip()
    return sorted(seen.values(), key=parse_term, reverse=True)
