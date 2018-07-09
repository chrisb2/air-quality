"""Configuration file for air quality monitor."""
from machine import Pin

sck = Pin(18)  # Marked CLK on Waveshare
mosi = Pin(23)  # Marked DIN on Waveshare
miso = Pin(12)  # Note used by Waveshare but must be supplied to SPI
cs = Pin(5)  # Marked CS on Waveshare
dc = Pin(26)  # Marked DC on Waveshare
rst = Pin(27)  # Marked RST on Waveshare
busy = Pin(32)  # Marked BUSY on Waveshare

baudrate = 20000000
