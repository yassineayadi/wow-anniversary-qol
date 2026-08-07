from pathlib import Path

import pytest


@pytest.fixture
def sample_import() -> str:
    return (Path(__file__).parents[1] / "imports" / "basis.wago").read_text(encoding="utf-8")

