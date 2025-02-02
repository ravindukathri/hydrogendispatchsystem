# controller.py

import time
from threading import Thread
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sfc5xxx import Sfc5xxxShdlcDevice, Sfc5xxxScaling, \
    Sfc5xxxUnitPrefix, Sfc5xxxUnit, Sfc5xxxUnitTimeBase, Sfc5xxxMediumUnit


class FlowController:
    def __init__(self, port, baudrate=115200, slave_address=0, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.slave_address = slave_address
        self.timeout = timeout
        self.device = None
        self.unit = None
        self.serial_port = None

    def connect(self):
        try:
            self.serial_port = ShdlcSerialPort(port=self.port, baudrate=self.baudrate)
            self.device = Sfc5xxxShdlcDevice(ShdlcConnection(self.serial_port), slave_address=self.slave_address)

            # Set gas calibration 0
            # self.device.activate_calibration(0)

            # Set user-defined flow unit to sccm
            self.unit = Sfc5xxxMediumUnit(
                Sfc5xxxUnitPrefix.MILLI,
                Sfc5xxxUnit.STANDARD_LITER,
                Sfc5xxxUnitTimeBase.MINUTE
            )
            self.device.set_user_defined_medium_unit(self.unit)

        except Exception as e:
            print(f"Error connecting to device on port {self.port}: {e}")
            
    def is_connected(self):
        """Return whether the controller is connected."""
        return self.connected

    def set_flow_rate(self, flow_rate):
        try:
            if self.device:
                self.device.set_setpoint(flow_rate, Sfc5xxxScaling.USER_DEFINED)
        except Exception as e:
            print(f"Error setting flow rate on port {self.port}: {e}")

    def set_flow_rate_with_retries(self, flow_rate, retries=3, timeout=500):
        """Set the flow rate with retries in case of failure."""
        for attempt in range(retries):
            try:
                # Increase timeout for SHDLC communication, if supported by your library
                self.device.set_setpoint(flow_rate, Sfc5xxxScaling.USER_DEFINED)
                return  # Success
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)  # Wait before retrying
                else:
                    # If all retries fail, raise the exception
                    raise ConnectionError(f"Failed to set flow rate after {retries} attempts: {e}")
            except KeyboardInterrupt:
                print("Process interrupted by user.")
                raise
    
    def get_measured_flow(self):
        try:
            if self.device:
                return self.device.read_measured_value(Sfc5xxxScaling.USER_DEFINED)
                
        except Exception as e:
            error_message = str(e)
            if "SHDLC device with address 0 is in error state" in error_message:
                print("Connection Lost!")
            else:
                print(f"Error reading measured flow on port {self.port}: {error_message}")
        return 0


    
    def get_current_gas_id(self):
        try:
            if self.device:
                return self.device.get_current_gas_description(Sfc5xxxScaling.USER_DEFINED)  
        except Exception as e:
            print(f"Error reading gas ID on port {self.port}: {e}")
        return None
    
        
    
    def get_current_setpoint(self):
        try:
            if self.device:
                return self.device.get_setpoint(Sfc5xxxScaling.USER_DEFINED)
        except Exception as e:
            print(f"Error reading current setpoint on port {self.port}: {e}")
        return 0

    def set_flow_rate_to_zero(self):
        try:
            if self.device:
                self.device.set_setpoint(0, Sfc5xxxScaling.USER_DEFINED)
        except Exception as e:
            print(f"Error setting flow rate to zero: {e}")

    def start_monitoring(self, gui_update_callback):
        """Monitor flow rates and update the GUI."""
        self.monitoring_active = True  # Set monitoring as active

        def monitor():
            while self.monitoring_active:
                flow = self.get_measured_flow()
                setpoint = self.get_current_setpoint()
                gui_update_callback(flow, setpoint)
                time.sleep(0.5)

        Thread(target=monitor, daemon=True).start()