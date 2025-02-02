#import smbus2
#import time

# I2C address of the flow sensor
#FS2012_ADDRESS = 0x07

# Initialize I2C bus (1 is the standard I2C bus on Raspberry Pi)
#i2c_bus = smbus2.SMBus(1)

#def read_flow_sensor():
#    try:
        # Request 2 bytes from the sensor
 #       data = i2c_bus.read_i2c_block_data(FS2012_ADDRESS, 0, 2)
        
        # Combine the two bytes into a single 16-bit integer
#        msb = data[0]
#        lsb = data[1]
#        flow_value = (msb << 8) | lsb
        
        # Optional debug output
        # print(f"Raw MSB: {msb}, LSB: {lsb}")
        
#        return flow_value
#    except OSError as e:
#        print(f"Error reading from sensor: {e}")
 #       time.sleep(1)  # Delay before retrying
 #       return None

import numpy as np
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
chan = AnalogIn(ads, ADS.P1)

# Mapping function to map voltage to ppm
#def map_voltage_to_ppm(voltage, in_min=0.05, in_max=2.02, out_min=0, out_max=1000):
#    if voltage < in_min:
#        return 0
#    return (voltage - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# Polynomial coefficients for the 7th-degree polynomial
#coefficients = [33.3390,	510.8307,	-35.1691]
#coefficients = [-716.5554,	1.0329e+03,	-238.2597,	438.4647,	-22.3287]
#coefficients = [2.0241e+04,	-6.2442e+04,	7.2538e+04,	-3.9689e+04,	1.0615e+04,	-788.9249,	18.5079]
coefficients = [1.9405e+03,	-5.8269e+03,	5.8529e+03,	-2.1844e+03,	747.5893,	-35.2682]
#coefficients = [-3.8038e+04,	1.5515e+05,	-2.3963e+05,	1.6813e+05,	-4.4049e+04,	-6.0685e+03,	5.3857e+03,	-404.7562,	8.7961]


# Function to calculate y given x
def calculate_y(x):
    y = np.polyval(coefficients, x)
    return y
    

# Function to monitor readings and return PPM value
def read_flow_sensor():
    sensor_voltage = chan.voltage
    # printing sensor voltage for debugging
    
    print(f"Flow Sensor Voltage = {sensor_voltage}")
    
    flow_value = calculate_y(sensor_voltage)
    print(f"Flow Value = {flow_value}")
    
    #flow_value = map_voltage_to_ppm(sensor_voltage)
    #flow_value = sensor_voltage
    
    # Return PPM value
    return flow_value