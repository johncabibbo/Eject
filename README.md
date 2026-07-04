# Eject Drives

A Python script to eject all external hard drives on macOS.

## Requirements

- macOS
- Python 3.12+
- CB9Lib (located at `~/Documents/script/CB9Lib`)

## Installation

The script is ready to use. Ensure it has execute permissions:

```bash
chmod +x ejectDrives.py
```

## Usage

### Interactive Mode

Run without arguments to launch the interactive menu:

```bash
python3 ejectDrives.py
./ejectDrives.py
```

**Interactive Menu Options:**
- `[A]` - Eject all external drives (with confirmation)
- `[1-9]` - Eject a specific drive by number
- `[R]` - Refresh the drive list
- `[Q]` or `[Enter]` - Quit

If a drive fails to eject, you'll be prompted to force eject.

### Command-Line Mode

#### Eject All Drives (No Prompts)

```bash
python3 ejectDrives.py all
```

Immediately ejects all external drives without any confirmation dialogs. Useful for scripts and automation.

#### Force Eject All Drives

```bash
python3 ejectDrives.py force
```

Force ejects all external drives, bypassing processes that may be using them (like Spotlight indexing). Use this if `all` fails due to processes holding the drive.

**Warning:** Force eject may cause data loss if files are being written. Ensure no active file operations before using.

**Exit codes:**
- `0` - All drives ejected successfully
- `1` - One or more drives failed to eject

#### List Drives

```bash
python3 ejectDrives.py list
```

Lists all connected external drives with their details (name, size, mount point, disk identifier) and exits.

#### Help

```bash
python3 ejectDrives.py help
```

Shows usage information.

## Examples

### Quick Eject Before Unplugging

```bash
./ejectDrives.py all && echo "Safe to unplug drives"
```

### Force Eject When Spotlight is Blocking

```bash
# If regular eject fails due to mds_stores (Spotlight)
./ejectDrives.py force
```

### Check Connected Drives

```bash
./ejectDrives.py list
```

Output:
```
Found 2 external drive(s):

  1. Backup_Drive
     Size: 2.0 TB
     Mount: /Volumes/Backup_Drive
     Disk: disk4

  2. USB_Stick
     Size: 32.0 GB
     Mount: /Volumes/USB_Stick
     Disk: disk5
```

### Use in Shell Script

```bash
#!/bin/bash
# backup_and_eject.sh

# Run backup
rsync -av ~/Documents /Volumes/Backup_Drive/

# Eject all drives when done (force if needed)
~/Documents/script/ejectDrives/ejectDrives.py all || \
~/Documents/script/ejectDrives/ejectDrives.py force
```

### Create an Alias

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias eject='~/Documents/script/ejectDrives/ejectDrives.py'
alias ejectall='~/Documents/script/ejectDrives/ejectDrives.py all'
alias ejectforce='~/Documents/script/ejectDrives/ejectDrives.py force'
```

Then use:
```bash
eject          # Interactive mode
ejectall       # Eject all without prompts
ejectforce     # Force eject all (bypasses Spotlight, etc.)
```

## How It Works

1. Scans `/Volumes/` for mounted volumes
2. Uses `diskutil info` to check each volume's properties
3. Identifies external drives by checking:
   - `Internal: No`
   - `Protocol: USB, Thunderbolt, SATA, or FireWire`
4. Uses `diskutil eject` to safely eject drives
5. For force eject, uses `diskutil unmountDisk force` before ejecting

## Troubleshooting

### "Unmount was dissented by PID"

This error means a process is using the drive. Common causes:
- **mds_stores (Spotlight)** - Indexing the drive
- **Finder** - Open windows or previews
- **Time Machine** - Backup in progress
- **Applications** - Files open from the drive

**Solutions:**
1. Use force eject: `./ejectDrives.py force`
2. Close applications using the drive
3. Disable Spotlight indexing for the drive (System Settings > Siri & Spotlight > Spotlight Privacy)

## Version History

- **v1.2** - Added force eject option (`force` command, interactive prompt on failure)
- **v1.1** - Added command-line arguments (`all`, `list`, `help`)
- **v1.0** - Initial release with interactive menu

## Author

Cloud Box 9 Inc.

## License

Copyright 2026 Cloud Box 9 Inc. All rights reserved.
