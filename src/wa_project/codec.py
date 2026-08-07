"""WeakAuras !WA:2! codec backed by the project's Lua libraries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lupa import LuaRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CODEC_ROOT = PROJECT_ROOT / "vendor" / "python-weakauras-tool"

_DECODE_LUA = r'''
function(input_string, path)
    dofile(path .. "/lua/libs/wowhelpers.lua")
    dofile(path .. "/lua/libs/LibStub/LibStub.lua")
    dofile(path .. "/lua/libs/LibDeflate/LibDeflate.lua")
    dofile(path .. "/lua/libs/LibSerialize/LibSerialize.lua")
    local LibDeflate = LibStub:GetLibrary("LibDeflate")
    local LibSerialize = LibStub("LibSerialize")
    local JSON = dofile(path .. "/lua/libs/json.lua")

    local _, _, encodeVersion, encoded = input_string:find("^(!WA:%d+!)(.+)$")
    if not encodeVersion then
        return "unsupported WeakAuras prefix"
    end
    encodeVersion = tonumber(encodeVersion:match("%d+"))
    if encodeVersion < 2 then
        return "unsupported WeakAuras version"
    end

    local decoded = LibDeflate:DecodeForPrint(encoded)
    if not decoded then return "failed to decode" end
    local decompressed = LibDeflate:DecompressDeflate(decoded)
    if not decompressed then return "failed to decompress" end
    local success, deserialized = LibSerialize:Deserialize(decompressed)
    if not success then return "failed to deserialize" end
    return JSON:encode(deserialized)
end
'''

_ENCODE_LUA = r'''
function(input_json, path)
    dofile(path .. "/lua/libs/wowhelpers.lua")
    dofile(path .. "/lua/libs/LibStub/LibStub.lua")
    dofile(path .. "/lua/libs/LibDeflate/LibDeflate.lua")
    dofile(path .. "/lua/libs/LibSerialize/LibSerialize.lua")
    local LibDeflate = LibStub:GetLibrary("LibDeflate")
    local LibSerialize = LibStub("LibSerialize")
    local JSON = dofile(path .. "/lua/libs/json.lua")

    local data = JSON:decode(input_json)
    if not data then return "failed to decode JSON" end
    local serialized = LibSerialize:SerializeEx({ errorOnUnserializableType = false }, data)
    local compressed = LibDeflate:CompressDeflate(serialized, { level = 9 })
    return "!WA:2!" .. LibDeflate:EncodeForPrint(compressed)
end
'''

_BIT_COMPAT_LUA = r'''
unpack = table.unpack
package.preload["bit"] = function()
    local bit = {}
    local function u32(n)
        return (math.tointeger(n) or 0) & 0xFFFFFFFF
    end
    function bit.band(a, b)
        return u32(u32(a) & u32(b))
    end
    function bit.bor(a, b)
        return u32(u32(a) | u32(b))
    end
    function bit.bxor(a, b)
        return u32(u32(a) ~ u32(b))
    end
    function bit.bnot(a)
        return u32(~u32(a))
    end
    function bit.lshift(a, b)
        return u32(u32(a) << (math.tointeger(b) or 0))
    end
    function bit.rshift(a, b)
        return u32(u32(a) >> (math.tointeger(b) or 0))
    end
    return bit
end
'''


def _run_lua(source: str, value: str) -> str:
    if not CODEC_ROOT.exists():
        raise RuntimeError(
            "Codec dependency is missing. Run: "
            "git submodule update --init --recursive"
        )
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(_BIT_COMPAT_LUA)
    function = lua.eval(source)
    result = function(value, str(CODEC_ROOT))
    if not isinstance(result, str):
        raise RuntimeError("WeakAuras codec returned a non-string result")
    if result.startswith(("failed ", "unsupported ")):
        raise ValueError(result)
    return result


def decode(import_text: str) -> dict[str, Any]:
    """Decode a `!WA:2!` import string into JSON-compatible Python data."""

    raw = _run_lua(_DECODE_LUA, import_text.strip())
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("WeakAuras import did not contain a top-level table")
    return data


def encode(data: dict[str, Any]) -> str:
    """Encode JSON-compatible Python data as a `!WA:2!` import string."""

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return _run_lua(_ENCODE_LUA, payload)
