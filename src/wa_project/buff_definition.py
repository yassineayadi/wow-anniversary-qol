"""Code-defined Tankadin Raid Buffs Tracker group."""

from __future__ import annotations

from typing import Any


_NOOP_ANIMATION = {
    "duration_type": "seconds",
    "easeStrength": 3.0,
    "easeType": "none",
    "type": "none",
}


# The first N entries are the blessings expected when N Paladins are present.
BLESSING_PRIORITY = (
    ("Blessing of Kings", 1),
    ("Blessing of Wisdom", 2),
    ("Blessing of Sanctuary", 3),
    ("Blessing of Might", 4),
)


def _animation() -> dict[str, dict[str, Any]]:
    return {
        "finish": dict(_NOOP_ANIMATION),
        "main": dict(_NOOP_ANIMATION),
        "start": {**_NOOP_ANIMATION, "preset": "shrink", "type": "preset"},
    }


def _load(*, wisdom: bool = False, wizard_oil: bool = False) -> dict[str, Any]:
    class_load = {"multi": {"PALADIN": True}, "single": "PALADIN"}

    load: dict[str, Any] = {
        "class": class_load,
        "ingroup": {"multi": {"raid": True}, "single": "raid"},
        "size": {
            "multi": {"ten": True, "twenty": True, "twentyfive": True},
            "single": "ten",
        },
        "spec": {"multi": []},
        "talent": {"multi": []},
        "use_ingroup": False,
        "use_size": False,
        "zoneIds": "",
    }
    if wisdom:
        load.update(
            {
                "role": {"multi": {"HEALER": True, "TANK": True}},
                "use_role": False,
                "use_never": False,
            }
        )
    load["use_class"] = True
    return load


def _aura_trigger(
    names: list[str],
    remaining: int,
    operator: str,
    *,
    missing: bool = False,
) -> dict[str, Any]:
    trigger: dict[str, Any] = {
        "auranames": names,
        "auraspellids": [],
        "debuffType": "HELPFUL",
        "event": "Health",
        "names": [],
        "rem": str(remaining),
        "remOperator": operator,
        "spellIds": [],
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
        "type": "aura2",
        "unit": "player",
        "useExactSpellId": False,
        "useName": True,
        "useRem": True,
        "useTotal": False,
    }
    if missing:
        trigger["matchesShowOn"] = "showOnMissing"
    return trigger


def _item_trigger(
    names: list[str],
    enchant: str,
    remaining: int,
    operator: str,
    *,
    missing: bool = False,
) -> dict[str, Any]:
    trigger = {
        "auranames": names,
        "auraspellids": [],
        "debuffType": "HELPFUL",
        "enchant": enchant,
        "event": "Weapon Enchant",
        "genericShowOn": "showOnCooldown",
        "namePattern_name": "Wizard Oil",
        "namePattern_operator": "find('%s')",
        "names": [],
        "rem": str(remaining),
        "remOperator": operator,
        "remaining": str(remaining),
        "remaining_operator": operator,
        "showOn": "showOnMissing" if missing else "showOnActive",
        "spellIds": [],
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
        "type": "item",
        "unit": "player",
        "useExactSpellId": False,
        "useName": False,
        "useNamePattern": not missing,
        "useRem": True,
        "useTotal": False,
        "use_enchant": True,
        "use_genericShowOn": True,
        "use_itemName": True,
        "use_remaining": True,
        "use_showOn": True,
        "use_weapon": True,
        "weapon": "main",
    }
    if missing:
        trigger["matchesShowOn"] = "showOnMissing"
    return trigger


def _paladin_count_trigger(minimum: int) -> dict[str, Any]:
    return {
        "check": "event",
        "custom": f"""function()
    if not IsInRaid() then
        return false
    end

    local paladins = 0

    for i = 1, MAX_RAID_MEMBERS do
        local _, _, _, _, _, classFile = GetRaidRosterInfo(i)

        if classFile == "PALADIN" then
            paladins = paladins + 1
        end
    end

    return paladins >= {minimum}
end""",
        "custom_type": "status",
        "debuffType": "HELPFUL",
        "events": "GROUP_ROSTER_UPDATE PLAYER_ENTERING_WORLD",
        "type": "custom",
        "unit": "player",
    }


