import tkinter as tk
import time
from tkinter import ttk, messagebox, filedialog
from controller import FlowController
from hydrogensensor import hydrogen_sensor
from flowsensor import read_flow_sensor
import threading

class SemiManualMode:
    def __init__(self, root, back_callback, controller_1_port, controller_2_port):
        self.root = root
        self.back_callback = back_callback

        self.root.resizable(True, True)
        self.root.title("Semi-Manual Mode Window")

        self.verified_numbers = []
        self.process_active = False
        self.current_time_value = 0
        self.total_time_seconds = 0
        self.elapsed_time = 0
        self.uploaded_numbers = None

        self.controller_1 = FlowController(port=controller_1_port)
        self.controller_2 = FlowController(port=controller_2_port)

        self.controller_1.connect()
        self.controller_2.connect()

        self.columns = ("Time Slot", "Time", "Hydrogen Flowrate", "Air Flowrate")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.radio_frame = tk.Frame(self.frame)
        self.radio_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.input_option = tk.IntVar(value=1)
        manual_radio = tk.Radiobutton(self.radio_frame, text="Enter the inputs", variable=self.input_option, value=1, command=self.select_input_source)
        upload_radio = tk.Radiobutton(self.radio_frame, text="Upload the inputs", variable=self.input_option, value=2, command=self.select_input_source)
        manual_radio.grid(row=0, column=0, padx=10, pady=5)
        upload_radio.grid(row=0, column=1, padx=10, pady=5)

        self.label = tk.Label(self.frame, text="Enter Time and Flowrate data (comma-separated):", anchor="w", justify="left")
        self.label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.entry = tk.Entry(self.frame, width=50)
        self.entry.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.upload_button = tk.Button(self.frame, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="n")
        self.upload_button.grid_remove()

        self.verify_button = tk.Button(self.frame, text="Verify the sequence", command=self.verify_numbers)
        self.verify_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        self.button_frame = tk.Frame(self.frame)
        self.button_frame.grid(row=9, column=0, sticky="w", padx=10, pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Process", state=tk.DISABLED, command=self.start_process)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.emergency_button = tk.Button(self.button_frame, text="Emergency Stop", state=tk.DISABLED, command=self.emergency_stop)
        self.emergency_button.grid(row=0, column=1, padx=10, pady=10)

        back_button = tk.Button(self.button_frame, text="Back", command=self.stop_and_back)
        back_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        self.data_frame = tk.Frame(self.frame)
        self.data_frame.grid(row=5, column=0, sticky="w", padx=10, pady=10)

        self.countdown_label = tk.Label(self.data_frame, text=" ")
        self.countdown_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.total_time_label = tk.Label(self.data_frame, text="Total time remaining: 00:00")
        self.total_time_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.hydrogen_label = tk.Label(self.data_frame, text="Hydrogen flow rate: 0 sccm")
        self.hydrogen_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.air_label = tk.Label(self.data_frame, text="Synthetic air flow rate: 0 sccm")
        self.air_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.hydrogen_ppm = tk.Label(self.data_frame, text="H2 Concentration: 0 PPM")
        self.hydrogen_ppm.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.flow_rate_label = tk.Label(self.data_frame, text="Air Flow SCCM")
        self.flow_rate_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.setup_table()

        self.progress_bar = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = 100

    def setup_table(self):
        self.table = ttk.Treeview(self.frame, columns=self.columns, show="headings")
        self.y_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=self.y_scrollbar.set)

        for col in self.columns:
            self.table.heading(col, text=col)

        self.table.column("Time Slot", width=80, anchor="center")
        self.table.column("Time", width=100, anchor="center")
        self.table.column("Hydrogen Flowrate", width=120, anchor="center")
        self.table.column("Air Flowrate", width=120, anchor="center")

        self.table.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        self.y_scrollbar.grid(row=4, column=3, sticky="ns")

    def select_input_source(self):
        if self.input_option.get() == 1:
            self.label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")
            self.entry.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
            self.entry.config(state=tk.NORMAL)
            self.upload_button.grid_remove()
        elif self.input_option.get() == 2:
            self.label.grid_remove()
            self.entry.grid_remove()
            self.upload_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="n")
        self.verify_button.config(state=tk.NORMAL)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.uploaded_numbers = file.read().strip()
                    if not self.uploaded_numbers:
                        raise ValueError("File is empty.")
                messagebox.showinfo("File Uploaded", "File uploaded successfully!")
                self.verify_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("File Error", f"Error reading file: {str(e)}")

    def verify_numbers_logic(self, numbers):
        try:
            num_list = [float(x) for x in numbers.split(',')]
        except ValueError:
            raise ValueError("Invalid input, must be numbers separated by commas.")

        if len(num_list) % 3 != 0:
            raise ValueError("Number of inputs must be divisible by 3.")

        for i in range(1, len(num_list), 3):
            hydrogen = num_list[i]
            air = num_list[i + 1]
            if hydrogen > 500 or air > 500:
                raise ValueError(f"Flowrates exceed limit at set {i//3 + 1}.")

        return num_list

    def verify_numbers(self):
        numbers = self.uploaded_numbers if self.input_option.get() == 2 else self.entry.get()
        try:
            self.verified_numbers = self.verify_numbers_logic(numbers)
            self.display_table(self.verified_numbers)
            self.total_time_seconds = sum(int(self.verified_numbers[i] * 60) for i in range(0, len(self.verified_numbers), 3))
            self.elapsed_time = 0
            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = self.total_time_seconds
            self.start_button.config(state=tk.NORMAL, bg="green", fg="white")
            messagebox.showinfo("Attention", "Please make sure that both values are open.")
        except ValueError as e:
            self.clear_table()
            messagebox.showerror("Input Error", str(e))
            self.start_button.config(state=tk.DISABLED)

    def display_table(self, num_list):
        self.clear_table()
        for i in range(0, len(num_list), 3):
            time_slot = i // 3 + 1
            time = num_list[i]
            hydrogen = num_list[i + 1]
            air = num_list[i + 2]
            self.table.insert("", "end", values=(time_slot, time, hydrogen, air))

    def clear_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def update_flow_labels(self, hydrogen_flow, air_flow, ppm_value, total_flow):
        self.hydrogen_label.config(text=f"H2 flow rate: {hydrogen_flow:.2f} sccm")
        self.air_label.config(text=f"Air flow rate: {air_flow:.2f} sccm")
        self.hydrogen_ppm.config(text=f"H2 Concentration: {ppm_value:.2f} PPM")
        self.flow_rate_label.config(text=f"Total Flow : {total_flow:.2f} SCCM")

    def start_monitoring_flow(self):
        self.monitoring_active = True

        def sensor_loop():
            while self.monitoring_active:
                try:
                    hydrogen_flow = self.controller_1.get_measured_flow()
                    air_flow = self.controller_2.get_measured_flow()
                    ppm_value = hydrogen_sensor()
                    total_flow = hydrogen_flow + air_flow
                    self.root.after(0, self.update_flow_labels, hydrogen_flow, air_flow, ppm_value, total_flow)
                except Exception as e:
                    print(f"[Monitoring Error] {e}")
                    self.monitoring_active = False
                    break
                time.sleep(0.5)

        thread = threading.Thread(target=sensor_loop, daemon=True)
        thread.start()

    def continuous_process_loop(self):
        if not self.process_active:
            return

        self.elapsed_time += 1
        self.progress_bar["value"] = self.elapsed_time

        total_mins, total_secs = divmod(self.total_time_seconds - self.elapsed_time, 60)
        self.total_time_label.config(text=f"Total time remaining: {total_mins:02d}:{total_secs:02d}")

        if self.current_time_value < len(self.time_schedule):
            start_time, hydrogen, air = self.time_schedule[self.current_time_value]
            if self.elapsed_time == start_time:
                print(f"[Sequence Switch] Time: {start_time}s | H2: {hydrogen} sccm | Air: {air} sccm")
                try:
                    self.set_flow_rate_with_retries(self.controller_1, hydrogen)
                    self.set_flow_rate_with_retries(self.controller_2, air)
                    self.current_time_value += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to set flowrates: {e}")
                    self.stop_process()
                    return

        if self.elapsed_time >= self.total_time_seconds:
            self.stop_process()
            return

        self.root.after(1000, self.continuous_process_loop)

    def start_process(self):
        if not self.verified_numbers or self.process_active:
            return

        self.process_active = True
        self.start_button.config(state=tk.DISABLED, bg="white", fg="black")
        self.verify_button.config(state=tk.DISABLED)
        self.emergency_button.config(state=tk.NORMAL, bg="red", fg="white")

        self.elapsed_time = 0
        self.current_time_value = 0
        self.time_schedule = []
        current_start = 0

        for i in range(0, len(self.verified_numbers), 3):
            duration = int(self.verified_numbers[i] * 60)
            hydrogen = self.verified_numbers[i + 1]
            air = self.verified_numbers[i + 2]
            self.time_schedule.append((current_start, hydrogen, air))
            current_start += duration

        self.total_time_seconds = current_start
        self.progress_bar["maximum"] = self.total_time_seconds

        # Set initial flowrate immediately
        if self.time_schedule:
            first_start, hydrogen, air = self.time_schedule[0]
            print(f"[Initial Set] H2: {hydrogen} sccm | Air: {air} sccm")
            try:
                self.set_flow_rate_with_retries(self.controller_1, hydrogen)
                self.set_flow_rate_with_retries(self.controller_2, air)
                self.current_time_value = 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set initial flowrates: {e}")
                self.stop_process()
                return

        self.start_monitoring_flow()
        self.continuous_process_loop()

    def emergency_stop(self):
        if messagebox.askokcancel("Emergency Stop", "Are you sure you want to stop the process?"):
            self.stop_process()

    def stop_process(self):
        self.monitoring_active = False
        self.process_active = False
        self.start_button.config(state=tk.NORMAL)
        self.emergency_button.config(state=tk.DISABLED)

        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)

        self.hydrogen_label.config(text="Hydrogen flow rate: 0 sccm")
        self.air_label.config(text="Synthetic air flow rate: 0 sccm")
        self.hydrogen_ppm.config(text="H2 Concentration: 0 PPM")

        self.countdown_label.config(text="Process Completed")
        self.total_time_label.config(text="Total time remaining: 00:00")
        self.progress_bar["value"] = 0
        self.verify_button.config(state=tk.NORMAL)
        messagebox.showinfo("Process Complete", "Testing Completed")

    def stop_and_back(self):
        self.monitoring_active = False
        self.stop_process()
        self.back_callback()

    def set_flow_rate_with_retries(self, controller, flow_rate, retries=3, delay=1):
        for attempt in range(retries):
            try:
                controller.set_flow_rate(flow_rate)
                return
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error setting flow rate on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise ConnectionError(f"Failed to set flow rate after {retries} attempts: {e}")
