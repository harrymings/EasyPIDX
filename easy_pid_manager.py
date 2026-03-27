#!/usr/bin/env python3
"""
EasyPID Manager - Integrated Arrow Selection & Manual PID Entry
"""

# Standard library imports
import subprocess
import sys
import os
import msvcrt

# Number of processes displayed per page in UI
PAGE_SIZE = 15


def get_processes():
    """Return a list of currently running processes on Windows.

    Uses tasklist (CSV) output and returns a dict list with keys:
    name, pid, memory (bytes).
    """
    try:
        result = subprocess.run(
            ['tasklist', '/fo', 'csv', '/nh'],
            capture_output=True,
            text=True,
            check=True
        )

        processes = []

        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue

            # tasklist CSV is like: "Image Name","PID","Session Name","Session#","Mem Usage"
            parts = [p.strip('"').strip() for p in line.split('","')]
            if len(parts) < 5:
                continue

            try:
                processes.append({
                    'name': parts[0],
                    'pid': int(parts[1]),
                    'memory': int(parts[4].replace(',', '').replace(' K', '')) * 1024
                })
            except ValueError:
                continue

        return processes

    except Exception as e:
        print(f"Error fetching processes: {e}")
        return []


def kill_process(pid):
    """Terminate an OS process by PID (force kill)."""
    result = subprocess.run(
        ['taskkill', '/pid', str(pid), '/f'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"\n[OK] Terminated PID {pid}")
        return True

    print(f"\n[ERROR] Could not kill {pid}. It may be a system process or access is denied.")
    return False


def clear_screen():
    """Clear terminal screen for Windows and POSIX systems."""
    os.system('cls' if os.name == 'nt' else 'clear')


def wait_for_key():
    """Wait for a key press and translate arrows/enter/esc."""
    key = msvcrt.getch()

    # Arrow key sequences are 2 bytes on Windows via msvcrt
    if key in (b'\x00', b'\xe0'):
        arrow = msvcrt.getch()
        return {
            b'H': 'UP',
            b'P': 'DOWN',
            b'M': 'RIGHT',
            b'K': 'LEFT'
        }.get(arrow)

    if key == b'\r':
        return 'ENTER'

    if key == b'\x1b':
        return 'ESC'

    # Normalize other printable keys
    return key.decode('utf-8', errors='ignore').upper()


def integrated_kill_ui(processes):
    """Interactive process browser + kill interface.

    Navigates with arrow keys, Enter to kill selection, K for manual PID input.
    """
    current_page = 0
    selected_idx = 0

    # Sort process list alphabetically for stable browsing
    processes.sort(key=lambda x: x['name'].lower())

    while True:
        clear_screen()

        total_procs = len(processes)
        total_pages = (total_procs + PAGE_SIZE - 1) // PAGE_SIZE
        current_page = max(0, min(current_page, total_pages - 1))

        start = current_page * PAGE_SIZE
        end = min(start + PAGE_SIZE, total_procs)
        page_items = processes[start:end]

        if selected_idx >= len(page_items):
            selected_idx = max(0, len(page_items) - 1)

        # Header
        print('=' * 75)
        print('                KILL PROCESS: SELECT OR ENTER PID')
        print('=' * 75)
        print(f"{'#':<4} {'NAME':<35} {'PID':<10} {'MEMORY':<15}")
        print('-' * 75)

        # Display rows
        for i, proc in enumerate(page_items):
            mem = f"{proc['memory'] // 1024 // 1024} MB"
            line = f"{i + 1:<4} {proc['name']:<35} {proc['pid']:<10} {mem:<15}"

            if i == selected_idx:
                # Invert colors on selected line (ANSI escape sequence)
                print(f"\033[7m{line}\033[0m")
            else:
                print(line)

        print('-' * 75)
        print(f" Page {current_page + 1}/{total_pages} | {total_procs} processes found")
        print(' [ARROWS] Navigate | [ENTER] Kill Selected | [K] Kill By Entering PID Manually | [ESC] Back')
        print('=' * 75)

        key = wait_for_key()

        # Navigation keys
        if key == 'UP':
            if selected_idx > 0:
                selected_idx -= 1
            elif current_page > 0:
                current_page -= 1
                selected_idx = PAGE_SIZE - 1

        elif key == 'DOWN':
            if selected_idx < len(page_items) - 1:
                selected_idx += 1
            elif current_page < total_pages - 1:
                current_page += 1
                selected_idx = 0

        elif key == 'RIGHT' and current_page < total_pages - 1:
            current_page += 1
            selected_idx = 0

        elif key == 'LEFT' and current_page > 0:
            current_page -= 1
            selected_idx = 0

        # Kill selected process entry
        elif key == 'ENTER':
            target = page_items[selected_idx]
            confirm = input(f"\nKill {target['name']} (PID {target['pid']})? (y/n): ").strip().lower()
            if confirm == 'y':
                kill_process(target['pid'])
                input('\nPress Enter to refresh list...')
                return

        # Manual PID entry
        elif key == 'K':
            try:
                manual_pid = int(input('\n>>> Enter PID to kill: ').strip())
                confirm = input(f"Confirm killing PID {manual_pid}? (y/n): ").strip().lower()
                if confirm == 'y':
                    kill_process(manual_pid)
                    input('\nPress Enter to refresh list...')
                    return
            except ValueError:
                print('\n[ERROR] Invalid PID. Please enter a number.')
                input('Press Enter...')

        # Exit UI and return to main menu
        elif key == 'ESC':
            return


def main():
    """Main menu loop for the EasyPID Manager CLI."""
    while True:
        clear_screen()
        print('=' * 70)
        print('                 EasyPID Manager - Integrated')
        print('=' * 70)
        print('\n [1] Browse/Search Processes')
        print(' [2] Kill Process (Arrow Select OR Manual PID)')
        print(' [Q] Quit')
        print('=' * 70)

        choice = input('\nChoice: ').strip().upper()

        if choice == '1':
            p_list = get_processes()
            s = input('\nSearch filter (Enter for all): ').strip().lower()
            filtered = [p for p in p_list if s in p['name'].lower() or s in str(p['pid'])]
            # Browse uses the same interactive UI but killing remains optional from the row.
            integrated_kill_ui(filtered)

        elif choice == '2':
            p_list = get_processes()
            integrated_kill_ui(p_list)

        elif choice == 'Q':
            print('Goodbye!')
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