def _standard_triggers(
    names: list[str],
    *,
    minimum_paladins: int | None = None,
) -> dict[str, Any]:
    triggers: dict[str, Any] = {
        "activeTriggerMode": -10.0,
        "customTriggerLogic": "\n\n",
        "disjunctive": "any",
    }
    for number, (remaining, operator) in enumerate(
        ((600, ">"), (600, "<="), (300, "<="), (60, "<=")),
        start=1,
    ):
        triggers[str(number)] = {
            "trigger": _aura_trigger(names, remaining, operator),
            "untrigger": [],
        }
    triggers["5"] = {
        "trigger": _aura_trigger(names, 60, ">", missing=True),
        "untrigger": [],
    }
    if minimum_paladins is not None:
        triggers["6"] = {
            "trigger": _paladin_count_trigger(minimum_paladins),
            "untrigger": [],
        }
        triggers["customTriggerLogic"] = """function(t)
    return not t[6] or t[1] or t[2] or t[3] or t[4] or t[5]
end"""
    return triggers


def _subregions() -> list[dict[str, Any]]:
    return [
        {"type": "subbackground"},
        {
            "anchorXOffset": 0.0,
            "anchorYOffset": 0.0,
            "anchor_point": "CENTER",
            "rotateText": "NONE",
            "text_anchorXOffset": 0.0,
            "text_anchorYOffset": 0.0,
            "text_automaticWidth": "Auto",
            "text_color": [1.0, 1.0, 1.0, 1.0],
            "text_fixedWidth": 64.0,
            "text_font": "Friz Quadrata TT",
            "text_fontSize": 14.0,
            "text_fontType": "OUTLINE",
            "text_justify": "CENTER",
            "text_selfPoint": "CENTER",
            "text_shadowColor": [0.0, 0.0, 0.0, 1.0],
            "text_shadowXOffset": 0.0,
            "text_shadowYOffset": 0.0,
            "text_text": "%p",
            "text_text_format_p_format": "timed",
            "text_text_format_p_time_dynamic_threshold": 60.0,
            "text_text_format_p_time_format": 1.0,
            "text_text_format_p_time_legacy_floor": False,
            "text_text_format_p_time_mod_rate": True,
            "text_text_format_p_time_precision": 1.0,
            "text_text_format_s_format": "none",
            "text_visible": False,
            "text_wordWrap": "WordWrap",
            "type": "subtext",
        },
        {
            "glow": False,
            "glowBorder": False,
            "glowColor": [1.0, 0.0, 0.12941176470588, 1.0],
            "glowDuration": 1.0,
            "glowFrequency": 0.25,
            "glowLength": 10.0,
            "glowLines": 8.0,
            "glowScale": 1.0,
            "glowThickness": 1.0,
            "glowType": "buttonOverlay",
            "glowXOffset": 0.0,
            "glowYOffset": 0.0,
            "type": "subglow",
            "useGlowColor": True,
        },
        {
            "glow": False,
            "glowBorder": False,
            "glowColor": [1.0, 0.0, 0.12941176470588, 1.0],
            "glowDuration": 1.0,
            "glowFrequency": 0.25,
            "glowLength": 10.0,
            "glowLines": 8.0,
            "glowScale": 1.0,
            "glowThickness": 1.0,
            "glowType": "buttonOverlay",
            "glowXOffset": 0.0,
            "glowYOffset": 0.0,
            "type": "subglow",
            "useGlowColor": False,
        },
    ]


