# findSerialPortOfPico.py -- Runs on PC
# Michael A. Covington 2025
# Released to the public domain

# Runs on PC as a demonstration of how to query
# the temperature and humidity from the RPi Pico.

import serial   # use "pip install pyserial" if not found
import serial.tools.list_ports

# Enumerate the serial ports

ports = serial.tools.list_ports.comports()

# Find the (first) Pico

picoPort = ""
for p in ports:
    if p.vid == 0x2e8a and p.pid == 0x0005:
        picoPort = p.device        
        break

if picoPort:
    print("Raspberry Pi Pico found at:", picoPort)
    
    # Repeatedly query and display the temperature and humidity
    
    with serial.Serial(picoPort, 9600, timeout=10) as ser:
        
        # Simulate pressing Enter

        ser.write(b"\r")
        
        # The data read may be the temperature, or may
        # just be the echo of the Enter that was sent.
        # Try a limited number of times until a non-empty result is read.

        result = ""
        count = 0
        while (result == "" and count < 5):
            count = count + 1
            result = ser.readline().decode("utf-8").strip()
        
        # Display the result
        
        print(result)

        
        
        


    