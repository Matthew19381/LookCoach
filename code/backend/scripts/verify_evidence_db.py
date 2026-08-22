"""Verify EVIDENCE_DB integrity rules.

Fails (exit 1) if any entry claims RCT/meta evidence without a real study_url,
or if a claimed URL doesn't look like a PubMed/DOI link.
Run: python -m backend.scripts.verify_evidence_db   (from code/)
"""
import re
import sys

from backend.services.evidence_engine import EVIDENCE_DB

URL_RE = re.compile(r"^https://(pubmed\.ncbi\.nlm\.nih\.gov/\d+/?|doi\.org/10\.\d{4,9}/\S+)$")
STRICT_LEVELS = ("rct", "meta")


def main() -> int:
    errors = []
    for entry in EVIDENCE_DB:
        eid = entry.get("id", "?")
        level = (entry.get("evidence_level") or "").strip().lower()
        url = (entry.get("study_url") or "").strip()

        if level in STRICT_LEVELS and not url:
            errors.append(
                f"{eid}: evidence_level '{entry['evidence_level']}' requires a non-empty "
                f"study_url — downgrade to observational/expert or attach a verified source"
            )
            continue

        if url and not URL_RE.match(url):
            errors.append(f"{eid}: study_url does not look like a verifiable PubMed/DOI link: {url}")

    if errors:
        print("EVIDENCE_DB verification FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    strict = sum(1 for e in EVIDENCE_DB if e["evidence_level"].lower() in STRICT_LEVELS)
    with_url = sum(1 for e in EVIDENCE_DB if e.get("study_url"))
    print(
        f"EVIDENCE_DB OK: {len(EVIDENCE_DB)} entries, "
        f"{strict} RCT/meta (all sourced), {with_url} with study links"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
