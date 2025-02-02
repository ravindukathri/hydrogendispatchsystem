import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C bus and ADS1115 ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2/3  # Gain setting to measure higher voltages

# Create single-ended input on channel 0 (A0 pin)
chan = AnalogIn(ads, ADS.P0)

# Global variables for voltage range
in_min = 0.821
in_max = 2.763

# Mapping function to map voltage to ppm
def map_voltage_to_ppm(voltage, in_min=in_min, in_max=in_max, out_min=0, out_max=20000):
    if voltage < in_min:
        return 0
    
    return (voltage - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to monitor readings and return PPM value
def hydrogen_sensor():
    sensor_voltage = chan.voltage
    ppm_value = map_voltage_to_ppm(sensor_voltage)
    
    hydrogen_percentage = ppm_value / 10000  # Calculated hydrogen percentage (optional)
    # Return PPM value
    return ppm_value

# Function to monitor and return sensor voltage
def hydrogen_sensor_voltage():
    sensor_voltage = chan.voltage
    
    return sensor_voltage
