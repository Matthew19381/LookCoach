"""Qualitative status for lifestyle checks (sleep, stress, nutrition).

Replaces the invented "X/100" scores (2026-11-02): the point weights (+30 for
7 h, +10 for a silk pillow, ...) had no source, and a single number hid what to
change. A status always comes with the list of reasons behind it.
"""

LABELS = {
    "good": "dobry",
    "needs_improvement": "do poprawy",
    "needs_attention": "wymaga uwagi",
}


def status_from_issues(issue_count: int) -> dict:
    if issue_count <= 0:
        key = "good"
    elif issue_count <= 2:
        key = "needs_improvement"
    else:
        key = "needs_attention"
    return {"status": key, "status_label": LABELS[key]}
