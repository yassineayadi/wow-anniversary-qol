from pathlib import Path

from wa_project.build import build, load_package, validate
from wa_project.codec import decode


def test_build_publishes_import_without_json_source(tmp_path: Path) -> None:
    output = tmp_path / "wa-import.txt"
    package = build(output=output)
    assert output.read_text(encoding="utf-8").startswith("!WA:2!")
    assert decode(output.read_text(encoding="utf-8")) == package


def test_validate_code_defined_package() -> None:
    validate()


def test_package_is_declared_in_code() -> None:
    package = load_package()
    assert package["d"]["desc"] == "Target Debuff Tracker - code-defined"
    assert "wagoID" not in package
    assert "url" not in package["d"]

    package["c"][0]["id"] = "mutated"
    assert load_package()["c"][0]["id"] == "TDT - Judgement of Wisdom"


def test_build_adds_hunter_and_pet_debuffs() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    ids = {child["id"] for child in package["c"]}
    assert {
        "TDT - Expose Weakness",
        "TDT - Blood Frenzy",
    } <= ids
    assert "TDT - Hemorrhage" not in ids
    assert len(package["c"]) == 9


def test_dynamic_group_grows_from_the_center() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    display = package["d"]

    assert display["id"] == "Target Debuff Tracker"
    assert display["regionType"] == "dynamicgroup"
    assert display["grow"] == "HORIZONTAL"
    assert display["align"] == "CENTER"
    assert display["animate"] is True


def test_target_debuffs_only_show_when_missing() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")

    for child in package["c"]:
        trigger = child["triggers"]["1"]["trigger"]
        assert trigger["unit"] == "target"
        assert trigger["matchesShowOn"] == "showOnMissing"

        target_check = child["triggers"]["3"]["trigger"]
        assert target_check["unit"] == "target"
        assert target_check["use_classification"] is True
        assert target_check["classification"] == {"multi": {"worldboss": True}}

        assert child["load"]["use_instance_type"] is True
        assert child["load"]["instance_type"] == {
            "multi": {"3": True, "4": True, "5": True, "6": True, "9": True}
        }

        lock = child["subRegions"][3]
        assert lock["type"] == "subtexture"
        assert lock["textureTexture"] == "Interface\\Icons\\INV_Misc_Lock_01"
        assert lock["textureVisible"] is False

        disabled_condition = child["conditions"][-1]
        assert disabled_condition["check"] == {
            "trigger": 2.0,
            "value": 0.0,
            "variable": "show",
        }
        assert {
            change["property"]: change.get("value")
            for change in disabled_condition["changes"]
        } == {
            "desaturate": True,
            "alpha": 0.25,
            "sub.1.glow": False,
            "sub.4.textureVisible": True,
        }
        assert {
            change["property"]: change.get("value")
            for change in child["conditions"][0]["changes"]
        }["sub.4.textureVisible"] is False

        logic = child["triggers"]["customTriggerLogic"]
        assert "not t[2]" in logic


def test_spec_specific_provider_checks() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    by_id = {child["id"]: child for child in package["c"]}

    expose_trigger = by_id["TDT - Expose Weakness"]["triggers"]["2"]["trigger"]
    assert expose_trigger["class"] == "HUNTER"
    assert expose_trigger["use_specId"] is True
    assert expose_trigger["specId"] == {"multi": {"255": True}}

    blood_frenzy_trigger = by_id["TDT - Blood Frenzy"]["triggers"]["2"]["trigger"]
    assert blood_frenzy_trigger["class"] == "WARRIOR"
    assert blood_frenzy_trigger["use_specId"] is True
    assert blood_frenzy_trigger["specId"] == {"multi": {"71": True}}


def test_sunder_preserves_armor_debuff_exclusivity() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    sunder = next(child for child in package["c"] if child["id"] == "TDT - Sunder Armor")
    assert "t[1] and t[5]" in sunder["triggers"]["customTriggerLogic"]
