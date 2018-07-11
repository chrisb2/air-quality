"""Air quality monitor screen."""
import epaper2in9
from machine import SPI
from display_buffer import Buffer


class Screen:
    """Air quality monitor screen."""

    # Text size scales
    _SMALL_TEXT = 0.6
    _LARGE_TEXT = 1.5
    # Screen
    _HALF_WIDTH = int(epaper2in9.EPD_WIDTH / 2)
    _HALF_HEIGHT = int(epaper2in9.EPD_HEIGHT / 2)

    def __init__(self, config):
        """Create with the supplied configuration."""
        spi = SPI(-1, baudrate=config.baudrate,
                  sck=config.sck, mosi=config.mosi, miso=config.miso)
        self._e = epaper2in9.EPD(spi, config.cs, config.dc,
                                 config.rst, config.busy)
        self._e.init()
        self._buffer = Buffer(epaper2in9.EPD_WIDTH, epaper2in9.EPD_HEIGHT)

    def update(self, temperature, humidity, co2, voc):
        """Update the screen with the supplied readings."""
        self._add_borders()
        self._add_temperature(temperature)
        self._add_humidity(humidity)
        self._add_co2(co2)
        self._add_voc(voc)
        self._update_screen()

    def _add_borders(self):
        self._buffer.background(self._buffer.WHITE)
        self._add_line(0, self._HALF_WIDTH,
                       epaper2in9.EPD_HEIGHT, self._HALF_WIDTH)
        self._add_line(self._HALF_HEIGHT, 0,
                       self._HALF_HEIGHT, epaper2in9.EPD_WIDTH)

    def _add_line(self, x1, y1, x2, y2):
        self._buffer.line(x1, y1, x2, y2,
                          self._buffer.BLACK, self._buffer.PEN_MEDIUM)

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
        self._write_text(text, x, y, self._SMALL_TEXT, self._buffer.PEN_MEDIUM)

    def _write_value_text(self, text, x, y):
        self._write_text(text, x, y, self._LARGE_TEXT, self._buffer.PEN_MEDIUM)

    def _write_text(self, text, x, y, scale, pen):
        self._buffer.write_text(text, x, y, self._buffer.BLACK,
                                scale, scale, None, pen)

    def _update_screen(self):
        self._e.set_frame_memory(self._buffer.get(), 0, 0,
                                 epaper2in9.EPD_WIDTH, epaper2in9.EPD_HEIGHT)
        self._e.display_frame()
