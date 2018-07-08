"""Air quality monitor screen."""
import epaper2in9
from machine import SPI
import display


class Screen:
    """Air quality monitor screen."""

    _BUFFER_SIZE = epaper2in9.EPD_WIDTH * epaper2in9.EPD_HEIGHT // 8
    _TEXT_SCALE = 2.0

    def __init__(self, config):
        """Create with the supplied configuration."""
        spi = SPI(-1, baudrate=config.baudrate,
                  sck=config.sck, mosi=config.mosi, miso=config.miso)
        self.e = epaper2in9.EPD(spi, config.cs, config.dc,
                                config.rst, config.busy)
        self.e.init()
        self.buffer = bytearray(self._BUFFER_SIZE)

    def update(self, temperature, humidity, co2, voc):
        """Update the screen with the supplied readings."""
        self._add_borders()
        self._add_temperature(temperature)
        self._add_humidity(humidity)
        self._add_co2(co2)
        self._add_voc(voc)
        self._update_screen()

    def _add_borders(self):
        display.background(self.buffer, display.WHITE)
        display.line(self.buffer, 0, 64, 296, 64,
                     display.BLACK, display.PEN_MEDIUM)
        display.line(self.buffer, 148, 0, 148, 128,
                     display.BLACK, display.PEN_MEDIUM)

    def _add_temperature(self, temperature):
        text = "%dC" % int(temperature)
        self._write_text(text, 10, 75)

    def _add_humidity(self, humidity):
        text = "%d%%RH" % int(humidity)
        self._write_text(text, 158, 75)

    def _add_co2(self, co2):
        text = "%dppm" % co2
        self._write_text(text, 10, 10)

    def _add_voc(self, voc):
        text = "%dppm" % voc
        self._write_text(text, 158, 10)

    def _write_text(self, text, x, y):
        display.write_text(self.buffer, text, x, y, display.BLACK,
                           self._TEXT_SCALE, self._TEXT_SCALE,
                           None, display.PEN_MEDIUM)

    def _update_screen(self):
        self.e.set_frame_memory(self.buffer, 0, 0, epaper2in9.EPD_WIDTH,
                                epaper2in9.EPD_HEIGHT)
        self.e.display_frame()
