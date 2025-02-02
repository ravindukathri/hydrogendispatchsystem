
# SemiOriginal Project

This project provides a user interface application to manage and control various modes, including automatic, manual, and semi-manual modes. It leverages Tkinter for the GUI and includes support for serial communication. The program checks and installs required dependencies from `requirements.txt`, ensuring all necessary libraries are available.

## Features

- **Mode Management**: Switch between automatic, manual, and semi-manual modes.
- **Dependency Management**: Automatically checks and installs required libraries from `requirements.txt`.
- **Virtual Environment Support**: Ensures the program runs within a virtual environment, making installation and execution consistent and isolated from system libraries.
- **User Interface**: Built using Tkinter for interactive graphical controls.

## Installation

### Step 1: Clone the Repository
Clone this project from GitHub:
```bash
git clone https://github.com/yourusername/SemiOriginal.git
cd SemiOriginal
```

### Step 2: Set Up the Virtual Environment
To create a virtual environment in the project directory:
```bash
python3 -m venv venv
```

### Step 3: Install Project Dependencies
If you prefer to install dependencies manually within the virtual environment, follow these steps:

1. **Activate the virtual environment**:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
 
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

Alternatively, the dependencies will be installed automatically the first time you run `main.py`.

## How to Run

Navigate to the project directory and run `main.py`:

```bash
cd /path/to/SemiOriginal
python main.py
```

- **Automatic Setup**: When you run `main.py`, the script will automatically activate the virtual environment and install all required libraries listed in `requirements.txt` if they are not already installed.
- **Startup Confirmation**: After all dependencies are installed, you will see a confirmation message, and the main application interface will start.

**Note**: The first run may take longer due to initial setup.

## Usage

1. **Starting the Application**: Run `python main.py` from the terminal. The program will handle dependency installation and virtual environment activation automatically.
2. **Switch Modes**: Use the GUI to toggle between different operational modes (automatic, manual, and semi-manual).
3. **Serial Communication**: The program is compatible with serial devices through the `pyserial` library.

## Requirements

The application dependencies are managed in `requirements.txt`. The main libraries used include:

- **Tkinter** for the GUI (often pre-installed with Python).
- **Pyserial** for serial communication.
- **Sensirion SHDLC** drivers (if applicable).

Dependencies are automatically installed when running `main.py`.

## Troubleshooting

- **Virtual Environment Activation Issues**: If the virtual environment does not activate, ensure that you have `venv` installed:
  ```bash
  sudo apt install python3-venv
  ```
  Then recreate the environment with:
  ```bash
  python3 -m venv venv
  ```

- **Missing Dependencies**: If any required libraries are missing, ensure `requirements.txt` is in the project directory and is formatted correctly. Re-run `main.py` to install missing packages.

- **Permission Errors**: If you encounter permission issues, you may need to use `sudo` or verify that your Python environment has appropriate permissions.

## File Structure

- `main.py`: Main entry point of the application. Manages virtual environment activation and dependency checks.
- `automatic_mode.py`, `manual_mode.py`, `semi_manual_mode.py`, `start_window.py`: Modules defining different operational modes and the main GUI window.
- `requirements.txt`: Lists the necessary dependencies for the project.


