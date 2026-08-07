"""Code-defined WeakAuras package.

This is the source of truth for the project.  The original Wago import is
kept under ``imports/`` as a reference, but the build does not decode it.
"""

from __future__ import annotations

from typing import Any

from .buff_definition import make_buff_group


_NOOP_ANIMATION = {
    "duration_type": "seconds",
    "easeStrength": 3.0,
    "easeType": "none",
    "type": "none",
}

TARGET_ICON_SIZE = 38.0
TARGET_GROUP_Y_OFFSET = -22.0


def _animation() -> dict[str, dict[str, Any]]:
    return {
        "finish": {**_NOOP_ANIMATION, "preset": "fade"},
        "main": dict(_NOOP_ANIMATION),
        "start": {**_NOOP_ANIMATION, "preset": "fade"},
    }


def _load() -> dict[str, Any]:
    return {
        "class": {"multi": {"HUNTER": True}, "single": "HUNTER"},
        "ingroup": {"multi": {"group": True}, "single": "group"},
        "size": {"multi": {"fortyman": True, "twentyfive": True}},
        "spec": {"multi": []},
        "talent": {"multi": []},
    }


def _target_aura_trigger(
    aura_name: str,
    *,
    name_pattern: bool = False,
    matches_show_on: str = "showAlways",
) -> dict[str, Any]:
    trigger: dict[str, Any] = {
        "auranames": [aura_name],
        "debuffType": "HARMFUL",
        "event": "Health",
        "matchesShowOn": matches_show_on,
        "names": [],
        "spellIds": [],
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
        "type": "aura2",
        "unit": "target",
        "useName": not name_pattern,
    }
    if name_pattern:
        trigger.update(
            {
                "namePattern_name": aura_name,
                "namePattern_operator": "find('%s')",
                "useName": False,
                "useNamePattern": True,
            }
        )
    return trigger


def _provider_trigger(
    class_name: str,
    aura_name: str | None = None,
) -> dict[str, Any]:
    trigger: dict[str, Any] = {
        "class": class_name,
        "debuffType": "HELPFUL",
        "event": "Unit Characteristics",
        "type": "unit",
        "unit": "group",
        "use_class": True,
        "use_unit": True,
    }
    if aura_name:
        trigger.update(
            {
                "auranames": [aura_name],
                "debuffType": "HARMFUL",
                "useName": True,
            }
        )
    return trigger


def _target_attackable_trigger() -> dict[str, Any]:
    return {
        "debuffType": "HELPFUL",
        "event": "Unit Characteristics",
        "type": "unit",
        "unit": "target",
        "use_attackable": True,
        "use_unit": True,
    }


def _target_alive_trigger() -> dict[str, Any]:
    return {
        "debuffType": "HELPFUL",
        "event": "Health",
        "health": "0",
        "health_operator": ">",
        "type": "unit",
        "unit": "target",
        "use_health": True,
        "use_unit": True,
    }


def _sunder_follow_up_trigger() -> dict[str, Any]:
    trigger = _target_aura_trigger("Expose Armor", matches_show_on="showOnMissing")
    trigger.update(
        {
            "health": "0",
            "health_operator": ">",
            "use_health": True,
            "use_unit": True,
        }
    )
    return trigger


