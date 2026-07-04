# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ejectDrives.py` — a single-file macOS utility to eject external drives. Supports an interactive TUI menu and non-interactive CLI modes for use in scripts.

**Current version:** v1.2  
**Python:** 3.12+ (`#!/opt/homebrew/opt/python@3.12/libexec/bin/python3`)

## Running the Script

```bash
# Interactive TUI mode
python3 ejectDrives.py
./ejectDrives.py

# CLI modes (no prompts — safe for shell scripts)
./ejectDrives.py all      # eject all external drives; exit 0 on full success, 1 on any failure
./ejectDrives.py force    # force-unmount then eject (bypasses Spotlight, Finder holds, etc.)
./ejectDrives.py list     # print connected external drives and exit
./ejectDrives.py help
```

## Dependency: CB9Lib

CB9Lib is loaded via `sys.path.insert(0, '~/Documents/script/CB9Lib')` at the top of the file. Functions used from it:

| Function / Constant | Purpose |
|---|---|
| `color_text(text, fg, style)` | ANSI-colored terminal output |
| `clear_screen()` | Clear terminal |
| `header(name, version, subtitle)` | Standardized script header bar |
| `confirm(prompt, default)` | Y/N prompt |
| `pause(prompt)` | Wait-for-keypress |
| `YELLOW, BOLD, WHITE, CYAN, GREEN, RED, BRIGHT_BLACK` | Color/style constants |

## Architecture

All logic lives in `ejectDrives.py`. Key functions:

- **`get_external_drives()`** — Scans `/Volumes/`, runs `diskutil info` on each mount point, and identifies external drives by checking `Internal: No` or `Protocol: USB/Thunderbolt/SATA/FireWire`. Deduplicates by disk identifier (e.g., `disk4`).

- **`eject_drive(identifier, force, volume_path, volume_name)`** — Primary eject logic. When `force=True`, runs `diskutil unmountDisk force` first. Otherwise tries `diskutil eject`; on failure falls back to `eject_via_finder()`.

- **`eject_via_finder(volume_name)`** — AppleScript fallback: `tell application "Finder" to eject disk "…"`.

- **`main()`** — Interactive TUI loop: display drives → menu → handle keystrokes (`A`, `1-9`, `R`, `Q/Enter`). On eject failure, prompts for force eject.

- **`eject_all_silent(force)`** — Used by `all`/`force` CLI args. Prints plain-text status per drive, returns exit code.

## Drive Detection Logic

A volume is classified as external when `diskutil info` reports either:
- `Internal: No`, OR
- `Protocol:` is one of `usb`, `thunderbolt`, `sata`, `firewire`, OR
- `Removable Media: Removable` / `Yes`

The disk identifier (e.g., `disk4`) comes from `Part of Whole:` or is parsed from `Device Identifier:` (stripping partition suffix like `s1`).
