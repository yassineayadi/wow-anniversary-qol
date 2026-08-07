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
    assert display["anchorFrameType"] == "SCREEN"
    assert display["anchorPoint"] == "TOP"
    assert display["xOffset"] == 0.0
    assert display["yOffset"] == -22.0


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

    assert len(buff_group["c"]) == 13
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
        "Scroll of Protection",
        "Scroll of Agility",
        "Superior Wizard Oil",
    } == ids

    wisdom = next(child for child in buff_group["c"] if child["id"] == "Blessing of Wisdom")
    assert "providers >= 2" in wisdom["triggers"]["6"]["trigger"]["custom"]

    wizard_oil = next(
        child for child in buff_group["c"] if child["id"] == "Superior Wizard Oil"
    )
    assert wizard_oil["triggers"]["1"]["trigger"]["type"] == "item"
    assert wizard_oil["triggers"]["5"]["trigger"]["matchesShowOn"] == "showOnMissing"

    for scroll_id, prefix in (
        ("Scroll of Protection", "Scroll of Protection"),
        ("Scroll of Agility", "Scroll of Agility"),
    ):
        scroll = next(child for child in buff_group["c"] if child["id"] == scroll_id)
        assert scroll["triggers"]["1"]["trigger"]["auranames"] == [
            prefix,
            f"{prefix} I",
            f"{prefix} II",
            f"{prefix} III",
            f"{prefix} IV",
            f"{prefix} V",
        ]
        assert "6" not in scroll["triggers"]


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
        assert f"providers >= {minimum}" in count_trigger["custom"]
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


def test_generic_buffs_are_locked_when_no_provider_class_is_present() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    buff_group = _group(package, "Tankadin Raid Buffs Tracker")

    for aura_id, provider_class in {
        "Prayer of Fortitude": "PRIEST",
        "Mark of the Wild": "DRUID",
        "Arcane Intellect": "MAGE",
        "Divine Spirit": "PRIEST",
        "Shadow Protection": "PRIEST",
    }.items():
        child = next(child for child in buff_group["c"] if child["id"] == aura_id)
        provider_trigger = child["triggers"]["6"]["trigger"]
        assert f'classFile == "{provider_class}"' in provider_trigger["custom"]
        assert child["subRegions"][4]["type"] == "subtexture"
        assert child["conditions"][-1]["check"] == {
            "trigger": 6.0,
            "value": 0.0,
            "variable": "show",
        }

    for aura_id in ("Well Fed", "Superior Wizard Oil"):
        child = next(child for child in buff_group["c"] if child["id"] == aura_id)
        assert "6" not in child["triggers"]
        assert all(subregion["type"] != "subtexture" for subregion in child["subRegions"])


def test_target_names_preserve_exact_and_pattern_matching() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    target_group = _group(package, "Target Debuff Tracker")
    by_id = {child["id"]: child for child in target_group["c"]}

    assert by_id["TDT - Hunter's Mark"]["triggers"]["1"]["trigger"]["useName"] is True
    assert "useNamePattern" not in by_id["TDT - Hunter's Mark"]["triggers"]["1"]["trigger"]
    assert by_id["TDT - Faerie Fire"]["triggers"]["1"]["trigger"]["useNamePattern"] is True
    assert by_id["TDT - Expose Weakness"]["triggers"]["1"]["trigger"]["useName"] is True


def test_trackers_share_top_center_layout_and_visual_scale() -> None:
    package = build(output=Path("dist") / "test-wa-import.txt")
    target_group = _group(package, "Target Debuff Tracker")
    buff_group = _group(package, "Tankadin Raid Buffs Tracker")
    target_display = target_group["d"]
    buff_display = buff_group["d"]
    target_child = target_group["c"][0]
    buff_child = buff_group["c"][0]

    assert buff_display["anchorFrameType"] == "SCREEN"
    assert buff_display["anchorPoint"] == "TOP"
    assert buff_display["xOffset"] == 0.0
    assert buff_display["yOffset"] == -70.0
    assert target_display["space"] == buff_display["space"] == 1.0

    assert target_child["width"] == target_child["height"] == 38.0
    assert buff_child["width"] * buff_display["scale"] == 38.25
    assert target_child["subRegions"][0]["glowColor"] == buff_child["subRegions"][2]["glowColor"]
    assert target_child["subRegions"][2]["text_font"] == buff_child["subRegions"][1]["text_font"]
