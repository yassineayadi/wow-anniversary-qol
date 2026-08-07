"""Project-owned WeakAuras edits for the target debuff tracker."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha1
from typing import Any


RAID_DPS_DEBUFFS = (
    ("Expose Weakness", 132212, "HUNTER", (255,)),  # Survival
    ("Blood Frenzy", 132334, "WARRIOR", (71,)),  # Arms
)

PROVIDER_SPEC_IDS = {
    "Expose Weakness": (255,),  # Survival Hunter
    "Blood Frenzy": (71,),  # Arms Warrior
}

RAID_DIFFICULTY_IDS = ("3", "4", "5", "6", "9")
LOCK_TEXTURE = "Interface\\Icons\\INV_Misc_Lock_01"


def _stable_uid(aura_name: str) -> str:
    """Create a repeatable WeakAuras UID for a generated child."""

    return sha1(f"wow-wa-project:{aura_name}".encode("utf-8")).hexdigest()[:10]


def _configure_target_trigger(
    aura: dict[str, Any],
    aura_name: str,
    *,
    name_pattern: bool = False,
) -> None:
    trigger = aura["triggers"]["1"]["trigger"]
    trigger["auranames"] = [aura_name]
    trigger["matchesShowOn"] = "showOnMissing"
    if name_pattern:
        trigger["namePattern_name"] = aura_name
        trigger["namePattern_operator"] = "find('%s')"
        trigger["useName"] = False
        trigger["useNamePattern"] = True
    else:
        trigger.pop("namePattern_name", None)
        trigger.pop("namePattern_operator", None)
        trigger.pop("useNamePattern", None)
        trigger["useName"] = True


def _configure_provider_trigger(
    aura: dict[str, Any],
    class_name: str,
    spec_ids: tuple[int, ...] = (),
) -> None:
    trigger = aura["triggers"]["2"]["trigger"]
    trigger["class"] = class_name
    trigger["use_class"] = True
    if spec_ids:
        trigger["specId"] = {"multi": {str(spec_id): True for spec_id in spec_ids}}
        trigger["use_specId"] = True
    else:
        trigger.pop("specId", None)
        trigger.pop("use_specId", None)


def _configure_raid_boss_target(aura: dict[str, Any]) -> None:
    trigger = aura["triggers"]["3"]["trigger"]
    trigger["classification"] = {"multi": {"worldboss": True}}
    trigger["use_classification"] = True

    load = aura.setdefault("load", {})
    load["instance_type"] = {
        "multi": {difficulty_id: True for difficulty_id in RAID_DIFFICULTY_IDS}
    }
    load["use_instance_type"] = True


def _configure_dynamic_group(package: dict[str, Any]) -> None:
    """Make visible children expand and collapse from the group's center."""

    display = package.setdefault("d", {})
    if display.get("regionType") != "dynamicgroup":
        return

    display["grow"] = "HORIZONTAL"
    display["align"] = "CENTER"
    display["animate"] = True


def _configure_activation_logic(aura: dict[str, Any]) -> None:
    """Show alerts when missing, or a disabled icon when no provider exists."""

    if "5" in aura["triggers"]:
        aura["triggers"]["customTriggerLogic"] = """function(t)
    return t[3] and t[4] and (not t[2] or (t[1] and t[5]))
end"""
    else:
        aura["triggers"]["customTriggerLogic"] = """function(t)
    return t[3] and t[4] and (not t[2] or t[1])
end"""


def _configure_lock_overlay(aura: dict[str, Any]) -> int:
    """Add a centered lock texture and return its one-based subregion index."""

    subregions = aura.setdefault("subRegions", [])
    for index, subregion in enumerate(subregions, start=1):
        if (
            subregion.get("type") == "subtexture"
            and subregion.get("textureTexture") == LOCK_TEXTURE
        ):
            return index

    subregions.append(
        {
            "type": "subtexture",
            "textureVisible": False,
            "textureTexture": LOCK_TEXTURE,
            "textureDesaturate": False,
            "textureColor": [1.0, 1.0, 1.0, 1.0],
            "textureBlendMode": "BLEND",
            "textureMirror": False,
            "textureRotate": False,
            "textureRotation": 0.0,
            "anchor_mode": "point",
            "self_point": "CENTER",
            "anchor_point": "CENTER",
            "width": 18.0,
            "height": 18.0,
            "scale": 1.0,
            "mirror": False,
            "rotate": False,
            "xOffset": 0.0,
            "yOffset": 0.0,
        }
    )
    return len(subregions)