def _subregions(text_size: float = 14.0, text: str = "%p") -> list[dict[str, Any]]:
    return [
        {
            "glow": False,
            "glowBorder": False,
            "glowColor": [1.0, 0.0, 0.12941176470588, 1.0],
            "glowDuration": 1.0,
            "glowFrequency": 0.25,
            "glowLength": 7.8,
            "glowLines": 8.0,
            "glowScale": 1.0,
            "glowThickness": 2.0,
            "glowType": "buttonOverlay",
            "glowXOffset": 0.0,
            "glowYOffset": 0.0,
            "type": "subglow",
            "useGlowColor": True,
        },
        {
            "border_color": [0.0, 0.0, 0.0, 1.0],
            "border_edge": "1 Pixel",
            "border_offset": 0.0,
            "border_size": 1.0,
            "border_visible": True,
            "type": "subborder",
        },
        {
            "anchorXOffset": 0.0,
            "anchorYOffset": 0.0,
            "rotateText": "NONE",
            "text_anchorPoint": "CENTER",
            "text_anchorXOffset": 1.0,
            "text_anchorYOffset": 0.0,
            "text_automaticWidth": "Auto",
            "text_color": [1.0, 1.0, 1.0, 1.0],
            "text_fixedWidth": 64.0,
            "text_font": "Friz Quadrata TT",
            "text_fontSize": text_size,
            "text_fontType": "OUTLINE",
            "text_justify": "CENTER",
            "text_selfPoint": "AUTO",
            "text_shadowColor": [0.0, 0.0, 0.0, 1.0],
            "text_shadowXOffset": 0.0,
            "text_shadowYOffset": 0.0,
            "text_text": text,
            "text_text_format_p_format": "timed",
            "text_text_format_p_time_dynamic_threshold": 0.0,
            "text_text_format_p_time_format": 0.0,
            "text_text_format_p_time_precision": 1.0,
            "text_visible": True,
            "text_wordWrap": "WordWrap",
            "type": "subtext",
        },
    ]


def _missing_condition() -> dict[str, Any]:
    return {
        "changes": [
            {"property": "desaturate", "value": True},
            {"property": "alpha", "value": 0.5},
            {"property": "sub.1.glow", "value": True},
        ],
        "check": {"trigger": 1.0, "value": 0.0, "variable": "buffed"},
    }


def _child(
    *,
    aura_id: str,
    aura_name: str,
    uid: str,
    icon: int,
    provider_class: str,
    provider_aura_name: str | None = None,
    name_pattern: bool = False,
    sunder_follow_up: bool = False,
) -> dict[str, Any]:
    triggers: dict[str, Any] = {
        "activeTriggerMode": -10.0,
        "customTriggerLogic": "function(t)\n    return (t[1] or t[2]) and t[3] and t[4]\nend",
        "disjunctive": "all",
        "1": {
            "trigger": _target_aura_trigger(aura_name, name_pattern=name_pattern),
            "untrigger": [],
        },
        "2": {
            "trigger": _provider_trigger(provider_class, provider_aura_name),
            "untrigger": [],
        },
        "3": {"trigger": _target_attackable_trigger(), "untrigger": []},
        "4": {"trigger": _target_alive_trigger(), "untrigger": []},
    }
    if sunder_follow_up:
        triggers["4"]["trigger"]["use_class"] = False
        triggers["customTriggerLogic"] = (
            "function(t)\n"
            "    return (t[1] or t[2]) and t[3] and t[4] and t[5]\n"
            "end"
        )
        triggers["5"] = {
            "trigger": _sunder_follow_up_trigger(),
            "untrigger": [],
        }

    return {
        "actions": {"finish": [], "init": [], "start": []},
        "alpha": 1.0,
        "anchorFrameType": "SCREEN",
        "anchorPoint": "CENTER",
        "animation": _animation(),
        "authorOptions": [],
        "color": [1.0, 1.0, 1.0, 1.0],
        "conditions": [_missing_condition()],
        "config": [],
        "cooldown": sunder_follow_up,
        "cooldownEdge": False,
        "cooldownSwipe": True,
        "cooldownTextDisabled": False,
        "desaturate": False,
        "displayIcon": icon,
        "frameStrata": 1.0,
        "icon": True,
        "iconSource": -1.0,
        "id": aura_id,
        "information": [],
        "internalVersion": 45.0,
        "inverse": False,
        "keepAspectRatio": False,
        "load": _load(),
        "regionType": "icon",
        "selfPoint": "CENTER",
        "subRegions": _subregions(20.0, "%s")
        if sunder_follow_up
        else _subregions(),
        "tocversion": 20502,
        "triggers": triggers,
        "uid": uid,
        "version": 1.0,
        "width": TARGET_ICON_SIZE,
        "height": TARGET_ICON_SIZE,
        "xOffset": 0.0,
        "yOffset": 0.0,
        "zoom": 0.15,
    }


