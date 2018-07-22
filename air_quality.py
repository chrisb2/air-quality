"""An air quality sensor and display.

Uses the BME280 and CCS811 sensors to read temperature, relative humidity,
equivalent CO2 (eCO2) and Total Volatile Organic Compound (TVOC) and displays
the values on a 2.9in Waveshare e-Paper display.
"""
import machine
import esp32
import ccs811
import bme280
import screen
import battery
import config

CONDITIONING_RUNS = 20  # 20 runs (minutes), p9 of datasheet

i2c = machine.I2C(scl=config.scl, sda=config.sda, freq=100000)
bme = bme280.BME280(i2c=i2c, mode=bme280.BME280_OSAMPLE_4)
rtc = machine.RTC()
scr = screen.Screen(config)
bat = battery.Battery(config.battery)


def run():
    """Main entry point to execute this program."""
    if _isFirstRun():
        _setRunsToCondition(CONDITIONING_RUNS)
        ccs = ccs811.CCS811(i2c, mode=ccs811.CCS811.DRIVE_MODE_60SEC)
        t, p, h = bme.read_data()
        # Full update of Waveshare on power on
        scr.update(t, h, None, None, bat.volts(), True)
    else:
        ccs = ccs811.CCS811(i2c, mode=None)
        _addRun()

        try:
            ccs.read()
            t, p, h = bme.read_data()
            ccs.put_envdata(t, h)
            if _isConditioned():
                scr.update(t, h, ccs.eco2, ccs.tvoc, bat.volts())
            else:
                scr.update(t, h, None, None, bat.volts())
            print('eCO2: %dppm, TVOC: %dppb, %.1fC, %.1f%%RH' %
                  (ccs.eco2, ccs.tvoc, t, h))
        except OSError as e:
            print(e)

    scr.sleep()
    esp32.wake_on_ext0(pin=config.int, level=0)
    machine.deepsleep()


def _setRunsToCondition(run_count):
    """Set number of runs (minutes) required to condition ccs811 sensor."""
    rtc.memory(bytes([run_count]))


def _isFirstRun():
    memory = rtc.memory()
    return len(memory) == 0


def _isConditioned():
    memory = rtc.memory()
    return memory[0] == 0


def _addRun():
    # Decrement run count in first 20mins of running
    memory = rtc.memory()
    if memory[0] != 0:
        rtc.memory(bytes([memory[0] - 1]))
