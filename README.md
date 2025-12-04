# AutoCheckBJMF - Class Cube Auto Check-in

[![License](https://img.shields.io/github/license/JasonYANG170/AutoCheckBJMF?label=License&style=for-the-badge)](LICENSE)
[![Commit Activity](https://img.shields.io/github/commit-activity/w/JasonYANG170/AutoCheckBJMF?style=for-the-badge)](https://github.com/JasonYANG170/AutoCheckBJMF/commits/main)
[![Language](https://img.shields.io/github/languages/count/JasonYANG170/AutoCheckBJMF?logo=python&style=for-the-badge)](https://github.com/JasonYANG170/AutoCheckBJMF)

An automated check-in script for "Class Cube" (班级魔方) based on Python. It supports GPS positioning, QR code check-in, and WeCom notifications.

> **Disclaimer**: This program is for educational purposes only. Please comply with local regulations and platform rules. Use at your own risk.

## Features

- ✅ **Multiple Check-in Modes**: Supports QR Code check-in (verified), GPS check-in (verified), and GPS+Photo check-in (verified).
- ✅ **Scheduled Tasks**: Supports daily scheduled check-ins and 24-hour unattended operation.
- ✅ **Location Simulation**: Custom latitude, longitude, and accuracy with random jitter for realistic GPS simulation.
- ✅ **Multi-Account & Multi-Location**: Manage multiple accounts and check-in locations via the GUI.
- ✅ **Notifications**: Supports Enterprise WeChat (WeCom) and PushPlus notifications.
- ✅ **User-Friendly Interface**: Includes a modern GUI built with [Flet](https://flet.dev) for easy configuration.
- ✅ **Cross-Platform**: Runs on Windows, macOS, and Linux.

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

### From Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JasonYANG170/AutoCheckBJMF.git
    cd AutoCheckBJMF
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the application in two modes: **CLI (Command Line Interface)** or **GUI (Graphical User Interface)**.

### GUI Mode (Recommended)

The GUI provides a comprehensive dashboard to manage accounts, locations, tasks, and settings.

```bash
python gui.py
```

1.  **Dashboard**: View the next run time and activity logs.
2.  **Tasks**: Link an Account to a Location to create a check-in task. Enable/Disable tasks as needed.
3.  **Accounts**: Add your Class Cube accounts (Cookie and Class ID required).
4.  **Locations**: Define check-in locations with coordinates (Latitude, Longitude).
5.  **Settings**: Configure global settings like daily schedule time and notification details.

### CLI Mode

The CLI is suitable for server environments or simple setups.

```bash
python main.py
```

- On the first run, if no configuration exists, it will prompt you for a basic setup (one account, one location).
- It will then execute the check-in immediately or wait for the scheduled time.

## Configuration

The application stores data in `config.json`. While you can edit this manually, using the GUI is safer.

**Structure:**

- `accounts`: List of user credentials.
- `locations`: List of coordinate targets.
- `tasks`: Mapping between accounts and locations.
- `scheduletime`: Time string (HH:MM) for daily runs.
- `wecom`: Configuration for Enterprise WeChat notifications.

### Environment Variables (Advanced)

For containerized or headless environments, you can configure the app using environment variables:

- `ClassID`: Class ID
- `MyCookie`: User Cookie (supports multi-line for multiple cookies)
- `X`: Latitude
- `Y`: Longitude
- `SearchTime`: Schedule Time (HH:MM)
- `WECOM_CORPID`, `WECOM_SECRET`, `WECOM_AGENTID`, `WECOM_TOUSER`: WeCom settings.

## Development

### Project Structure

- `core.py`: Core logic for API interaction (`BJMFClient`), configuration (`ConfigManager`), and scheduling (`CheckInManager`).
- `gui.py`: Flet-based graphical user interface.
- `main.py`: Command-line interface entry point.

### Building Executables

You can use PyInstaller to build standalone executables.

**For CLI:**
```bash
pyinstaller --name AutoCheckBJMF_CLI --onefile --clean main.py
```

**For GUI:**
```bash
pyinstaller --name AutoCheckBJMF_GUI --onefile --noconsole --clean gui.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
