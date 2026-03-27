# EasyPIDX

EasyPIDX (EasyPID Manager) is a tiny Python command-line tool for Windows that lists running processes and provides a keyboard-friendly interface to kill processes by PID.

## Features

- Displays current processes in a table with name, PID, and memory usage
- Paginated navigation using arrow keys
- Kill process using selected row + Enter
- Manual PID kill mode using `K`
- Process search/filter by name or PID

## Requirements

- Windows (uses `tasklist`, `taskkill`, and `msvcrt`)
- Python 3.x

## Installation

1. Clone repo:

```bash
git clone https://github.com/<YOUR_USERNAME>/EasyPIDX.git
cd EasyPIDX
```

2. Run directly:

```bash
python easy_pid_manager.py
```

## Usage

- Option `1`: Browse/Search Processes
- Option `2`: Kill Process (arrow select + Enter, or manual PID entry)
- `Q`: Quit

## Notes

- Run with administrator privileges for best ability to kill processes.
- Killing system or protected processes may fail.
