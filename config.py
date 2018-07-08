"""Configuration file for air quality monitor."""
from machine import Pin

sck = Pin(18)
mosi = Pin(23)
miso = Pin(12)
cs = Pin(5)
dc = Pin(26)
rst = Pin(27)
busy = Pin(32)

baudrate = 2000000
