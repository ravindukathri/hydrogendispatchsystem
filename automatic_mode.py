import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controller import FlowController
from hydrogensensor import hydrogen_sensor
import time


class AutomaticMode:
    def __init__(self, root, back_callback, controller_1_port, controller_2_port):
        self.root = root
        self.back_callback = back_callback
        self.root.resizable(True, True)  # Allow window resizing
        self.root.title("Automatic Mode Window")

        self.is_running = False

        # Initialize PID variables
        self.integral = 0
        self.previous_error = 0

        # Initialize flow controllers
        self.controller_1 = FlowController(port=controller_1_port)
        self.controller_2 = FlowController(port=controller_2_port)
        self.controller_1.connect()
        self.controller_2.connect()

        # Set up the UI components
        self.create_automatic_mode_window()

    def create_automatic_mode_window(self):
        # Sequence input fields
        tk.Label(self.root, text="Insert your sequence:").grid(row=0, column=0)
        self.sequence_entry = tk.Entry(self.root)
        self.sequence_entry.grid(row=0, column=1)

        # Flow Setpoint input
        tk.Label(self.root, text="Flow Setpoint:").grid(row=1, column=0)
        self.flow_setpoint_entry = tk.Entry(self.root)
        self.flow_setpoint_entry.insert(0, "100")  # Default flow setpoint value
        self.flow_setpoint_entry.grid(row=1, column=1)

        # Frame to hold buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=2, column=1, columnspan=2, pady=10, sticky="nsew")

        # Verify button
        self.verify_button = tk.Button(button_frame, text="Verify", command=self.verify_sequence)
        self.verify_button.grid(row=0, column=0, padx=5, pady=5)

        # Set and Run button (initially disabled)
        self.run_button = tk.Button(button_frame, text="Set and Run", command=self.start_sequence, state="disabled")
        self.run_button.grid(row=0, column=1, padx=5, pady=5)

        # Stop button
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_controller, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

        # Back button
        self.back_button = tk.Button(button_frame, text="Back", command=self.back_stop_process)
        self.back_button.grid(row=0, column=3, padx=5, pady=5)

        # Frame for PID parameter inputs
        pid_frame = tk.Frame(self.root)
        pid_frame.grid(row=7, column=0, sticky="w", padx=10, pady=10)

        # Kp input
        tk.Label(pid_frame, text="Kp:", width=8, anchor="e").grid(row=0, column=0, sticky="e")
        self.kp_entry = tk.Entry(pid_frame, width=12)
        self.kp_entry.insert(0, "0.395")  # Default Kp value
        self.kp_entry.grid(row=0, column=1, padx=10)

        # Ki input
        tk.Label(pid_frame, text="Ki:", width=8, anchor="e").grid(row=1, column=0, sticky="e")
        self.ki_entry = tk.Entry(pid_frame, width=12)
        self.ki_entry.insert(0, "0.0350")  # Default Ki value
        self.ki_entry.grid(row=1, column=1, padx=10)

        # Kd input
        tk.Label(pid_frame, text="Kd:", width=8, anchor="e").grid(row=2, column=0, sticky="e")
        self.kd_entry = tk.Entry(pid_frame, width=12)
        self.kd_entry.insert(0, "0.1")  # Default Kd value
        self.kd_entry.grid(row=2, column=1, padx=10)

        # Additional frame for data display inside pid_frame
        data_frame = tk.Frame(pid_frame)
        data_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        # Hydrogen PPM Label
        self.hydrogen_ppm = tk.Label(data_frame, text="H2 Concentration:")
        self.hydrogen_ppm.grid(row=0, column=0, sticky="w")

        # Flow rate label
        self.flow_rate_label = tk.Label(data_frame, text="Air Flow:")
        self.flow_rate_label.grid(row=1, column=0, sticky="w")

        # Timer Label
        self.counter_label = tk.Label(data_frame, text="Time Remaining: 00:00")
        self.counter_label.grid(row=2, column=0, sticky="w")

        # Set up the table for displaying sequence
        self.setup_table()

        # Initialize the live plot
        self.fig, self.ax1 = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=3)

        self.line_setpoint, = self.ax1.plot([], [], label="Setpoint", color='blue')
        self.line_measured, = self.ax1.plot([], [], label="Measured Value", color='green')
        self.ax1.set_xlabel("Time Step")
        self.ax1.set_ylabel("Hydrogen Concentration", color='green')
        self.ax1.legend(loc="upper left")

        self.ax2 = self.ax1.twinx()
        self.line_control, = self.ax2.plot([], [], label="Control Signal", color='red')
        self.ax2.set_ylabel("Control Signal (0-250)", color='red')
        self.ax2.legend(loc="upper right")

        # Data for plotting
        self.time_steps = []
        self.setpoints = []
        self.measured_values = []
        self.hydrogen_flowrates = []
        self.sequence = []

        # Start updating sensor data
        self.update_sensor_data()

    def setup_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.grid(row=7, column=1, sticky="nsew", padx=10, pady=10)

        self.columns = ("Row", "Time (min)", "Setpoint")
        self.sequence_table = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        self.sequence_table.heading("Row", text="Row")
        self.sequence_table.heading("Time (min)", text="Time (min)")
        self.sequence_table.heading("Setpoint", text="Setpoint")
        self.sequence_table.column("Row", width=40, anchor="center")
        self.sequence_table.column("Time (min)", width=100, anchor="center")
        self.sequence_table.column("Setpoint", width=100, anchor="center")

        self.y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.sequence_table.yview)
        self.sequence_table.configure(yscrollcommand=self.y_scrollbar.set)

        self.sequence_table.grid(row=0, column=0, sticky="nsew")
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def update_sensor_data(self):
        """Update the hydrogen sensor data and flow rates every 500ms."""
        hydrogen_flow = self.controller_1.get_measured_flow()
        air_flow = self.controller_2.get_measured_flow()

        ppm_value = hydrogen_sensor()
        self.hydrogen_ppm.config(text=f"Hydrogen: {ppm_value:.2f} PPM")

        flow_data = hydrogen_flow + air_flow
        self.flow_rate_label.config(text=f"Total Flow: {flow_data:.2f} SCCM")

        self.root.after(500, self.update_sensor_data)

    def calculate_total_time(self):
        """Calculate the total time in the sequence."""
        total_time = sum(row[0] for row in self.sequence)
        minutes = int(total_time)
        seconds = int((total_time - minutes) * 60)
        self.counter_label.config(text=f"Time Remaining: {minutes:02}:{seconds:02}")
        return total_time * 60  # Return total time in seconds

    def start_timer(self, total_time):
        """Start the countdown timer."""
        if self.is_running and total_time > 0:
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            self.counter_label.config(text=f"Time Remaining: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.start_timer, total_time - 1)
        else:
            self.counter_label.config(text="Process Completed")
            
            
    def verify_sequence(self):
        """Verify the input sequence."""
        input_sequence = self.sequence_entry.get().split(',')
        try:
            sequence = list(map(float, input_sequence))
            if len(sequence) % 2 != 0:
                raise ValueError("Sequence must have an even number of values.")

            for i in range(1, len(sequence), 2):
                if not (0 <= sequence[i] <= 20000):
                    raise ValueError("Setpoint values must be between 0 and 20000.")

            for i in range(0, len(sequence), 2):
                if sequence[i] <= 0:
                    raise ValueError("Time values must be positive.")

            self.sequence = [(sequence[i], sequence[i + 1]) for i in range(0, len(sequence), 2)]
            self.run_button.config(state="normal")

            for row in self.sequence_table.get_children():
                self.sequence_table.delete(row)
            for idx, (time_val, setpoint) in enumerate(self.sequence, start=1):
                self.sequence_table.insert("", "end", values=(idx, time_val, setpoint))

            self.calculate_total_time()

            tk.messagebox.showinfo("Verification", "Verification successful!")
        except ValueError as e:
            tk.messagebox.showerror("Verification Error", str(e))
            self.run_button.config(state="disabled")

    def start_sequence(self):
        """Run the sequence according to the verified time and setpoints."""
        if not self.is_running:
            self.kp = float(self.kp_entry.get())
            self.ki = float(self.ki_entry.get())
            self.kd = float(self.kd_entry.get())

            self.flow_setpoint = int(self.flow_setpoint_entry.get())

            self.is_running = True
            self.stop_button.config(state="normal")
            self.control_thread = threading.Thread(target=self.run_sequence)
            self.control_thread.start()

            total_time = self.calculate_total_time()
            self.start_timer(total_time)

    def run_sequence(self):
        """Execute each (time, setpoint) pair in the sequence with the PID control loop."""
        for time_val, setpoint in self.sequence:
            if not self.is_running:
                break

            self.setpoint = setpoint

            self.run_for_duration(time_val)

        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)
        tk.messagebox.showinfo("Completion", "Testing completed")
        self.is_running = False


    def run_for_duration(self, minutes):
        """Run the PID control loop for the specified duration in minutes."""
        end_time = time.time() + minutes * 60  # Convert minutes to seconds

        while time.time() < end_time and self.is_running:
            measured_value = hydrogen_sensor()
            

            # Calculate control signal using PID algorithm to match the current setpoint
            control_signal = self.pid_controller(self.setpoint, measured_value)
            
            # Calculate flow rates for both controllers based on control signal
            hydrogen_flowrate = (self.flow_setpoint / 100) * control_signal
            air_flowrate = self.flow_setpoint - hydrogen_flowrate
            
            #print(f"H2 Flowrate: {hydrogen_flowrate}")
            
            # Apply flow rates to the controllers
            self.controller_1.set_flow_rate(hydrogen_flowrate)
            self.controller_2.set_flow_rate(air_flowrate)

            # Update live plot with current data
            self.time_steps.append(len(self.time_steps))
            self.setpoints.append(self.setpoint)
            self.measured_values.append(measured_value)
            self.hydrogen_flowrates.append(hydrogen_flowrate)

            # Limit display range to the last 300 points
            display_range = 500
            time_data = self.time_steps[-display_range:]
            setpoint_data = self.setpoints[-display_range:]
            measured_data = self.measured_values[-display_range:]
            hydrogen_flowrate_data = self.hydrogen_flowrates[-display_range:]

            # Update plot lines
            self.line_setpoint.set_data(time_data, setpoint_data)
            self.line_measured.set_data(time_data, measured_data)
            self.line_control.set_data(time_data, hydrogen_flowrate_data)

            # Rescale plot axes
            if len(time_data) > 1:
                self.ax1.set_xlim(min(time_data), max(time_data))
            else:
                self.ax1.set_xlim(0, 1)  # Default range when there is only one data point
            
            # Rescale plot axes
            
            max_measured = max(self.measured_values)
            max_setpoint = max(self.setpoints)
            
            max_data = max(max_measured, max_setpoint)
            
            self.ax1.set_xlim(min(time_data), max(time_data))
            self.ax1.set_ylim(0, max_data * 1.2)  # Adjust Y-axis as needed
            self.ax2.set_ylim(0, 250)  # Control signal range

            # Draw the plot
            self.canvas.draw()
            
            
            
    

    def stop_controller(self):
        self.is_running = False
        self.counter_label.config(text="Process Completed")
        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)

    def back_stop_process(self):
        self.is_running = False
        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)
        self.root.after_cancel(self.update_sensor_data)  # Cancel periodic updates
        self.back_callback()
        
    def pid_controller(self, setpoint, measured_value):
        """Calculate the control signal using PID."""
        error = setpoint - measured_value
        
        kp = self.kp
        ki = self.ki
        kd = self.kd
        
        #print(f"{kp} | {ki} | {kd}")
        
        proportional = self.kp * error
        self.integral += error
        integral = self.ki * self.integral
        derivative = self.kd * (error - self.previous_error)
        self.previous_error = error

        # PID output
        output = proportional + integral + derivative

        # Scale output to be within 0–100 range
        scaled_output = max(0, min(100, output / 200))
        return scaled_output



















