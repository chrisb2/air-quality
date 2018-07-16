"""
CCS811 Indoor Air Quality Sensor.

Based on CCS811 datasheet. Inspired by Adafruit and Sparkfun libraries
"""
import logging
from micropython import const


class CCS811:
    """CCS811 gas sensor. Measures eCO2 in ppm and TVOC in ppb."""

    DRIVE_MODE_IDLE = const(0x00)
    DRIVE_MODE_1SEC = const(0x01)
    DRIVE_MODE_10SEC = const(0x02)
    DRIVE_MODE_60SEC = const(0x03)
    DRIVE_MODE_250MS = const(0x04)

    __STATUS_REG = 0x00
    __MODE_REG = 0x01
    __DATA_REG = 0x02
    __ENV_REG = 0x05
    __BASELINE_REG = 0x11
    __ERROR_REG = 0xe0

    __DEVICE_MSG = 'CCS811 not found, check wiring, pull nWake to GND'
    __APPLICATION_MSG = 'Application not valid'

    __ADDRESS = 0x5A

    def __init__(self, i2c, mode=DRIVE_MODE_1SEC, address=__ADDRESS,
                 log_level=logging.ERROR):
        """Initialize sensor in the specified mode."""
        self._i2c = i2c
        self._addr = address
        self._tVOC = 0
        self._eCO2 = 0
        self._mode = mode
        self._error = False
        logging.basicConfig(level=log_level)
        self._log = logging.getLogger("ccs811")

        self._validate_device_present()
        self._validate_hardware()
        self._validate_application_present()
        self._start_application()
        self._set_mode(mode)

    @property
    def tvoc(self):
        """Total Volatile Organic Compound in parts per billion (ppb).

        Clipped to 0 to 1187 ppb.
        """
        return self._tVOC

    @property
    def eco2(self):
        """Equivalent Carbon Dioxide in parts per million (ppm).

        Clipped to 400 to 8192ppm.
        """
        return self._eCO2

    def data_ready(self):
        """Return true if new data is ready. Values in eCO2 and tVOC."""
        status = self._read_status()
        # bit 3 in the status register: data_ready
        if (status[0] >> 3) & 0x01:
            self._read()
            return True
        else:
            return False

    def __str__(self):
        """Return human readable values."""
        return 'eCO2: %d ppm, tVOC: %d ppb' % (self.eco2, self.tvoc)

    def _read(self):
        # datasheet Figure 14: Algorithm Register Byte Order (0x02)
        register = self.__read_register(self.__DATA_REG, 4)
        co2HB = register[0]
        co2LB = register[1]
        tVOCHB = register[2]
        tVOCLB = register[3]
        self._eCO2 = ((co2HB << 8) | co2LB)
        self._tVOC = ((tVOCHB << 8) | tVOCLB)

    def get_baseline(self):
        """Get the current baseline value."""
        register = self.__read_register(self.__BASELINE_REG, 2)
        HB = register[0]
        LB = register[1]
        return (HB << 8) | LB

    def put_baseline(self, baseline):
        """Set the baseline value."""
        register = bytearray([0x00, 0x00])
        register[0] = baseline >> 8
        register[1] = baseline & 0xff
        self.__write_register(self.__BASELINE_REG, register)

    def put_envdata(self, humidity, temp):
        """Set the environment data (temperature and humidity)."""
        envregister = bytearray([0x00, 0x00, 0x00, 0x00])
        envregister[0] = int(humidity) << 1
        t = int(temp//1)
        tf = temp % 1
        t_H = (t + 25) << 9
        t_L = int(tf * 512)
        t_comb = t_H | t_L
        envregister[2] = t_comb >> 8
        envregister[3] = t_comb & 0xFF
        self.__write_register(self.__ENV_REG, envregister)

    def _validate_device_present(self):
        # Check if sensor is available at i2c bus address
        devices = self._i2c.scan()
        if self._addr not in devices:
            raise ValueError(self.__DEVICE_MSG)

    def _validate_hardware(self):
        # See figure 22 in datasheet: Bootloader Register Map
        # Check HW_ID register (0x20) - correct value 0x81
        # hardware_id = self._i2c.readfrom_mem(self._addr, 0x20, 1)
        # if (hardware_id[0] != 0x81):
        #     raise ValueError('Wrong Hardware ID.')
        pass

    def _start_application(self):
        # Application start. Write with no data to App_Start (0xf4)
        self._i2c.writeto(self._addr, bytearray([0xf4]))

    def _validate_application_present(self):
        # Check Status Register (0x00) to see if valid application present-
        status = self._read_status()
        # See figure 12 in datasheet: Status register: Bit 4: App valid
        if not (status[0] >> 4) & 0x01:
            raise ValueError(self.__APPLICATION_MSG)

    def _set_mode(self, mode):
        self.__write_register(self.__MODE_REG, bytearray([(mode << 4) | 0x8]))

    def _read_status(self):
        status = self.__read_register(self.__STATUS_REG, 1)
        self._log.debug("valid: %d, ready: %d, error: %d",
                        (status[0] >> 4) & 0x01, (status[0] >> 3) & 0x01,
                        status[0] & 0x01)
        return status

    def __write_register(self, register, register_bytes):
        self.__log_register_operation("write", register, register_bytes)
        self._i2c.writeto_mem(self._addr, register, register_bytes)

    def __read_register(self, register, bytes):
        register_bytes = self._i2c.readfrom_mem(self._addr, register, bytes)
        self.__log_register_operation("read", register, register_bytes)
        return register_bytes

    def __log_register_operation(self, msg, register, bytes):
        # performance optimisation
        if logging._level == logging.DEBUG:
            # binary = '{0:#010b}'.format(value)
            self._log.debug("%s register 0x%02x: %s", msg, register,
                            ' '.join('0x{:02x}'.format(x) for x in bytes))