def _lock_subregion() -> dict[str, Any]:
    return {
        "type": "subtexture",
        "textureVisible": False,
        "textureTexture": "Interface\\Icons\\INV_Misc_Lock_01",
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


def _conditions(lock_subregion: int | None = None) -> list[dict[str, Any]]:
    conditions = [
        {
            "changes": [
                {"property": "alpha", "value": 0.5},
                {"property": "sub.3.glow", "value": True},
                {"property": "desaturate", "value": True},
            ],
            "check": {"trigger": 5.0, "value": 1.0, "variable": "show"},
        },
        {
            "changes": [
                {"property": "alpha", "value": 1.0},
                {"property": "sub.4.glow", "value": True},
                {"property": "sub.3.glow", "value": True},
                {"property": "sub.2.text_visible", "value": True},
            ],
            "check": {"trigger": 4.0, "value": 1.0, "variable": "show"},
            "linked": True,
        },
        {
            "changes": [
                {"property": "alpha", "value": 0.75},
                {"property": "sub.4.glow", "value": True},
                {"property": "sub.3.glow"},
                {"property": "sub.2.text_visible", "value": True},
            ],
            "check": {"trigger": 3.0, "value": 1.0, "variable": "show"},
            "linked": True,
        },
        {
            "changes": [
                {"property": "alpha", "value": 0.25},
                {"property": "sub.3.glow"},
                {"property": "sub.4.glow"},
                {"property": "sub.2.text_visible"},
            ],
            "check": {"trigger": 2.0, "value": 1.0, "variable": "show"},
            "linked": True,
        },
        {
            "changes": [
                {"property": "alpha"},
                {"property": "sub.3.glow"},
                {"property": "sub.4.glow"},
                {"property": "sub.2.text_visible"},
            ],
            "check": {"trigger": 1.0, "value": 1.0, "variable": "show"},
            "linked": True,
        },
    ]

    if lock_subregion is not None:
        lock_property = f"sub.{lock_subregion}.textureVisible"
        for condition in conditions:
            condition["changes"].append(
                {"property": lock_property, "value": False}
            )
        conditions.append(
            {
                "changes": [
                    {"property": "alpha", "value": 0.25},
                    {"property": "desaturate", "value": True},
                    {"property": lock_property, "value": True},
                ],
                "check": {"trigger": 6.0, "value": 0.0, "variable": "show"},
            }
        )
    return conditions


def _child(
    *,
    aura_id: str,
    uid: str,
    icon: int | str,
    names: list[str],
    minimum_paladins: int | None = None,
) -> dict[str, Any]:
    return {
        "actions": {"finish": [], "init": {"do_custom": False}, "start": []},
        "alpha": 1.0,
        "anchorFrameType": "SCREEN",
        "anchorPoint": "CENTER",
        "animation": _animation(),
        "authorOptions": [],
        "color": [1.0, 1.0, 1.0, 1.0],
        "config": [],
        "conditions": _conditions(lock_subregion=5)
        if minimum_paladins is not None
        else _conditions(),
        "cooldown": False,
        "cooldownEdge": False,
        "cooldownSwipe": False,
        "cooldownTextDisabled": False,
        "desaturate": False,
        "displayIcon": icon,
        "frameStrata": 1.0,
        "height": 45.0,
        "icon": True,
        "iconSource": 0.0,
        "id": aura_id,
        "information": {
            "forceEvents": True,
            "ignoreOptionsEventErrors": True,
            "showNilIsFalse": True,
        },
        "internalVersion": 90.0,
        "inverse": False,
        "keepAspectRatio": False,
        "load": _load(),
        "regionType": "icon",
        "selfPoint": "CENTER",
        "subRegions": [*_subregions(), _lock_subregion()]
        if minimum_paladins is not None
        else _subregions(),
        "tocversion": 20506,
        "triggers": _standard_triggers(names, minimum_paladins=minimum_paladins),
        "uid": uid,
        "version": 3.0,
        "width": 45.0,
        "xOffset": 0.0,
        "yOffset": 0.0,
        "zoom": 0.0,
    }


def _wizard_oil() -> dict[str, Any]:
    names = ["Wizard Oil"]
    triggers: dict[str, Any] = {
        "activeTriggerMode": -10.0,
        "customTriggerLogic": "\n\n",
        "disjunctive": "any",
        "1": {
            "trigger": _item_trigger(
                ["Minor Wizard Oil", "Lesser Wizard Oil", "Wizard Oil"],
                "Brilliant Wizard Oil",
                600,
                ">",
            ),
            "untrigger": [],
        },
        "2": {
            "trigger": _item_trigger(names, "Wizard Oil", 600, "<="),
            "untrigger": [],
        },
        "3": {
            "trigger": _item_trigger(names, "Superior Wizard Oil", 300, "<="),
            "untrigger": [],
        },
        "4": {
            "trigger": _item_trigger(names, "Superior Wizard Oil", 60, "<="),
            "untrigger": [],
        },
        "5": {
            "trigger": _item_trigger(
                [
                    "Minor Wizard Oil",
                    "Lesser Wizard Oil",
                    "Wizard Oil",
                    "Brilliant Wizard Oil",
                ],
                "Superior Wizard Oil",
                60,
                ">",
                missing=True,
            ),
            "untrigger": [],
        },
    }
    return {
        "actions": {"finish": [], "init": {"do_custom": False}, "start": []},
        "alpha": 1.0,
        "anchorFrameType": "SCREEN",
        "anchorPoint": "CENTER",
        "animation": _animation(),
        "authorOptions": [],
        "color": [1.0, 1.0, 1.0, 1.0],
        "config": [],
        "conditions": _conditions(),
        "cooldown": False,
        "cooldownEdge": False,
        "cooldownSwipe": False,
        "cooldownTextDisabled": False,
        "desaturate": False,
        "displayIcon": "134767",
        "frameStrata": 1.0,
        "height": 45.0,
        "icon": True,
        "iconSource": 0.0,
        "id": "Superior Wizard Oil",
        "information": {
            "forceEvents": True,
            "ignoreOptionsEventErrors": True,
            "showNilIsFalse": True,
        },
        "internalVersion": 90.0,
        "inverse": False,
        "keepAspectRatio": False,
        "load": _load(wizard_oil=True),
        "regionType": "icon",
        "selfPoint": "CENTER",
        "subRegions": _subregions(),
        "tocversion": 20506,
        "triggers": triggers,
        "uid": "X1)YxUxDeTx",
        "version": 3.0,
        "width": 45.0,
        "xOffset": 0.0,
        "yOffset": 0.0,
        "zoom": 0.0,
    }


def _buff_group() -> dict[str, Any]:
    minimum_paladins = dict(BLESSING_PRIORITY)
    children = [
        _child(
            aura_id="Blessing of Kings",
            uid="xd8MKWVWNCn",
            icon=135993,
            names=["Greater Blessing of Kings", "Blessing of Kings"],
            minimum_paladins=minimum_paladins["Blessing of Kings"],
        ),
        _child(
            aura_id="Blessing of Wisdom",
            uid="rslA2SaZdJD",
            icon=135912,
            names=["Greater Blessing of Wisdom", "Blessing of Wisdom"],
            minimum_paladins=minimum_paladins["Blessing of Wisdom"],
        ),
        _child(
            aura_id="Blessing of Sanctuary",
            uid="1AcFf)aZWMg",
            icon="Interface\\Icons\\Spell_Holy_GreaterBlessingofSanctuary",
            names=["Greater Blessing of Sanctuary", "Blessing of Sanctuary"],
            minimum_paladins=minimum_paladins["Blessing of Sanctuary"],
        ),
        _child(
            aura_id="Blessing of Might",
            uid="MK)EVfLab4k",
            icon=135908,
            names=["Greater Blessing of Might", "Blessing of Might"],
            minimum_paladins=minimum_paladins["Blessing of Might"],
        ),
        _child(
            aura_id="Prayer of Fortitude",
            uid="7AkfkGaf5L1",
            icon="135941",
            names=["Prayer of Fortitude", "Power Word: Fortitude"],
        ),
        _child(
            aura_id="Mark of the Wild",
            uid="PORpl7QvaKs",
            icon=136038,
            names=["Gift of the Wild", "Mark of the Wild"],
        ),
        _child(
            aura_id="Arcane Intellect",
            uid="BzmrReW24L)",
            icon=135869,
            names=["Arcane Brilliance", "Arcane Intellect"],
        ),
        _child(
            aura_id="Divine Spirit",
            uid="w(4DygDR1PR",
            icon=135946,
            names=["Prayer of Spirit", "Divine Spirit"],
        ),
        _child(
            aura_id="Shadow Protection",
            uid="v1V9gYykpUo",
            icon=135945,
            names=["Prayer of Shadow Protection", "Shadow Protection"],
        ),
        _child(
            aura_id="Well Fed",
            uid="7cHYBkGPYe0",
            icon=136000,
            names=["Well Fed"],
        ),
        _wizard_oil(),
    ]
    return {
        "c": children,
        "d": {
            "actions": {"finish": [], "init": [], "start": []},
            "align": "CENTER",
            "alpha": 1.0,
            "anchorFrameType": "SCREEN",
            "anchorPoint": "CENTER",
            "animate": True,
            "animation": {
                "finish": dict(_NOOP_ANIMATION),
                "main": dict(_NOOP_ANIMATION),
                "start": dict(_NOOP_ANIMATION),
            },
            "arcLength": 360.0,
            "authorOptions": [],
            "backdropColor": [1.0, 1.0, 1.0, 0.5],
            "border": False,
            "borderBackdrop": "Blizzard Tooltip",
            "borderColor": [0.0, 0.0, 0.0, 1.0],
            "borderEdge": "1 Pixel",
            "borderInset": 1.0,
            "borderOffset": 4.0,
            "borderSize": 2.0,
            "centerType": "LR",
            "columnSpace": 1.0,
            "conditions": [],
            "config": [],
            "constantFactor": "RADIUS",
            "desc": "Tracks raid buffs, Helps prevent you from having to scan buffbar to double check if you got everything.",
            "frameStrata": 1.0,
            "fullCircle": True,
            "gridType": "RD",
            "gridWidth": 5.0,
            "groupIcon": 135740,
            "grow": "HORIZONTAL",
            "id": "Tankadin Raid Buffs Tracker",
            "information": {
                "forceEvents": True,
                "ignoreOptionsEventErrors": True,
                "showNilIsFalse": True,
            },
            "internalVersion": 90.0,
            "limit": 5.0,
            "load": {
                "class": {"multi": {"PALADIN": True}, "single": "PALADIN"},
                "size": {"multi": []},
                "spec": {"multi": []},
                "talent": {"multi": []},
                "use_class": True,
                "zoneIds": "",
            },
            "radius": 200.0,
            "regionType": "dynamicgroup",
            "rotation": 0.0,
            "rowSpace": 1.0,
            "scale": 0.85,
            "selfPoint": "CENTER",
            "sort": "none",
            "space": 0.0,
            "stagger": 0.0,
            "stepAngle": 15.0,
            "subRegions": [],
            "tocversion": 20506,
            "triggers": [
                {
                    "trigger": {
                        "debuffType": "HELPFUL",
                        "event": "Health",
                        "names": [],
                        "spellIds": [],
                        "subeventPrefix": "SPELL",
                        "subeventSuffix": "_CAST_START",
                        "type": "aura2",
                        "unit": "player",
                    },
                    "untrigger": [],
                }
            ],
            "uid": "jAAcQ(ToJl(",
            "useAnchorPerUnit": False,
            "useLimit": False,
            "xOffset": 0.0,
            "yOffset": 506.0,
        },
    }


def make_buff_group() -> dict[str, Any]:
    """Return a fresh code-defined Tankadin raid-buff dynamic group."""

    return _buff_group()
