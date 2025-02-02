import subprocess
import sys
import os
import time
import threading
import tkinter as tk
import serial

# Path to requirements file and virtual environment
requirements_path = "requirements.txt"
venv_path = "venv"

# Function to check if the script is running in the virtual environment
def is_virtual_env():
    return os.environ.get("VIRTUAL_ENV") is not None

# Function to activate the virtual environment and restart the script
def activate_and_restart_in_venv():
    if not is_virtual_env():
        print("Activating the virtual environment and restarting...")
        # Restart the script within the virtual environment using bash
        activate_script = os.path.join(venv_path, "bin", "activate")
        command = f"bash -c 'source {activate_script} && python {sys.argv[0]}'"
        subprocess.call(command, shell=True)
        sys.exit()  # Exit the current process after spawning the new one

# Install packages from requirements.txt
def install_packages_from_requirements():
    try:
        with open(requirements_path, "r") as file:
            required_packages = [line.strip() for line in file if line.strip() and not line.startswith("#")]
        for package in required_packages:
            try:
                __import__(package.split('==')[0])  # Check only the package name without version
            except ImportError:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("All required libraries are installed.")
    except FileNotFoundError:
        print(f"{requirements_path} not found. Please make sure it exists.")
        sys.exit(1)

# Check if in virtual environment and install packages
activate_and_restart_in_venv()
install_packages_from_requirements()

# Import custom modules
import automatic_mode
import controller
import manual_mode
import semi_manual_mode
import start_window

# Define a placeholder or actual switch_mode_callback function
def switch_mode_callback(mode):
    print(f"Switching to mode: {mode}")
    # Implement mode switching logic if needed

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Application")
        #self.root.geometry("400x300")
        self.show_start_window()

    def show_start_window(self):
        """Display the start window."""
        self.clear_window()
        start_window.StartWindow(self.root, self.switch_to_mode)

    def switch_to_mode(self, mode, controller_1_port=None, controller_2_port=None):
        """Switch to the selected mode (Manual, Semi-Manual, Automatic)."""
        if mode == "Manual":
            self.load_manual_mode(controller_1_port, controller_2_port)
        elif mode == "Semi-Manual":
            self.load_semi_manual_mode(controller_1_port, controller_2_port)
        elif mode == "Automatic":
            self.load_automatic_mode(controller_1_port, controller_2_port)

    def load_manual_mode(self, controller_1_port, controller_2_port):
        """Load Manual Mode window."""
        self.clear_window()
        manual_mode.ManualMode(self.root, self.show_start_window,  controller_1_port, controller_2_port)

    def load_semi_manual_mode(self, controller_1_port, controller_2_port):
        """Load Semi-Manual Mode window."""
        self.clear_window()
        semi_manual_mode.SemiManualMode(self.root, self.show_start_window, controller_1_port, controller_2_port)

    def load_automatic_mode(self, controller_1_port, controller_2_port):
        """Load Automatic Mode window."""
        self.clear_window()
        automatic_mode.AutomaticMode(self.root, self.show_start_window, controller_1_port, controller_2_port)

    def clear_window(self):
        """Clear the existing window content."""
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    print("Starting the main application...")
    
    # Initialize the main application window
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()









# import tkinter as tk
# from start_window import StartWindow

# class MainApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Main Application")
#         #self.root.geometry("400x300")
#         self.show_start_window()

#     def show_start_window(self):
#         """Display the start window."""
#         self.clear_window()
#         StartWindow(self.root, self.switch_to_mode)

#     def switch_to_mode(self, mode, controller_1_port=None, controller_2_port=None):
#         """Switch to the selected mode (Manual, Semi-Manual, Automatic)."""
#         if mode == "Manual":
#             self.load_manual_mode(controller_1_port)
#         elif mode == "Semi-Manual":
#             self.load_semi_manual_mode(controller_1_port, controller_2_port)
#         elif mode == "Automatic":
#             self.load_automatic_mode(controller_1_port)

#     def load_manual_mode(self, controller_1_port):
#         """Load Manual Mode window."""
#         self.clear_window()
#         import manual_mode
#         manual_mode.ManualMode(self.root, self.show_start_window, controller_1_port)

#     def load_semi_manual_mode(self, controller_1_port, controller_2_port):
#         """Load Semi-Manual Mode window."""
#         self.clear_window()
#         import semi_manual_mode
#         semi_manual_mode.SemiManualMode(self.root, self.show_start_window, controller_1_port, controller_2_port)

#     def load_automatic_mode(self, controller_1_port):
#         """Load Automatic Mode window."""
#         self.clear_window()
#         import automatic_mode
#         automatic_mode.AutomaticMode(self.root, self.show_start_window, controller_1_port)

#     def clear_window(self):
#         """Clear the existing window content."""
#         for widget in self.root.winfo_children():
#             widget.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = MainApp(root)
#     root.mainloop()



#Original Code 

# import tkinter as tk
# from start_window import StartWindow

# class MainApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Main Application")
#         #self.root.geometry("400x300")
#         self.show_start_window()

#     def show_start_window(self):
#         """Display the start window."""
#         self.clear_window()
#         StartWindow(self.root, self.switch_to_mode)

#     def switch_to_mode(self, mode, controller_1_port=None, controller_2_port=None):
#         """Switch to the selected mode (Manual, Semi-Manual, Automatic)."""
#         if mode == "Manual":
#             self.load_manual_mode(controller_1_port)
#         elif mode == "Semi-Manual":
#             self.load_semi_manual_mode(controller_1_port, controller_2_port)
#         elif mode == "Automatic":
#             self.load_automatic_mode(controller_1_port)

#     def load_manual_mode(self, controller_1_port):
#         """Load Manual Mode window."""
#         self.clear_window()
#         import manual_mode
#         manual_mode.ManualMode(self.root, self.show_start_window, controller_1_port)

#     def load_semi_manual_mode(self, controller_1_port, controller_2_port):
#         """Load Semi-Manual Mode window."""
#         self.clear_window()
#         import semi_manual_mode
#         semi_manual_mode.SemiManualMode(self.root, self.show_start_window, controller_1_port, controller_2_port)

#     def load_automatic_mode(self, controller_1_port):
#         """Load Automatic Mode window."""
#         self.clear_window()
#         import automatic_mode
#         automatic_mode.AutomaticMode(self.root, self.show_start_window, controller_1_port)

#     def clear_window(self):
#         """Clear the existing window content."""
#         for widget in self.root.winfo_children():
#             widget.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = MainApp(root)
#     root.mainloop()
