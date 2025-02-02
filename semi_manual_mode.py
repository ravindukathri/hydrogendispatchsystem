import tkinter as tk
import time
from tkinter import ttk, messagebox, filedialog
from controller import FlowController  # Import FlowController
from hydrogensensor import hydrogen_sensor #Import Hydrogen Sensor
from flowsensor import read_flow_sensor
import threading

class SemiManualMode:
    def __init__(self, root, back_callback, controller_1_port, controller_2_port):
        self.root = root
        self.back_callback = back_callback
        
        self.root.resizable(True, True)  # Allow window resizing
        self.root.title("Semi-Manual Mode Window")

        self.verified_numbers = []
        self.process_active = False
        self.current_time_value = 0
        self.total_time_seconds = 0
        self.elapsed_time = 0  # Track the time elapsed
        self.uploaded_numbers = None
        self.i = 0  # Initialize i as a class attribute

        # Initialize flow controllers
        self.controller_1 = FlowController(port=controller_1_port)
        self.controller_2 = FlowController(port=controller_2_port)

        # Connect to both controllers
        self.controller_1.connect()
        self.controller_2.connect()

        self.columns = ("Time Slot", "Time", "Hydrogen Flowrate", "Air Flowrate")

        # Create the layout with a frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)
        
        self.radio_frame = tk.Frame(self.frame)
        self.radio_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)  # Correct usage

        # Input option variables and selection
        self.input_option = tk.IntVar(value=1)  # Default to manual entry
        manual_radio = tk.Radiobutton(self.radio_frame, text="Enter the inputs", variable=self.input_option, value=1, command=self.select_input_source)
        upload_radio = tk.Radiobutton(self.radio_frame, text="Upload the inputs", variable=self.input_option, value=2, command=self.select_input_source)
        manual_radio.grid(row=0, column=0, padx=10, pady=5)
        upload_radio.grid(row=0, column=1, padx=10, pady=5)

        # Manual input fields
        self.label = tk.Label(self.frame, text="Enter Time and Flowrate data (comma-separated):", anchor="w", justify="left")
        self.label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.entry = tk.Entry(self.frame, width=50)
        self.entry.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Upload button (hidden initially)
        self.upload_button = tk.Button(self.frame, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="n")
        self.upload_button.grid_remove()  # Hide by default

        # Verify button
        self.verify_button = tk.Button(self.frame, text="Verify the sequence", command=self.verify_numbers)
        self.verify_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="n")


        self.button_frame = tk.Frame(self.frame)
        self.button_frame.grid(row=9, column=0, sticky="w", padx=10, pady=10)  # Correct usage
        
        # Start, emergency stop, and exit buttons
        self.start_button = tk.Button(self.button_frame, text="Start Process", state=tk.DISABLED, command=self.start_process)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.emergency_button = tk.Button(self.button_frame, text="Emergency Stop", state=tk.DISABLED, command=self.emergency_stop)
        self.emergency_button.grid(row=0, column=1, padx=10, pady=10)

        # Back button in the bottom-right corner
        back_button = tk.Button(self.button_frame, text="Back", command=self.stop_and_back)
        back_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        
        
        self.data_frame = tk.Frame(self.frame)
        self.data_frame.grid(row=5, column=0, sticky="w", padx=10, pady=10)  # Correct usage

        
        # Countdown and flow rate labels
        self.countdown_label = tk.Label(self.data_frame, text=" ")
        self.countdown_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.total_time_label = tk.Label(self.data_frame, text="Total time remaining: 00:00")
        self.total_time_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.hydrogen_label = tk.Label(self.data_frame, text="Hydrogen flow rate: 0 sccm")
        self.hydrogen_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.air_label = tk.Label(self.data_frame, text="Synthetic air flow rate: 0 sccm")
        self.air_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        #Labels for Hydrogen PPM and Total Flow Rate
        self.hydrogen_ppm = tk.Label(self.data_frame, text="H2 Concentration: 0 PPM")
        self.hydrogen_ppm.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.flow_rate_label = tk.Label(self.data_frame, text="Air Flow SCCM")
        self.flow_rate_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Setup the table with a vertical scrollbar
        self.setup_table()

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
        self.progress_bar["value"] = 0  # Start at 0
        self.progress_bar["maximum"] = 100  # Default maximum; will be adjusted

    def setup_table(self):
        """Set up the table with a vertical scrollbar."""
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
        """Handle the input source selection (manual entry or file upload)."""
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
        """Handle file upload functionality."""
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
        """Logic to verify numbers without GUI interaction."""
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
        """Verify numbers and display in the table."""
        numbers = ""
        if self.input_option.get() == 2:
            if self.uploaded_numbers is None:
                messagebox.showerror("Input Error", "No file uploaded. Please upload a file.")
                return
            numbers = self.uploaded_numbers
        else:
            numbers = self.entry.get()

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
        """Display the numbers in a table."""
        self.clear_table()
        for i in range(0, len(num_list), 3):
            time_slot = i // 3 + 1
            time = num_list[i]
            hydrogen = num_list[i + 1]
            air = num_list[i + 2]
            self.table.insert("", "end", values=(time_slot, time, hydrogen, air))

    def clear_table(self):
        """Clear the table content."""
        for row in self.table.get_children():
            self.table.delete(row)

    def set_flow_rate_with_retries(self, controller, flow_rate, retries=3, delay=1):
        """Attempt to set the flow rate with retries and handle timeouts."""
        for attempt in range(retries):
            try:
                controller.set_flow_rate(flow_rate)
                return
            except KeyboardInterrupt:
                print("Process interrupted manually.")
                raise
            except Exception as e:
                print(f"Error setting flow rate on attempt {attempt + 1}: {e}")
                if "timeout" in str(e).lower():
                    print("Timeout detected, retrying...")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise ConnectionError(f"Failed to set flow rate after {retries} attempts: {e}")

    def process_set(self, index):
        """Combined process flow and countdown."""
        print('Process Set, Started')

        # Check if the process is active and index is valid
        if not self.process_active or index >= len(self.verified_numbers):
            self.stop_process()
            print('Process Set, Stopped')
            return

        print(f'Time Slot: {self.i}')
        self.i += 1

        # Extract time duration, hydrogen flowrate, and air flowrate
        time_duration = self.verified_numbers[index]
        hydrogen_flowrate = self.verified_numbers[index + 1]
        air_flowrate = self.verified_numbers[index + 2]

        try:
            # Set hydrogen flow rate on controller 1
            print('Start setting controller 1')
            self.set_flow_rate_with_retries(self.controller_1, hydrogen_flowrate)
            print('Finished setting controller 1')

            # Set air flow rate on controller 2
            print('Start setting controller 2')
            self.set_flow_rate_with_retries(self.controller_2, air_flowrate)
            print('Finished setting controller 2')

            # Small delay to stabilize flow rates before monitoring
            time.sleep(0.5)
        except Exception as e:
            # If an error occurs, stop the process and display the error message
            messagebox.showerror("Connection or Value Error", "Please check the connection and values!")
            self.stop_process()
            return

        # Start flow monitoring if setting flow rates was successful
        print('Process Set, Started Flow Monitoring')
        self.start_monitoring_flow()

        # Run the countdown and proceed to the next set
        time_in_seconds = int(time_duration * 60)
        self.run_countdown(time_in_seconds, lambda: self.process_set(index + 3))

    def start_monitoring_flow(self):
        """Monitor the actual flow rates and update the GUI every 500ms."""

        # Flag to control the monitoring loop
        self.monitoring_active = True
    
        def update_flow_rates():
            if not self.monitoring_active:
                return  # Exit if monitoring is inactive
    
            try:
                # Get measured flow rates
                hydrogen_flow = self.controller_1.get_measured_flow()
                air_flow = self.controller_2.get_measured_flow()
    
                # Update the labels with the flow data
                self.hydrogen_label.config(text=f"H2 flow rate: {hydrogen_flow:.2f} sccm")
                self.air_label.config(text=f"Air flow rate: {air_flow:.2f} sccm")
    
                # Get hydrogen sensor reading and update the label
                ppm_value = hydrogen_sensor()
                self.hydrogen_ppm.config(text=f"H2 Concentration: {ppm_value:.2f} PPM")
    
                # Calculate total flow and update the label
                flow_data = hydrogen_flow + air_flow
                self.flow_rate_label.config(text=f"Total Flow : {flow_data:.2f} SCCM")
    
            except Exception as e:
                print(f"Error updating flow rates: {e}")
                #messagebox.showerror("Error", "Failed to update flow rates. Check sensor connections.")
                self.monitoring_active = False  # Stop monitoring on error
                return
    
            # Schedule the next update in 500ms
            self.root.after(500, update_flow_rates)
    
        # Start the monitoring in a single background thread
        monitoring_thread = threading.Thread(target=update_flow_rates)
        monitoring_thread.daemon = True  # Ensures thread exits with the program
        monitoring_thread.start()

    def run_countdown(self, seconds, callback):
        """Countdown handler."""
        if seconds > 0 and self.process_active:
            mins, secs = divmod(seconds, 60)
            self.countdown_label.config(text=f"Time remaining (section): {mins:02d}:{secs:02d}")
            self.elapsed_time += 1
            self.progress_bar["value"] = self.elapsed_time
            self.root.after(1000, self.run_countdown, seconds - 1 , callback)  
            total_mins, total_secs = divmod(self.total_time_seconds - self.elapsed_time, 60)
            self.total_time_label.config(text=f"Total time remaining: {total_mins:02d}:{total_secs:02d}")
        elif self.process_active:
            callback()

    def start_process(self):
        """Start process handler."""
        if not self.verified_numbers or self.process_active:
            return

        self.process_active = True
        self.start_button.config(state=tk.DISABLED, bg="white", fg="black")
        self.verify_button.config(state=tk.DISABLED)
        self.emergency_button.config(state=tk.NORMAL, bg="red", fg="white")

        self.elapsed_time = 0
        self.total_time_seconds = sum(int(self.verified_numbers[i] * 60) for i in range(0, len(self.verified_numbers), 3))
        
        print('Start Process Executed, Next to Process Set')
        
        self.i = 1
        self.process_set(0)

    def stop_and_back(self):
        """Stop the process and navigate back."""
        self.monitoring_active = False  # Stop monitoring on error
        self.back_stop_process()  # Ensure the process stops
        self.back_callback()  # Navigate back to the previous screen
    
    def back_stop_process(self):
        
        """Stop process and reset flow rates to zero."""
        self.monitoring_active = False  # Stop monitoring on error
        self.process_active = False
        self.monitoring_active = False  # Stop the monitoring loop
        self.start_button.config(state=tk.NORMAL)
        self.emergency_button.config(state=tk.DISABLED)

        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)
        
        self.i = 1

        self.hydrogen_label.config(text="Hydrogen flow rate: 0 sccm")
        self.air_label.config(text="Synthetic air flow rate: 0 sccm")
        self.hydrogen_ppm.config(text=f"H2 Concentration: 0 PPM")
    
        self.countdown_label.config(text="Process Completed")
        self.total_time_label.config(text="Total time remaining: 00:00")
        self.progress_bar["value"] = 0
        self.verify_button.config(state=tk.NORMAL)
        #messagebox.showinfo("Process Complete", "Testing Completed")
        
        
    def stop_process(self):
        
        """Stop process and reset flow rates to zero."""
        self.monitoring_active = False  # Stop monitoring on error
        self.process_active = False
        self.monitoring_active = False  # Stop the monitoring loop
        self.start_button.config(state=tk.NORMAL)
        self.emergency_button.config(state=tk.DISABLED)

        self.controller_1.set_flow_rate(0)
        self.controller_2.set_flow_rate(0)
        
        self.i = 1

        self.hydrogen_label.config(text="Hydrogen flow rate: 0 sccm")
        self.air_label.config(text="Synthetic air flow rate: 0 sccm")
        self.hydrogen_ppm.config(text=f"H2 Concentration: 0 PPM")
    
        self.countdown_label.config(text="Process Completed")
        self.total_time_label.config(text="Total time remaining: 00:00")
        self.progress_bar["value"] = 0
        self.verify_button.config(state=tk.NORMAL)
        messagebox.showinfo("Process Complete", "Testing Completed")

    def emergency_stop(self):
        """Emergency stop handler."""
        if messagebox.askokcancel("Emergency Stop", "Are you sure you want to stop the process?"):
            self.stop_process()