def _configure_conditions(aura: dict[str, Any], lock_subregion: int) -> None:
    """Preserve the missing alert and dim icons without an available provider."""

    conditions = aura.setdefault("conditions", [])
    lock_property = f"sub.{lock_subregion}.textureVisible"
    missing_check = {"trigger": 1.0, "value": 0.0, "variable": "buffed"}
    for condition in conditions:
        if condition.get("check") == missing_check and not any(
            change.get("property") == lock_property
            for change in condition.get("changes", [])
        ):
            condition.setdefault("changes", []).append(
                {"property": lock_property, "value": False}
            )

    disabled_condition = {
        "changes": [
            {"property": "desaturate", "value": True},
            {"property": "alpha", "value": 0.25},
            {"property": "sub.1.glow", "value": False},
            {"property": lock_property, "value": True},
        ],
        "check": {"trigger": 2.0, "value": 0.0, "variable": "show"},
    }
    if not any(
        condition.get("check") == disabled_condition["check"]
        for condition in conditions
    ):
        conditions.append(disabled_condition)


def _add_debuff(
    package: dict[str, Any],
    template: dict[str, Any],
    aura_name: str,
    icon: int,
    class_name: str,
    spec_ids: tuple[int, ...] = (),
) -> None:
    aura_id = f"TDT - {aura_name}"
    existing_ids = {child.get("id") for child in package.get("c", [])}
    if aura_id in existing_ids:
        return

    child = deepcopy(template)
    child["id"] = aura_id
    child["uid"] = _stable_uid(aura_name)
    child["displayIcon"] = icon
    _configure_target_trigger(child, aura_name)
    _configure_raid_boss_target(child)
    _configure_provider_trigger(child, class_name, spec_ids)
    _configure_activation_logic(child)
    lock_subregion = _configure_lock_overlay(child)
    _configure_conditions(child, lock_subregion)
    for key in ("wagoID", "url", "version", "semver"):
        child.pop(key, None)
    package.setdefault("c", []).append(child)


def _target_group(package: dict[str, Any]) -> dict[str, Any]:
    """Find the nested target-debuff group in the published package."""

    for child in package.get("c", []):
        if child.get("d", {}).get("id") == "Target Debuff Tracker":
            return child
    raise KeyError("Target Debuff Tracker group is missing from the package")


def apply_edits(package: dict[str, Any]) -> dict[str, Any]:
    """Apply project edits and return the package to publish.

    The code-defined package tracks the major raid armor debuffs plus Hunter's
    Mark. Add only raid DPS amplification debuffs that materially affect a
    hunter's physical damage: Expose Weakness and Blood Frenzy.
    """

    target_group = _target_group(package)
    _configure_dynamic_group(target_group)
    children = target_group.get("c", [])
    for child in children:
        if child.get("id", "").startswith("TDT - "):
            trigger = child.get("triggers", {}).get("1", {}).get("trigger", {})
            aura_names = trigger.get("auranames", [])
            if aura_names:
                _configure_target_trigger(
                    child,
                    aura_names[0],
                    name_pattern=bool(trigger.get("useNamePattern")),
                )
                _configure_raid_boss_target(child)
                _configure_activation_logic(child)
                lock_subregion = _configure_lock_overlay(child)
                _configure_conditions(child, lock_subregion)
                provider_spec_ids = PROVIDER_SPEC_IDS.get(aura_names[0], ())
                provider_trigger = child.get("triggers", {}).get("2", {}).get("trigger", {})
                if provider_trigger.get("class"):
                    _configure_provider_trigger(
                        child,
                        provider_trigger["class"],
                        provider_spec_ids,
                    )

    template = next(
        child for child in children if child.get("id") == "TDT - Hunter's Mark"
    )
    for aura_name, icon, class_name, spec_ids in RAID_DPS_DEBUFFS:
        _add_debuff(target_group, template, aura_name, icon, class_name, spec_ids)
    return package
