"""Air quality monitor screen."""
import epaper2in9
from machine import SPI
from display_buffer import Buffer


class Screen:
    """Air quality monitor screen."""

    # Text size scales
    _TINY_TEXT = 0.3
    _SMALL_TEXT = 0.6
    _LARGE_TEXT = 1.5
    # Screen
    _HALF_WIDTH = int(epaper2in9.EPD_WIDTH / 2)
    _HALF_HEIGHT = int(epaper2in9.EPD_HEIGHT / 2)

    def __init__(self, config):
        """Create with the supplied configuration."""
        spi = SPI(-1, baudrate=config.baudrate,
                  sck=config.sck, mosi=config.mosi, miso=config.miso)
        self._epd = epaper2in9.EPD(spi, config.cs, config.dc,
                                   config.rst1, config.busy)
        self._epd.init()
        self._buffer = Buffer(epaper2in9.EPD_WIDTH, epaper2in9.EPD_HEIGHT)

    def update(self, temperature, humidity, co2, voc, voltage,
               baseline=False, fullupdate=False):
        """Update the screen with the supplied readings."""
        self._add_borders()
        self._add_temperature(temperature)
        self._add_humidity(humidity)
        self._add_co2(co2)
        self._add_voc(voc)
        self._add_voltage(voltage)
        self._add_baseline_indicator(baseline)
        self._update_screen(fullupdate)

    def sleep(self):
        """Put the screen into low current mode."""
        self._epd.sleep()

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
        self._write_value_text("%dC" % int(round(temperature)), 5, 70)

    def _add_humidity(self, humidity):
        self._write_title_text("Humidity", 152, 113)
        self._write_value_text("%d%%" % int(round(humidity)), 158, 70)

    def _add_co2(self, co2):
        # 400ppm to 32768ppm
        self._write_title_text("eCO2 ppm", 2, 48)
        if co2 is None:
            self._add_line(50, 25, 80, 25)
        else:
            self._write_value_text("%d" % co2, 10, 5)

    def _add_voc(self, voc):
        # 0ppb to 32768ppb
        self._write_title_text("TVOC ppb", 152, 48)
        if voc is None:
            self._add_line(200, 25, 230, 25)
        else:
            self._write_value_text("%d" % voc, 158, 5)

    def _add_voltage(self, voltage):
        if voltage is not None:
            self._buffer.line(272, 118, 272, epaper2in9.EPD_WIDTH,
                              self._buffer.BLACK, self._buffer.PEN_THIN)
            self._buffer.line(272, 118, epaper2in9.EPD_HEIGHT, 118,
                              self._buffer.BLACK, self._buffer.PEN_THIN)
            self._write_text("%.1fV" % voltage, 274, 120, self._TINY_TEXT,
                             self._buffer.PEN_THIN)

    def _add_baseline_indicator(self, baseline):
        if baseline:
            self._write_text("B", 288, 2, self._TINY_TEXT,
                             self._buffer.PEN_THIN)

    def _write_title_text(self, text, x, y):
        self._write_text(text, x, y, self._SMALL_TEXT, self._buffer.PEN_MEDIUM)

    def _write_value_text(self, text, x, y):
        self._write_text(text, x, y, self._LARGE_TEXT, self._buffer.PEN_MEDIUM)

    def _write_text(self, text, x, y, scale, pen):
        self._buffer.write_text(text, x, y, self._buffer.BLACK,
                                scale, scale, None, pen)

    def _update_screen(self, fullupdate):
        if fullupdate:
            self._epd.set_lut(self._epd.LUT_FULL_UPDATE)
        else:
            self._epd.set_lut(self._epd.LUT_PARTIAL_UPDATE)
        self._epd.set_frame_memory(self._buffer.get(), 0, 0,
                                   epaper2in9.EPD_WIDTH, epaper2in9.EPD_HEIGHT)
        self._epd.display_frame()
