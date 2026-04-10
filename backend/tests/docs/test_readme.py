"""R10 — README completeness gate.

Verifies that the root README.md contains all required sections for
reproducibility and demo readiness.
"""
from pathlib import Path

README_PATH = Path(__file__).parents[3] / "README.md"

REQUIRED_SECTIONS = [
    "project purpose",
    "local setup",
    "how to run",
    "data model",
    "create a profile",
    "create a team",
    "filter",
    "join request",
]


def test_readme_exists():
    assert README_PATH.exists(), f"README.md not found at {README_PATH}"


def test_readme_contains_required_sections():
    content = README_PATH.read_text(encoding="utf-8").lower()
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    assert not missing, f"README is missing required content: {missing}"
