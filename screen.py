"""Air quality monitor screen."""
import epaper2in9
from machine import SPI
import display


class Screen:
    """Air quality monitor screen."""

    _BUFFER_SIZE = epaper2in9.EPD_WIDTH * epaper2in9.EPD_HEIGHT // 8
    _SMALL_SCALE = 0.6
    _LARGE_SCALE = 1.5

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
        self._write_title_text("Temperature", 2, 113)
        self._write_value_text("%dC" % int(temperature), 5, 70)

    def _add_humidity(self, humidity):
        self._write_title_text("Humidity", 152, 113)
        self._write_value_text("%d%%" % int(humidity), 158, 70)

    def _add_co2(self, co2):
        # 400ppm to 8192ppm
        self._write_title_text("eCO2 ppm", 2, 48)
        self._write_value_text("%d" % co2, 10, 5)

    def _add_voc(self, voc):
        # 0ppb to 1187ppb
        self._write_title_text("TVOC ppb", 152, 48)
        self._write_value_text("%d" % voc, 158, 5)

    def _write_title_text(self, text, x, y):
        self._write_text(text, x, y, self._SMALL_SCALE, display.PEN_MEDIUM)

    def _write_value_text(self, text, x, y):
        self._write_text(text, x, y, self._LARGE_SCALE, display.PEN_MEDIUM)

    def _write_text(self, text, x, y, scale, pen):
        display.write_text(self.buffer, text, x, y, display.BLACK,
                           scale, scale, None, pen)

    def _update_screen(self):
        self.e.set_frame_memory(self.buffer, 0, 0, epaper2in9.EPD_WIDTH,
                                epaper2in9.EPD_HEIGHT)
        self.e.display_frame()
