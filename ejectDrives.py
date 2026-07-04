#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
"""
Eject Drives - Eject all external hard drives on Mac

Usage:
    python3 ejectDrives.py          # Interactive mode
    python3 ejectDrives.py all      # Eject all drives without prompts
    python3 ejectDrives.py force    # Force eject all drives (use if 'all' fails)
    python3 ejectDrives.py list     # List external drives and exit
    python3 ejectDrives.py help     # Show help
"""

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # bundled CB9Lib (self-contained)

from CB9Lib import *
import subprocess
import re
import shutil
import os
import argparse

SCRIPT_NAME = "Eject Drives"
SCRIPT_VERSION = "v1.2"


def get_external_drives():
    """Get list of external drives by checking mounted volumes"""
    drives = []

    try:
        # Get all mounted volumes from /Volumes
        volumes_path = '/Volumes'
        if not os.path.exists(volumes_path):
            return drives

        for volume_name in os.listdir(volumes_path):
            volume_path = os.path.join(volumes_path, volume_name)

            # Skip if not a mount point
            if not os.path.ismount(volume_path):
                continue

            # Get disk info for this volume
            info_result = subprocess.run(
                ['diskutil', 'info', volume_path],
                capture_output=True,
                text=True
            )

            if info_result.returncode != 0:
                continue

            info = info_result.stdout

            # Check if it's external/removable
            is_external = False
            is_removable = False
            disk_identifier = None
            size = "Unknown"

            for line in info.split('\n'):
                if 'Protocol:' in line:
                    protocol = line.split(':')[1].strip().lower()
                    if protocol in ['usb', 'thunderbolt', 'sata', 'firewire']:
                        is_external = True
                elif 'Removable Media:' in line:
                    if 'Removable' in line or 'Yes' in line:
                        is_removable = True
                elif 'Part of Whole:' in line:
                    disk_identifier = line.split(':')[1].strip()
                elif 'Device Identifier:' in line and not disk_identifier:
                    # Get base disk from partition identifier (e.g., disk4s1 -> disk4)
                    part_id = line.split(':')[1].strip()
                    match = re.match(r'(disk\d+)', part_id)
                    if match:
                        disk_identifier = match.group(1)
                elif 'Disk Size:' in line or 'Container Total Space:' in line or 'Volume Total Space:' in line:
                    size_match = re.search(r'\((\d[\d,]*)\s*Bytes\)', line)
                    if size_match:
                        bytes_val = int(size_match.group(1).replace(',', ''))
                        size = format_size(bytes_val)
                    else:
                        # Try alternate format
                        size_match = re.search(r'([\d.]+)\s*([KMGT]?B)', line)
                        if size_match:
                            size = size_match.group(1) + ' ' + size_match.group(2)
                elif 'Internal:' in line:
                    if 'No' in line:
                        is_external = True

            # Add if it's external
            if (is_external or is_removable) and disk_identifier:
                drives.append({
                    'identifier': disk_identifier,
                    'name': volume_name,
                    'size': size,
                    'mount_point': volume_path
                })

        # Remove duplicates based on identifier (keep first occurrence with best name)
        seen = {}
        unique_drives = []
        for drive in drives:
            if drive['identifier'] not in seen:
                seen[drive['identifier']] = drive
                unique_drives.append(drive)

        return unique_drives

    except Exception as e:
        return []


def format_size(bytes_val):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"


