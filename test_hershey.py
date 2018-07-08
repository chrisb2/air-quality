"""Test Hershey font."""
import epaper2in9
from machine import SPI, Pin
import display

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

buf = bytearray(128 * 296 // 8)
display.background(buf, display.WHITE)
display.write_text(buf, 'lmnopqr', 0, 20, display.BLACK, 2.0, 2.0,
                   None, display.PEN_MEDIUM)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()

display.plot(buf, 10, 10, display.BLACK)
display.blob(buf, 10, 10, display.BLACK)
