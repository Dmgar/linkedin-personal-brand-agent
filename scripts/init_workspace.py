"""
Workspace Initialization Utility for LinkedIn Personal Brand Agent.
Copies all `.example` templates into active local files (ignored by Git) so any
user who clones this repository can immediately customize their own local agent
without exposing personal data or credentials on GitHub.
"""

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

TEMPLATE_MAPPINGS = [
    (".env.example", ".env"),
    ("knowledge/professional-identity.example.md", "knowledge/professional-identity.md"),
    ("knowledge/writing-style.example.md", "knowledge/writing-style.md"),
    ("knowledge/skills.example.md", "knowledge/skills.md"),
    ("content/editorial-calendar.example.md", "content/editorial-calendar.md"),
    ("networking/target-companies.example.md", "networking/target-companies.md"),
    ("networking/opportunities.example.md", "networking/opportunities.md"),
    ("analytics/performance-history.example.csv", "analytics/performance-history.csv"),
]


def init_workspace() -> None:
    print("Initializing local workspace for LinkedIn Personal Brand Agent...\n")
    created_count = 0
    skipped_count = 0

    for src_rel, dst_rel in TEMPLATE_MAPPINGS:
        src = ROOT / src_rel
        dst = ROOT / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            print(f"  [SKIP] {dst_rel} already exists locally.")
            skipped_count += 1
        elif src.exists():
            shutil.copyfile(src, dst)
            print(f"  [CREATE] {dst_rel} (from {src_rel})")
            created_count += 1

    print(
        f"\nDone! Created {created_count} local file(s), kept {skipped_count} existing file(s)."
    )
    print(
        "All personal files are protected by .gitignore and stay strictly on your machine."
    )


if __name__ == "__main__":
    init_workspace()
