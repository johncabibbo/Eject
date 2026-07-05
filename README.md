# Eject Drives

**Safely eject all external drives on your Mac — from an interactive menu or a single command.**

`ejectDrives.py` finds every external volume mounted under `/Volumes`, then ejects them — either through an interactive terminal menu or non-interactively for use inside shell scripts. When a normal eject is blocked (Spotlight, Finder holds, etc.), it can force-unmount and falls back to a Finder AppleScript eject. CB9Lib is bundled.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Alias Setup — Run From Anywhere](#alias-setup--run-from-anywhere)
6. [Usage & Examples](#usage--examples)
7. [How Drive Detection Works](#how-drive-detection-works)
8. [Troubleshooting](#troubleshooting)
9. [License / Copyright](#license--copyright)

---

## Overview

One command cleanly disconnects every external drive before you unplug a dock or shut down — no dragging icons to the Trash, no "disk not ejected properly" warnings.

---

## Features

- **Interactive TUI** — see all external drives; eject all `[A]`, one by number `[1-9]`, refresh `[R]`, or quit.
- **Non-interactive CLI modes** — `all`, `force`, `list`, `help` for scripting and automation.
- **Force eject** — `diskutil unmountDisk force` for stubborn volumes.
- **Finder fallback** — AppleScript eject when `diskutil` refuses.
- **Script-friendly exit codes** — `0` on full success, `1` if any drive fails.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| **macOS** | Uses `diskutil` and Finder AppleScript — macOS only. |
| **Python 3.12+** | CB9Lib is **bundled** — no separate install. |

---

## Installation

```bash
git clone <REPOSITORY_URL> Eject
cd Eject
python3 ejectDrives.py list
```

---

## Alias Setup — Run From Anywhere

Launch from any directory by typing `eject`.

### macOS (zsh or bash)

Add to `~/.zshrc` (default on modern macOS) or `~/.bash_profile`:

```bash
alias eject='python3 ~/path/to/Eject/ejectDrives.py'
```

Reload and run:

```bash
source ~/.zshrc
eject
```

**Alternative — symlink onto your `PATH`:**

```bash
chmod +x ~/path/to/Eject/ejectDrives.py
ln -s ~/path/to/Eject/ejectDrives.py /usr/local/bin/eject
```

> **Windows / Linux:** not applicable — this tool is macOS-specific.

---

## Usage & Examples

```bash
python3 ejectDrives.py          # interactive menu
./ejectDrives.py all            # eject all external drives (no prompts)
./ejectDrives.py force          # force-unmount then eject (use if 'all' fails)
./ejectDrives.py list           # list external drives and exit
./ejectDrives.py help           # show help
```

**In a shutdown script:**

```bash
~/path/to/Eject/ejectDrives.py all || echo "Some drives failed to eject"
```

`all` exits `0` only when every external drive ejects successfully.

---

## How Drive Detection Works

A volume under `/Volumes` is treated as **external** when `diskutil info` reports any of:

- `Internal: No`, or
- `Protocol:` is `usb`, `thunderbolt`, `sata`, or `firewire`, or
- `Removable Media:` is `Removable` / `Yes`.

Volumes are deduplicated by their whole-disk identifier (e.g. `disk4`).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Resource busy" / eject fails | Close apps using the disk, then try `force`. |
| Drive still won't eject | `./ejectDrives.py force` force-unmounts before ejecting. |
| Internal disk listed | It shouldn't be — report the `diskutil info` output; detection keys on external/removable/protocol. |

---

## License / Copyright

---
**Version:** 1.2
**Author:** Cloud Box 9 Inc.
**Maintainer / Owner:** Cloud Box 9 Inc.
**Last Updated:** Jul 5, 2026

Copyright © 2026 Cloud Box 9 Inc. All rights reserved.
