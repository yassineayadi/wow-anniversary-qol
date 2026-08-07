"""Publish the generated import through a small companion WoW addon."""

from __future__ import annotations

import json
from hashlib import sha1
from pathlib import Path
from typing import Any

from .build import DEFAULT_OUTPUT, build


ADDON_NAME = "WowAnniversaryQoL"
TOC_INTERFACE = "20506"


def _addon_toc() -> str:
    return f"""## Interface: {TOC_INTERFACE}
## Title: WoW Anniversary QoL - Generated WeakAuras
## Notes: Applies the project-generated WeakAuras package.
## Dependencies: WeakAuras
## SavedVariables: WoWAnniversaryQoLDB

{ADDON_NAME}.lua
"""


def _addon_lua(import_string: str, build_id: str) -> str:
    encoded_import = json.dumps(import_string, ensure_ascii=True)
    encoded_build_id = json.dumps(build_id, ensure_ascii=True)
    return f"""local importString = {encoded_import}
local buildId = {encoded_build_id}

WoWAnniversaryQoLDB = WoWAnniversaryQoLDB or {{}}

local function updateWeakAuras()
    if not WeakAuras or type(WeakAuras.ImportString) ~= "function" then
        print("|cffff5555WoW Anniversary QoL: WeakAuras import API unavailable.|r")
        return false
    end

    local result = WeakAuras.ImportString(importString)
    if not result then
        print("|cffff5555WoW Anniversary QoL: WeakAuras import failed.|r")
        return false
    end

    WoWAnniversaryQoLDB.lastAppliedBuild = buildId
    print("|cff55ff55WoW Anniversary QoL: WeakAuras updated (" .. buildId .. ").|r")
    return true
end

local function updateIfChanged()
    if WoWAnniversaryQoLDB.lastAppliedBuild ~= buildId then
        updateWeakAuras()
    end
end

SLASH_WOWANNIVERSARYQOL1 = "/waqol"
SlashCmdList.WOWANNIVERSARYQOL = function(message)
    message = (message or ""):lower()
    if message == "" or message == "update" then
        updateWeakAuras()
    elseif message == "version" then
        print("WoW Anniversary QoL generated build: " .. buildId)
    else
        print("Usage: /waqol update | /waqol version")
    end
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_LOGIN")
frame:SetScript("OnEvent", function(self)
    self:UnregisterEvent("PLAYER_LOGIN")
    updateIfChanged()
end)
"""


def publish(
    addon_root: Path,
    *,
    import_output: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Build and install the companion addon under an Interface/AddOns folder."""

    package = build(output=import_output)
    import_string = import_output.read_text(encoding="utf-8").strip()
    build_id = sha1(import_string.encode("utf-8")).hexdigest()[:12]

    addon_dir = addon_root / ADDON_NAME
    addon_dir.mkdir(parents=True, exist_ok=True)
    (addon_dir / f"{ADDON_NAME}.toc").write_text(
        _addon_toc(), encoding="utf-8", newline="\n"
    )
    (addon_dir / f"{ADDON_NAME}.lua").write_text(
        _addon_lua(import_string, build_id), encoding="utf-8", newline="\n"
    )
    return {
        "package": package,
        "addon_dir": addon_dir,
        "import_output": import_output,
        "build_id": build_id,
    }
