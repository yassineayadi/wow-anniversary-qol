from pathlib import Path

from wa_project.publish import ADDON_NAME, publish


def test_publish_generates_companion_addon(tmp_path: Path) -> None:
    result = publish(addon_root=tmp_path / "Interface" / "AddOns")
    addon_dir = tmp_path / "Interface" / "AddOns" / ADDON_NAME

    assert result["addon_dir"] == addon_dir
    assert len(result["build_id"]) == 12
    assert (addon_dir / f"{ADDON_NAME}.toc").read_text(encoding="utf-8").__contains__(
        "## Dependencies: WeakAuras"
    )

    lua = (addon_dir / f"{ADDON_NAME}.lua").read_text(encoding="utf-8")
    assert "!WA:2!" in lua
    assert "WeakAuras.ImportString" in lua
    assert "/waqol update" in lua
