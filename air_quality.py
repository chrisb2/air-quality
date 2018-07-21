"""An air quality sensor and display.

Uses the BME280 and CCS811 sensors to read temperature, relative humidity,
equivalent CO2 (eCO2) and Total Volatile Organic Compound (TVOC) and displays
the values on a 2.9in Waveshare e-Paper display.
"""
import machine
import esp32
from ccs811 import CCS811
import bme280
from screen import Screen
import config

i2c = machine.I2C(scl=config.scl, sda=config.sda, freq=100000)
bme = bme280.BME280(i2c=i2c, mode=bme280.BME280_OSAMPLE_4)
rtc = machine.RTC()
scr = Screen(config)


def run():
    """Main entry point to execute this program."""
    memory = rtc.memory()
    if len(memory) == 0 or memory[0] == 0x00:
        rtc.memory(bytes([0x01]))
        ccs = CCS811(i2c, mode=CCS811.DRIVE_MODE_60SEC)
    else:
        ccs = CCS811(i2c, mode=None)
        # updated wake count

        try:
            ccs.read()
            t, p, h = bme.read_data()
            ccs.put_envdata(t, h)
            # read battery voltage
            scr.update(t, h, ccs.eco2, ccs.tvoc, None)
            # if wake count > 20: # 20mins
            #     put baseline to ccs811
            print('eCO2: %dppm, TVOC: %dppb, %.1fC, %.1f%%RH' %
                  (ccs.eco2, ccs.tvoc, t, h))
        except OSError as e:
            print(e)

    # put screen to sleep
    esp32.wake_on_ext0(pin=config.int, level=0)
    machine.deepsleep()


def reinitialize():
    """Re-initialize state of ccs811 sensor."""
    machine.RTC.memory(bytes([0x00]))
