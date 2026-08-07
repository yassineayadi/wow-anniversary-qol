from pathlib import Path

from wa_project.build import build, load_package, validate
from wa_project.codec import decode


def _group(package: dict, group_id: str) -> dict:
    return next(group for group in package["c"] if group["d"]["id"] == group_id)


def test_build_publishes_import_without_json_source(tmp_path: Path) -> None:
    output = tmp_path / "wa-import.txt"
    package = build(output=output)
    assert output.read_text(encoding="utf-8").startswith("!WA:2!")
    assert decode(output.read_text(encoding="utf-8")) == package


def test_validate_code_defined_package() -> None:
    validate()


def test_package_is_declared_in_code() -> None:
    package = load_package()
    assert package["d"]["id"] == "WoW Anniversary QoL"
    assert "wagoID" not in package
    assert "url" not in package["d"]

    _group(package, "Target Debuff Tracker")["d"]["id"] = "mutated"
    assert _group(load_package(), "Target Debuff Tracker")["c"][0]["id"] == (
        "TDT - Judgement of Wisdom"
    )


def test_build_adds_hunter_and_pet_debuffs() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    target_group = _group(package, "Target Debuff Tracker")
    ids = {child["id"] for child in target_group["c"]}
    assert {
        "TDT - Expose Weakness",
        "TDT - Blood Frenzy",
    } <= ids
    assert "TDT - Hemorrhage" not in ids
    assert len(target_group["c"]) == 9


def test_dynamic_group_grows_from_the_center() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    display = _group(package, "Target Debuff Tracker")["d"]

    assert display["id"] == "Target Debuff Tracker"
    assert display["regionType"] == "dynamicgroup"
    assert display["grow"] == "HORIZONTAL"
    assert display["align"] == "CENTER"
    assert display["animate"] is True


def test_target_debuffs_only_show_when_missing() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")

    for child in _group(package, "Target Debuff Tracker")["c"]:
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
    target_group = _group(package, "Target Debuff Tracker")
    by_id = {child["id"]: child for child in target_group["c"]}

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
    target_group = _group(package, "Target Debuff Tracker")
    sunder = next(
        child for child in target_group["c"] if child["id"] == "TDT - Sunder Armor"
    )
    assert "t[1] and t[5]" in sunder["triggers"]["customTriggerLogic"]


def test_imported_buff_tracker_is_code_defined() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    buff_group = _group(package, "Tankadin Raid Buffs Tracker")
    ids = {child["id"] for child in buff_group["c"]}

    assert len(buff_group["c"]) == 11
    assert {
        "Blessing of Kings",
        "Blessing of Wisdom",
        "Blessing of Sanctuary",
        "Blessing of Might",
        "Prayer of Fortitude",
        "Mark of the Wild",
        "Arcane Intellect",
        "Divine Spirit",
        "Shadow Protection",
        "Well Fed",
        "Superior Wizard Oil",
    } == ids

    wisdom = next(child for child in buff_group["c"] if child["id"] == "Blessing of Wisdom")
    assert "paladins >= 2" in wisdom["triggers"]["6"]["trigger"]["custom"]

    wizard_oil = next(
        child for child in buff_group["c"] if child["id"] == "Superior Wizard Oil"
    )
    assert wizard_oil["triggers"]["1"]["trigger"]["type"] == "item"
    assert wizard_oil["triggers"]["5"]["trigger"]["matchesShowOn"] == "showOnMissing"


def test_blessings_use_paladin_count_priority() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    buff_group = _group(package, "Tankadin Raid Buffs Tracker")
    blessings = [child for child in buff_group["c"] if child["id"].startswith("Blessing")]

    assert [child["id"] for child in blessings] == [
        "Blessing of Kings",
        "Blessing of Wisdom",
        "Blessing of Sanctuary",
        "Blessing of Might",
    ]
    for minimum, child in enumerate(blessings, start=1):
        count_trigger = child["triggers"]["6"]["trigger"]
        assert f"paladins >= {minimum}" in count_trigger["custom"]
        assert "not t[6]" in child["triggers"]["customTriggerLogic"]
        assert child["subRegions"][4]["type"] == "subtexture"
        assert child["conditions"][-1] == {
            "changes": [
                {"property": "alpha", "value": 0.25},
                {"property": "desaturate", "value": True},
                {"property": "sub.5.textureVisible", "value": True},
            ],
            "check": {"trigger": 6.0, "value": 0.0, "variable": "show"},
        }
