"""An air quality sensor and display.

Uses the BME280 and CCS811 sensors to read temperature, relative humidity,
equivalent CO2 (eCO2) and Total Volatile Organic Compound (TVOC) and displays
the values on a 2.9in Waveshare e-Paper display.
"""
import machine
import esp32
import utime
import ccs811
import bme280
import screen
import battery
import baseline
import config

_i2c = machine.I2C(scl=config.scl, sda=config.sda, freq=100000)
_rtc = machine.RTC()
_bat = battery.Battery(config.battery)
_baseline = baseline.Baseline()


def run():
    """Main entry point to execute this program."""
    try:
        bme = bme280.BME280(i2c=_i2c, mode=bme280.BME280_OSAMPLE_4)
        scr = screen.Screen(config)

        if _is_first_run():
            # 20 runs (minutes), p9 of datasheet
            _set_runs_to_condition(20)
            ccs = ccs811.CCS811(_i2c, mode=ccs811.CCS811.DRIVE_MODE_60SEC)
            t, p, h = bme.read_data()
            # Full update of Waveshare on power on
            scr.update(t, h, None, None, _bat.volts(), True)
        else:
            ccs = ccs811.CCS811(_i2c, mode=None)
            _add_run()
            ccs.read()
            t, p, h = bme.read_data()
            ccs.put_envdata(t, h)

            if _ccs811_is_conditioned():
                # Stored baseline should only be loaded after conditioning
                if not _ccs811_baseline_is_loaded() and _baseline.exists():
                    baseline = _baseline.retrieve()
                    ccs.put_baseline(baseline)
                    _set_ccs811_baseline_loaded()
                    scr.update(t, h, None, None, _bat.volts())
                    print('ccs811 baseline %d loaded' % baseline)
                else:
                    scr.update(t, h, ccs.eco2, ccs.tvoc, _bat.volts())
                if _new_ccs811_baseline_requested():
                    baseline = ccs.get_baseline()
                    _baseline.store(baseline)
                    print('ccs811 baseline %d stored' % baseline)
            else:
                scr.update(t, h, None, None, _bat.volts())

            print('eCO2: %dppm, TVOC: %dppb, %.1fC, %.1f%%RH, baseline: %r' %
                  (ccs.eco2, ccs.tvoc, t, h, _ccs811_baseline_is_loaded()))

        scr.sleep()
        _flash_led()
    except Exception as e:
        _flash_led(3)
        print(e)

    esp32.wake_on_ext0(pin=config.int, level=0)
    machine.deepsleep()


def _set_runs_to_condition(run_count):
    """Set number of runs (minutes) required to condition ccs811 sensor."""
    _rtc.memory(bytes([run_count]))


def _is_first_run():
    memory = _rtc.memory()
    return len(memory) == 0


def _ccs811_is_conditioned():
    memory = _rtc.memory()
    return memory[0] == 0


def _ccs811_baseline_is_loaded():
    memory = _rtc.memory()
    return len(memory) > 1 and memory[1] == 1


def _set_ccs811_baseline_loaded():
    memory = _rtc.memory()
    _rtc.memory(bytes([memory[0], 1]))


def _new_ccs811_baseline_requested():
    return config.sw1.value() == 0


def _add_run():
    # Decrement run count in first 20mins of running
    memory = _rtc.memory()
    if memory[0] != 0:
        _rtc.memory(bytes([memory[0] - 1]))


def _flash_led(count=1):
    # Built in LED on Lolin D32
    led = machine.Pin(5, machine.Pin.OUT)
    for _ in range(0, count):
        led.value(0)
        utime.sleep_ms(100)
        led.value(1)
        utime.sleep_ms(100)
