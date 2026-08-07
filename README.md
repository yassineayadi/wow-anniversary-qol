# WeakAuras programmatic project

This project declares the WeakAuras package in Python code. All aura edits belong in code, and the build step publishes a copy/paste-ready `!WA:2!` string.

The starting point was the aura from [Wago](https://wago.io/wpBxVjpPl). Its original import is preserved at `imports/basis.wago` as a reference only; the build never decodes or depends on that file.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
git submodule update --init --recursive
```

The codec submodule contains the WeakAuras-compatible Lua libraries used for `!WA:2!` encoding and round-trip validation. Keep it initialized before running the CLI.

## Workflow

```powershell
# Build the final import string from the code-defined package
wa build

# Inspect the code-defined package in memory
wa inspect

# Verify code definition -> edits -> encode -> decode
wa validate
```

Put the full aura definition in [`src/wa_project/definition.py`](<C:\Users\ayadi\Documents\WoW Classic Anniv\src\wa_project\definition.py>). Put transformations in [`src/wa_project/customize.py`](<C:\Users\ayadi\Documents\WoW Classic Anniv\src\wa_project\customize.py>) inside `apply_edits(package)`. The build creates a fresh package from the definition, applies those edits, and exports it using WeakAuras' current `LibSerialize` + `LibDeflate` `!WA:2!` format.

The package publishes two independent dynamic groups: the raid-DPS-focused Target Debuff Tracker and the imported Tankadin Raid Buffs Tracker. Both are screen-centered at the top, with target debuffs in the first row and raid-buff coverage directly below; their effective icon sizes, spacing, text font, and alert glow are harmonized. Target debuffs include Expose Weakness and Blood Frenzy. Each target debuff icon is visible only inside a raid instance and against a worldboss/raid boss. If a matching class/spec provider exists, the icon is hidden while active and glows when missing; if no provider exists, it remains visible as a dimmed/desaturated disabled icon with a lock overlay. Exact aura names remain the default matching mode, with name patterns retained only for debuffs that genuinely have variants. The dynamic groups grow horizontally from their centers with expand/collapse animation enabled. Expose Weakness requires a Survival Hunter and Blood Frenzy requires an Arms Warrior. The buff tracker is Paladin-only, makes existing generic raid-buff warnings provider-aware, preserves its graduated coverage states, tracks all ranks of Scroll of Protection and Scroll of Agility by name, and tracks Wizard Oil weapon-enchant coverage. It applies the blessing priority Kings -> Wisdom -> Sanctuary -> Might based on the number of Paladins in the raid. Blessings and buffs without an available provider remain visible with a disabled lock state.

On Classic/TBC, group-member spec detection requires WeakAuras' `LibSpecialization` data to be available and synced. If it is unavailable, the spec-gated debuffs remain hidden until the provider spec is known.

The generated import is written to `dist/wa-import.txt`, which is ignored by Git. `imports/basis.wago` remains checked in only as a recovery/comparison reference.

## Editing safely

Prefer small, named transformations over hand-editing large blobs. `apply_edits` receives the code-defined package, finds auras by `id`, changes only the desired properties, and returns the result for the build step. Keep `imports/basis.wago` unchanged so it remains a recovery point.
