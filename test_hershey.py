"""Test Hershey font."""
import epaper2in9
from machine import SPI, Pin
from display_buffer import Buffer

w = 128
h = 296
x = 0
y = 0

spi = SPI(-1, baudrate=2000000, sck=Pin(18), mosi=Pin(23), miso=Pin(12))
cs = Pin(5)
dc = Pin(26)
rst = Pin(27)
busy = Pin(32)

e = epaper2in9.EPD(spi, cs, dc, rst, busy)
e.init()

buffer = Buffer(128, 296)
buffer.background(buffer.WHITE)
buffer.write_text(':?/|\\', 0, 60, buffer.BLACK, 1.0, 1.0,
                  None, buffer.PEN_MEDIUM)
e.set_frame_memory(buffer.get(), x, y, w, h)
e.display_frame()
