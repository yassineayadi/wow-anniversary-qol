"""Code-first WeakAuras build pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .codec import decode, encode
from .customize import apply_edits
from .definition import make_package


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "dist" / "wa-import.txt"


def load_package() -> dict[str, Any]:
    """Create a fresh package from the project-owned Python definition."""

    return make_package()


def build(
    output: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Create, customize, encode, and publish a WeakAuras import string."""

    package = apply_edits(load_package())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encode(package) + "\n", encoding="utf-8")
    return package


def inspect_package() -> dict[str, Any]:
    """Return a compact summary of the code-defined package."""

    package = load_package()
    root = package.get("d", {})
    groups = package.get("c", [])
    child_count = sum(
        len(group.get("c", []))
        for group in groups
        if isinstance(group, dict) and isinstance(group.get("c", []), list)
    )
    return {
        "mode": package.get("m", "<missing>"),
        "version": package.get("v", "<missing>"),
        "source": package.get("s", "<missing>"),
        "groups": len(groups) if isinstance(groups, list) else "<not a list>",
        "children": child_count,
        "display id": root.get("id", "<missing>"),
        "display type": root.get("regionType", "<missing>"),
    }


def validate() -> None:
    """Verify the code-defined build pipeline preserves its decoded result."""

    package = apply_edits(load_package())
    rebuilt = decode(encode(package))
    if rebuilt != package:
        raise ValueError("WeakAuras code-first round trip changed the package")