def _dynamic_group() -> dict[str, Any]:
    return {
        "actions": {"finish": [], "init": [], "start": []},
        "align": "CENTER",
        "anchorFrameType": "SCREEN",
        "anchorPoint": "TOP",
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
        "borderEdge": "Square Full White",
        "borderInset": 1.0,
        "borderOffset": 4.0,
        "borderSize": 2.0,
        "columnSpace": 1.0,
        "conditions": [],
        "config": [],
        "constantFactor": "RADIUS",
        "desc": "Target Debuff Tracker - code-defined",
        "frameStrata": 1.0,
        "fullCircle": True,
        "gridType": "RD",
        "gridWidth": 10.0,
        "groupIcon": 136142,
        "grow": "HORIZONTAL",
        "id": "Target Debuff Tracker",
        "information": [],
        "internalVersion": 45.0,
        "limit": 5.0,
        "load": {
            "class": {"multi": []},
            "size": {"multi": []},
            "spec": {"multi": []},
            "talent": {"multi": []},
        },
        "radius": 200.0,
        "regionType": "dynamicgroup",
        "rotation": 0.0,
        "rowSpace": 1.0,
        "scale": 1.0,
        "selfPoint": "CENTER",
        "sort": "none",
        "space": 1.0,
        "stagger": 0.0,
        "subRegions": [],
        "tocversion": 20502,
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
        "uid": "7fDRG37S0iS",
        "useLimit": False,
        "xOffset": 0.0,
        "yOffset": TARGET_GROUP_Y_OFFSET,
    }


def _outer_group() -> dict[str, Any]:
    """Define the import root that keeps each tracker independently configurable."""

    return {
        "actions": {"finish": [], "init": [], "start": []},
        "anchorFrameType": "SCREEN",
        "anchorPoint": "CENTER",
        "animation": _animation(),
        "authorOptions": [],
        "conditions": [],
        "config": [],
        "id": "WoW Anniversary QoL",
        "information": [],
        "internalVersion": 90.0,
        "load": {
            "class": {"multi": []},
            "size": {"multi": []},
            "spec": {"multi": []},
            "talent": {"multi": []},
        },
        "regionType": "group",
        "selfPoint": "CENTER",
        "subRegions": [],
        "tocversion": 20506,
        "uid": "wow-anniversary-qol",
        "version": 1.0,
        "xOffset": 0.0,
        "yOffset": 0.0,
    }


def make_package() -> dict[str, Any]:
    """Return a fresh, fully code-defined tracker package."""

    children = [
        _child(
            aura_id="TDT - Judgement of Wisdom",
            aura_name="Judgement of Wisdom",
            uid="gtyC4skSdg1",
            icon=135960,
            provider_class="PALADIN",
        ),
        _child(
            aura_id="TDT - Judgement of the Crusade",
            aura_name="Judgement of the Crusader",
            uid="C75XNQxMSRd",
            icon=135924,
            provider_class="PALADIN",
        ),
        _child(
            aura_id="TDT - Hunter's Mark",
            aura_name="Hunter's Mark",
            uid="2CcbNBeYyh1",
            icon=132212,
            provider_class="HUNTER",
        ),
        _child(
            aura_id="TDT - Faerie Fire",
            aura_name="Faerie Fire",
            uid="Py8MtHWwJdo",
            icon=136033,
            provider_class="DRUID",
            name_pattern=True,
        ),
        _child(
            aura_id="TDT - Curse of Recklessness",
            aura_name="Curse of Recklessness",
            uid="08jSlp0AHf(",
            icon=136225,
            provider_class="WARLOCK",
        ),
        _child(
            aura_id="TDT - Expose Armor",
            aura_name="Expose Armor",
            uid="s1cpLPmfmn9",
            icon=132354,
            provider_class="ROGUE",
            provider_aura_name="Expose Armor",
            name_pattern=True,
        ),
        _child(
            aura_id="TDT - Sunder Armor",
            aura_name="Sunder Armor",
            uid="i3lHUIHu9aF",
            icon=132363,
            provider_class="WARRIOR",
            name_pattern=True,
            sunder_follow_up=True,
        ),
    ]
    target_group = {"c": children, "d": _dynamic_group()}

    return {
        "c": [target_group, make_buff_group()],
        "d": _outer_group(),
        "m": "d",
        "s": "3.7.2",
        "v": 1421.0,
    }
