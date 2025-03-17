# temp_humidity.py
# Michael A. Covington, 2025 January 17
# Released to the public domain

# Parts:
#  Raspberry Pi Pico original model
#  SSD1306 OLED display, I2C bus
#  DHT22 temperature/humidity sensor on breakout board

# Connections:
#  Powered by USB
#  Pin 36 (3V3)  to display's Vcc and DHT22 sensor's V+
#  Pin 24 (GP18) to DHT22 sensor's output
#  Pin 23 (GND)  to display's GND and DHT22 sensor's GND
#  Pin 22 (GP17) to display's SCL
#  Pin 21 (GP16) to display's SDA
#  no pin (GP25) to Pico internal LED

# Libraries used:
#   Installed from Thonny (Tools, Manage Packages):
#     ssd1306.py
#   From https://github.com/peterhinch/micropython-font-to-py/tree/master/writer:
#     writer.py
# Fonts:
#   IBM Plex Sans is a free font given away by IBM, closely resembling Arial.
#   IBMPlexSans-Semibold.ttf was obtained from https://fonts.google.com/specimen/IBM+Plex+Sans
#   and converted to IBMPlexSans30.py and IBMPlexSans14.py using font_to_py.py
#   from Peter Hinch's library just mentioned.

import time
import machine

# For writing on the OLED display
import ssd1306
from writer import Writer
import IBMPlexSans30
import IBMPlexSans14

# For DHT22 temperature/humidity sensor
import dht

# For low-level serial input checking
from select import select
import sys

# Initialization of globals

VERSION="2025 Mar 10"

LED = machine.Pin(25,machine.Pin.OUT)
I2C = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17), freq=400000)
WIDTH = 128
HEIGHT = 64
DISPLAY = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, I2C, addr=0x3c)

SENSOR = dht.DHT22(machine.Pin(18))
TEMPERATURE = 0
HUMIDITY = 0

#
# Display access
#

def text(font, message):
    """Clear the screen and then write the message
    in the given font, replacing '|' with newline"""
    DISPLAY.fill(0) # clear it
    Writer.set_textpos(DISPLAY,0,0)
    writer = Writer(DISPLAY, font, verbose=False)  # verbose = False to suppress console output
    # For legibility in source code, | represents newline in text
    writer.printstring(message.replace("|","\n"))
    DISPLAY.show()

def progress_indicator(value):
    """A line of specified length, 0 to 63, 
    across the bottom of the screen"""
    DISPLAY.line(0,63,value,63,1)
    DISPLAY.show()
    
def draw_line_slowly():
    """Draw progress indicator line
    slowly, taking 3.84 seconds"""
    for x in range(0,127):
        progress_indicator(x)
        time.sleep(0.03)

#
# Opening display messages
#

def splash_screens():
    """Display opening messages, allowing plenty
    of time for sensor to initialize and stabilize"""
    
    text(IBMPlexSans14, "Temperature|and|Humidity|Meter")
    draw_line_slowly()
    
    text(IBMPlexSans14, "Covington|Innovations||" + VERSION)
    draw_line_slowly()
    
    text(IBMPlexSans14, "To read from|PC, connect to|USB serial and|send Enter (CR).")
    draw_line_slowly()

    text(IBMPlexSans14, "Disconnect when|doing other Pi|development on|same PC.")
    draw_line_slowly()
    
#
# Serial communication
#

def clear_serial_input():
    """Consume any characters that are waiting to be read"""
    while pending_serial_input():
            sys.stdin.read(1)

def pending_serial_input():
    """True if any characters are waiting to be read"""
    return select([sys.stdin], [], [], 0)[0]    

#
# Accessing temperature
#

def read_sensor():
    """Read the sensor and update the globals TEMPERATURE and HUMIDITY"""

    global SENSOR 
    global TEMPERATURE
    global HUMIDITY
    
    # Measurement will fail if attempted too soon after an earlier measurement,
    # and possibly for other reasons
    try:
        SENSOR.measure()
        TEMPERATURE = 1.8 * SENSOR.temperature() + 32  # Fahrenheit
        HUMIDITY = SENSOR.humidity()
    except OSError as e:
        TEMPERATURE = -1
        HUMIDITY = -1

def update_display():
    """Put current temperature and humidity on the display"""
    text(IBMPlexSans30, f" {TEMPERATURE:.1f} F\n {HUMIDITY:.1f} %")

def main_loop():
    """Read the sensor and update the display every 5 seconds.
    Also, if any input is received on the serial port, consume it
    ignoring its contents, and immediately report the most recently
    read temperature and humidity to serial output."""

    # Sensor needs to stabilize at least 2 seconds before each reading.
    # The splash screens and the 5-second main loop take care of this.
    
    read_sensor()
    update_display()
    
    # Wait 5 seconds, in the meantime servicing
    # any serial requests that are received.
    deadline = time.ticks_add(time.ticks_ms(), 5000)
    
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        
        if pending_serial_input():

            clear_serial_input()
            
            # report temperature and humidity to serial output
            print(f"{TEMPERATURE:.0f}F {HUMIDITY:.0f}%")  
        
            # blink the LED to show that a request was serviced
            LED.value(1)
            time.sleep(0.1)
            LED.value(0)
    
        # This is a busy-wait loop; nothing else to do
    
 
#
# Main
#
  
def main():
    clear_serial_input()
    splash_screens()
    while True:
        main_loop()
    
main()



