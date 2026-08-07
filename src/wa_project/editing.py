"""Small, deliberately explicit helpers for programmatic aura edits."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


def iter_auras(package: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield the root display and all nested child displays."""

    def walk(node: Any) -> Iterator[dict[str, Any]]:
        if not isinstance(node, dict):
            return
        if "id" in node:
            yield node
        children = node.get("c", [])
        if isinstance(children, list):
            for child in children:
                yield from walk(child)

    yield from walk(package.get("d"))
    children = package.get("c", [])
    if isinstance(children, list):
        for child in children:
            yield from walk(child)


def find_aura(package: dict[str, Any], aura_id: str) -> dict[str, Any]:
    """Return one aura by its WeakAuras `id`, or raise `KeyError`."""

    for aura in iter_auras(package):
        if aura.get("id") == aura_id:
            return aura
    raise KeyError(f"Aura not found: {aura_id}")

