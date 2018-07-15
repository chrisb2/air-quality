"""Configuration file for air quality monitor."""
from machine import Pin

# Waveshare Display
baudrate = 20000000
sck = Pin(2)  # Marked CLK on Waveshare
mosi = Pin(15)  # Marked DIN on Waveshare
miso = Pin(23)  # Not used by Waveshare but must be supplied to SPI
cs = Pin(0)  # Marked CS on Waveshare
dc = Pin(4)  # Marked DC on Waveshare
rst1 = Pin(16)  # Marked RST on Waveshare
busy = Pin(17)  # Marked BUSY on Waveshare

# BME-280 and CCS811
scl = Pin(26)
sda = Pin(25)
# Following are CCS811 only
wake = Pin(33, Pin.OUT)
int = Pin(34, Pin.IN, Pin.PULL_UP)  # pulled down by CCS811
rst2 = Pin(32, Pin.OUT)

# Control Switches (sw1 is power)
sw2 = Pin(13)
sw3 = Pin(12)
sw4 = Pin(14)
