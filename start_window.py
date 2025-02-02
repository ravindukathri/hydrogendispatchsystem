import tkinter as tk
import serial.tools.list_ports
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sfc5xxx import Sfc5xxxShdlcDevice
from tkinter import ttk, messagebox

class StartWindow:
    def __init__(self, root, switch_mode_callback):
        self.root = root
        self.switch_mode_callback = switch_mode_callback
        
        self.root.resizable(True, True)  # Allow window resizing
        self.root.title("Start Window")

        # Initialize the COM ports for controllers as None
        self.controller_1_comport = None
        self.controller_2_comport = None

        # USB Select Section
        self.create_usb_selection_section()

        # Mode Buttons Section
        self.create_mode_buttons_section()

        # Exit Button
        self.create_exit_button()

    def create_usb_selection_section(self):
        """Create the USB selection section with dropdowns and confirm button."""
        usb_label = tk.Label(self.root, text="Please select the USB COM ports to proceed.", font=("Arial", 12))
        usb_label.pack(pady=10)

        self.device1_var = tk.StringVar()
        self.device2_var = tk.StringVar()

        tk.Label(self.root, text="MFC 1").pack()
        self.device1_dropdown = ttk.Combobox(self.root, textvariable=self.device1_var, values=self.get_com_ports())
        self.device1_dropdown.pack()

        tk.Label(self.root, text="MFC 2").pack()
        self.device2_dropdown = ttk.Combobox(self.root, textvariable=self.device2_var, values=self.get_com_ports())
        self.device2_dropdown.pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=self.check_com_ports)
        confirm_button.pack(pady=10)

    def get_com_ports(self):
        """Function to get available COM ports."""
        ports = serial.tools.list_ports.comports()
        com_ports = [port.device for port in ports]
        return com_ports

    def check_com_ports(self):
        """Check if both COM ports are selected, verify serial numbers, and assign to controllers."""
        device1 = self.device1_var.get()
        device2 = self.device2_var.get()

        # Check if both COM ports are selected
        if not device1 or not device2:
            messagebox.showerror("Error", "Please select COM ports for both devices.")
            self.set_mode_buttons_state(tk.DISABLED)  # Keep buttons disabled
            return
        elif device1 == device2:
            messagebox.showerror("Error", "Device 1 and Device 2 cannot have the same COM port.")
            self.set_mode_buttons_state(tk.DISABLED)  # Keep buttons disabled
            return

        try:
            # Initialize controller assignments as None
            self.controller_1_comport = None
            self.controller_2_comport = None

            # Connect to Device 1 and get the serial number
            with ShdlcSerialPort(port=device1, baudrate=115200) as port1:
                device_1 = Sfc5xxxShdlcDevice(ShdlcConnection(port1), slave_address=0)
                serial_number_1 = device_1.get_serial_number()
                print(f"Device 1 Serial Number: {serial_number_1}")

            # Connect to Device 2 and get the serial number
            with ShdlcSerialPort(port=device2, baudrate=115200) as port2:
                device_2 = Sfc5xxxShdlcDevice(ShdlcConnection(port2), slave_address=0)
                serial_number_2 = device_2.get_serial_number()
                print(f"Device 2 Serial Number: {serial_number_2}")

            # Assign COM ports based on serial numbers
            if serial_number_1 == "24170036":
                self.controller_1_comport = device1
            elif serial_number_1 == "24170038":
                self.controller_2_comport = device1

            if serial_number_2 == "24170036":
                self.controller_1_comport = device2
            elif serial_number_2 == "24170038":
                self.controller_2_comport = device2

            # Check if both controllers have been assigned correctly
            if self.controller_1_comport and self.controller_2_comport:
                print(f"Controller 1 assigned to {self.controller_1_comport}\n"
                      f"Controller 2 assigned to {self.controller_2_comport}")
                self.set_mode_buttons_state(tk.NORMAL)  # Enable buttons on success
            else:
                messagebox.showerror("Error", "Failed to assign both controllers based on the serial numbers.")
                self.set_mode_buttons_state(tk.DISABLED)  # Keep buttons disabled

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to one or both devices.\nError: {str(e)}")
            self.set_mode_buttons_state(tk.DISABLED)  # Keep buttons disabled

    def create_mode_buttons_section(self):
        """Create the section with mode buttons (Manual, Semi-Manual, Automatic)."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # Pass the controller COM ports to the mode functions
        self.manual_button = tk.Button(self.button_frame, text="Calibration / Flushing", width=15, 
                                       command=lambda: self.switch_mode_callback("Manual", self.controller_1_comport, self.controller_2_comport), 
                                       state=tk.DISABLED)
        self.manual_button.grid(row=0, column=0, padx=5)

        self.semi_manual_button = tk.Button(self.button_frame, text="Semi-Manual Mode", width=15, 
                                            command=lambda: self.switch_mode_callback("Semi-Manual", self.controller_1_comport, self.controller_2_comport),
                                            state=tk.DISABLED)
        self.semi_manual_button.grid(row=0, column=1, padx=5)

        self.automatic_button = tk.Button(self.button_frame, text="Automatic Mode", width=15, 
                                          command=lambda: self.switch_mode_callback("Automatic", self.controller_1_comport,self.controller_2_comport), 
                                          state=tk.DISABLED)
        self.automatic_button.grid(row=0, column=2, padx=5)

    def set_mode_buttons_state(self, state):
        """Enable or disable mode buttons."""
        self.manual_button.config(state=state)
        self.semi_manual_button.config(state=state)
        self.automatic_button.config(state=state)

    def create_exit_button(self):
        """Create an exit button at the bottom right corner."""
        exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        exit_button.pack(side="bottom", anchor="se", padx=10, pady=10)
