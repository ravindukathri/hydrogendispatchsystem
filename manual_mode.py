import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controller import FlowController
from hydrogensensor import hydrogen_sensor_voltage, in_min, in_max
import time

class ManualMode:
    def __init__(self, root, back_callback, controller_1_port, controller_2_port):
        self.root = root
        self.back_callback = back_callback
        self.root.resizable(True, True)  # Allow window resizing
        self.root.title("Calibration/Flushing Window") 

        # Initialize flow controllers
        self.controller_1 = FlowController(port=controller_1_port)
        self.controller_2 = FlowController(port=controller_2_port)
        self.controller_1.connect()
        self.controller_2.connect()

        self.create_manual_mode_window()

    def create_manual_mode_window(self):

        # Add row with text and buttons
        row_frame = tk.Frame(self.root)
        row_frame.pack(pady=10)

        tk.Label(row_frame, text="Hydrogen Sensor Calibration may take around 3 minutes.").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Button(row_frame, text="Calibrate Hydrogen Sensor", command=self.calibrate_hydrogen_sensor).grid(row=2, column=0, padx=10, pady=10)

        tk.Label(row_frame, text="").grid(row=3, column=0)  # Spacer

        tk.Label(row_frame, text="Flushing the system may take around 20 seconds.").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        tk.Button(row_frame, text="Flush the System", command=self.flush_system).grid(row=5, column=0, padx=10, pady=10)
        
        tk.Label(row_frame, text="").grid(row=6, column=0)  # Spacer
        tk.Label(row_frame, text="").grid(row=7, column=0)  # Spacer

        self.back_button = tk.Button(row_frame, text="Back", command=self.back_callback)
        self.back_button.grid(row=8, column=0, padx=10, pady=10)

    def calibrate_hydrogen_sensor(self):
        def calibration_process():
            self.back_button.config(state="disabled")
            # Step 1: Show initial message
            if messagebox.showinfo("Calibration", "Please remove the outlet from the testing setup") == "ok":

                # Step 2: Apply flow rates for initial calibration
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(500)
                time.sleep(30)

                # Step 3: Apply new flow rates
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(100)
                time.sleep(60)

                # Step 4: Collect minimum values
                minimum_value_array = []
                for _ in range(100):
                    minimum_value_array.append(hydrogen_sensor_voltage())
                    time.sleep(0.1)
                min_avg = sum(minimum_value_array) / len(minimum_value_array)
                print(f"Minimum Average Value: {min_avg}")

                # Step 5: Change flow rates
                self.controller_1.set_flow_rate(100)
                self.controller_2.set_flow_rate(0)
                time.sleep(60)

                # Step 6: Collect maximum values
                maximum_value_array = []
                for _ in range(100):
                    maximum_value_array.append(hydrogen_sensor_voltage())
                    time.sleep(0.1)
                max_avg = sum(maximum_value_array) / len(maximum_value_array)
                print(f"Maximum Average Value: {max_avg}")

                # Step 7: Reset flow rates
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(500)
                time.sleep(10)
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(0)
                time.sleep(5)

                # Step 8: Update sensor calibration values
                global in_min, in_max
                in_min = min_avg
                in_max = max_avg

                # Step 9: Show completion message
                messagebox.showinfo("Calibration", "Hydrogen sensor is successfully calibrated.")

            self.back_button.config(state="normal")

        # Run the calibration process in a separate thread
        threading.Thread(target=calibration_process).start()

    def flush_system(self):
        def flush_process():
            self.back_button.config(state="disabled")
            # Step 1: Show initial message
            if messagebox.showinfo("Flush System", "Please remove the outlet from the testing setup") == "ok":

                # Step 2: Apply flow rates to flush the system
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(500)
                time.sleep(15)

                # Step 3: Set both controllers to 0 and wait
                self.controller_1.set_flow_rate(0)
                self.controller_2.set_flow_rate(0)
                time.sleep(5)

                # Step 4: Show completion message
                messagebox.showinfo("Flush System", "System is flushed.")

            self.back_button.config(state="normal")

        # Run the flush process in a separate thread
        threading.Thread(target=flush_process).start()