def eject_via_finder(volume_name):
    """Eject a drive using Finder/AppleScript (same as clicking eject button)

    Args:
        volume_name: Volume name (e.g., MyDrive, not /Volumes/MyDrive)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Use AppleScript to tell Finder to eject - needs just the disk name
        script = f'''
        tell application "Finder"
            eject disk "{volume_name}"
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, "Ejected via Finder"
        else:
            return False, result.stderr.strip()

    except Exception as e:
        return False, str(e)


def eject_drive(identifier, force=False, volume_path=None, volume_name=None):
    """Eject a drive by its identifier

    Args:
        identifier: Disk identifier (e.g., disk4)
        force: If True, force unmount before ejecting
        volume_path: Optional mount path (e.g., /Volumes/MyDrive)
        volume_name: Optional volume name for Finder fallback

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if force:
            # Force unmount all volumes on the disk first
            unmount_result = subprocess.run(
                ['diskutil', 'unmountDisk', 'force', identifier],
                capture_output=True,
                text=True
            )

            if unmount_result.returncode != 0:
                return False, f"Force unmount failed: {unmount_result.stderr.strip()}"

        # Try diskutil eject first
        result = subprocess.run(
            ['diskutil', 'eject', identifier],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, result.stdout.strip()

        # If diskutil fails, try Finder (using volume name)
        if not force:
            # Get volume name from path if not provided
            name = volume_name
            if not name and volume_path:
                name = os.path.basename(volume_path)

            if name:
                finder_success, finder_msg = eject_via_finder(name)
                if finder_success:
                    return True, finder_msg

        return False, result.stderr.strip()

    except Exception as e:
        return False, str(e)


def display_drives(drives):
    """Display the list of external drives"""
    if not drives:
        print(color_text("\n  No external drives found.\n", fg=YELLOW))
        return

    print()
    for i, drive in enumerate(drives, 1):
        # Format: number. Name | Size | Mount Point
        num = color_text(f"{i}.", fg=YELLOW, style=BOLD)
        name = color_text(drive['name'], fg=WHITE, style=BOLD)
        sep = color_text(" | ", fg=BRIGHT_BLACK)
        size = color_text(drive['size'], fg=CYAN)
        mount = color_text(drive['mount_point'], fg=GREEN)

        print(f"  {num} {name}{sep}{size}{sep}{mount}")
    print()


def eject_all_drives(drives):
    """Eject all external drives"""
    if not drives:
        return

    print()
    success_count = 0
    failed_drives = []

    for drive in drives:
        print(color_text(f"  Ejecting {drive['name']}...", fg=CYAN), end=' ')
        success, message = eject_drive(drive['identifier'], volume_path=drive['mount_point'])

        if success:
            print(color_text("Success", fg=GREEN, style=BOLD))
            success_count += 1
        else:
            print(color_text("Failed", fg=RED, style=BOLD))
            print(color_text(f"    Error: {message}", fg=RED))
            failed_drives.append(drive)

    print()
    print_separator()

    if not failed_drives:
        print(color_text(f"\n  All {success_count} drive(s) ejected successfully!\n", fg=GREEN, style=BOLD))
    else:
        print(color_text(f"\n  Ejected: {success_count} | Failed: {len(failed_drives)}\n", fg=YELLOW, style=BOLD))

        # Offer to force eject failed drives
        if confirm("  Force eject failed drive(s)?", default=False):
            print()
            for drive in failed_drives:
                print(color_text(f"  Force ejecting {drive['name']}...", fg=YELLOW), end=' ')
                success, message = eject_drive(drive['identifier'], force=True, volume_path=drive['mount_point'])

                if success:
                    print(color_text("Success", fg=GREEN, style=BOLD))
                    success_count += 1
                else:
                    print(color_text("Failed", fg=RED, style=BOLD))
                    print(color_text(f"    Error: {message}", fg=RED))

            print()
            failed_final = len(failed_drives) - (success_count - (len(drives) - len(failed_drives)))
            if failed_final == 0:
                print(color_text(f"  All drives ejected successfully!\n", fg=GREEN, style=BOLD))
            else:
                print(color_text(f"  Some drives could not be ejected.\n", fg=RED, style=BOLD))

    pause("  Press Enter to return to main menu...")


def print_separator():
    """Print a separator line"""
    width = shutil.get_terminal_size().columns
    print(color_text("-" * width, fg=BRIGHT_BLACK))


def show_exit():
    """Show exit screen"""
    clear_screen()
    header(SCRIPT_NAME, SCRIPT_VERSION)
    print(color_text(f"\n{SCRIPT_NAME} exiting...\n", fg=GREEN))
    print(color_text("Copyright \u00a9 2026 Cloud Box 9 Inc. All rights reserved.\n", fg=CYAN))


def main():
    """Main function"""
    while True:
        clear_screen()
        header(SCRIPT_NAME, SCRIPT_VERSION, "[External Drives]")

        # Get current external drives
        drives = get_external_drives()

        # Display drives
        display_drives(drives)

        # Show menu options
        print_separator()

        if drives:
            print(color_text(" [A]", fg=YELLOW, style=BOLD) + color_text(" Eject All  ", fg=WHITE) +
                  color_text("[1-9]", fg=YELLOW, style=BOLD) + color_text(" Eject Selected  ", fg=WHITE) +
                  color_text("[R]", fg=YELLOW, style=BOLD) + color_text(" Refresh  ", fg=WHITE) +
                  color_text("[Q/Enter]", fg=YELLOW, style=BOLD) + color_text(" Quit", fg=WHITE))
        else:
            print(color_text(" [R]", fg=YELLOW, style=BOLD) + color_text(" Refresh  ", fg=WHITE) +
                  color_text("[Q/Enter]", fg=YELLOW, style=BOLD) + color_text(" Quit", fg=WHITE))

        print_separator()
        print(color_text("Option: ", fg=WHITE), end='', flush=True)

        # Get user input
        user_input = input().strip().lower()

        if user_input in ['q', '']:
            show_exit()
            break
        elif user_input == 'r':
            continue  # Refresh - just loop again
        elif user_input == 'a' and drives:
            if confirm(f"Eject all {len(drives)} drive(s)?", default=False):
                eject_all_drives(drives)
        elif user_input.isdigit() and drives:
            index = int(user_input) - 1
            if 0 <= index < len(drives):
                drive = drives[index]
                if confirm(f"Eject {drive['name']}?", default=True):
                    print(color_text(f"\n  Ejecting {drive['name']}...", fg=CYAN), end=' ')
                    success, message = eject_drive(drive['identifier'], volume_path=drive['mount_point'])

                    if success:
                        print(color_text("Success", fg=GREEN, style=BOLD))
                    else:
                        print(color_text("Failed", fg=RED, style=BOLD))
                        print(color_text(f"    Error: {message}", fg=RED))

                        # Offer force eject
                        print()
                        if confirm("  Force eject?", default=False):
                            print(color_text(f"\n  Force ejecting {drive['name']}...", fg=YELLOW), end=' ')
                            success, message = eject_drive(drive['identifier'], force=True, volume_path=drive['mount_point'])

                            if success:
                                print(color_text("Success", fg=GREEN, style=BOLD))
                            else:
                                print(color_text("Failed", fg=RED, style=BOLD))
                                print(color_text(f"    Error: {message}", fg=RED))

                    print()
                    pause("  Press Enter to return to main menu...")


def eject_all_silent(force=False):
    """Eject all external drives without prompts (for CLI mode)

    Args:
        force: If True, use force unmount for all drives
    """
    drives = get_external_drives()

    if not drives:
        print("No external drives found.")
        return 0

    success_count = 0
    fail_count = 0
    mode = "Force ejecting" if force else "Ejecting"

    for drive in drives:
        print(f"{mode} {drive['name']}...", end=' ')
        success, message = eject_drive(drive['identifier'], force=force, volume_path=drive['mount_point'])

        if success:
            print("OK")
            success_count += 1
        else:
            print(f"FAILED: {message}")
            fail_count += 1

    print(f"\nEjected: {success_count} | Failed: {fail_count}")
    return 0 if fail_count == 0 else 1


def list_drives_cli():
    """List external drives (for CLI mode)"""
    drives = get_external_drives()

    if not drives:
        print("No external drives found.")
        return 0

    print(f"Found {len(drives)} external drive(s):\n")
    for i, drive in enumerate(drives, 1):
        print(f"  {i}. {drive['name']}")
        print(f"     Size: {drive['size']}")
        print(f"     Mount: {drive['mount_point']}")
        print(f"     Disk: {drive['identifier']}")
        print()

    return 0


def show_help():
    """Show help message"""
    print(f"{SCRIPT_NAME} {SCRIPT_VERSION}")
    print("Eject all external hard drives on Mac\n")
    print("Usage:")
    print("  ejectDrives.py              Interactive mode with menu")
    print("  ejectDrives.py all          Eject all drives without prompts")
    print("  ejectDrives.py force        Force eject all drives (use if 'all' fails)")
    print("  ejectDrives.py list         List external drives and exit")
    print("  ejectDrives.py help         Show this help message")
    print()
    print("Examples:")
    print("  python3 ejectDrives.py all    # Quick eject all external drives")
    print("  python3 ejectDrives.py force  # Force eject (ignores Spotlight, etc.)")
    print("  ./ejectDrives.py list         # See what drives are connected")
    print()
    print("Note: Force eject bypasses processes using the drive (like Spotlight).")
    print("      Use with caution - ensure no files are being written.")
    return 0


if __name__ == "__main__":
    try:
        # Check for command-line arguments
        if len(sys.argv) > 1:
            cmd = sys.argv[1].lower()

            if cmd == 'all':
                sys.exit(eject_all_silent(force=False))
            elif cmd == 'force':
                sys.exit(eject_all_silent(force=True))
            elif cmd == 'list':
                sys.exit(list_drives_cli())
            elif cmd in ['help', '-h', '--help', '-?']:
                sys.exit(show_help())
            else:
                print(f"Unknown command: {cmd}")
                print("Use 'help' for usage information.")
                sys.exit(1)
        else:
            # Interactive mode
            main()
    except KeyboardInterrupt:
        show_exit()
