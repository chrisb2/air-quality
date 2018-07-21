"""Program to upgrade the firmware of the ccs811 sensor."""
from machine import I2C
import utime
import config
import uio
import binascii

ADDRESS = 0x5A

i2c = I2C(scl=config.scl, sda=config.sda, freq=100000)


def firmware_upgrade(firmware_file):
    """Upgrade ccs811 firmware.

    For example: firmware_upgrade('CCS811_SW000246_1-00.bin')
    """
    reset = config.rst2
    wake = config.wake

    # Pulse Reset pin
    print("Enter boot mode...")
    reset.value(0)
    utime.sleep_ms(100)
    reset.value(1)
    utime.sleep_ms(100)

    # Set Wake low
    wake.value(0)
    utime.sleep_ms(100)

    # Erase application
    print("Erase application...")
    i2c.writeto_mem(ADDRESS, 0xf1, bytearray([0xe7, 0xa7, 0xe6, 0x09]))
    utime.sleep_ms(500)

    # Send firmware to ccs811
    print("Load firmware...")
    with uio.open(firmware_file, mode='rb') as firmware:
        while True:
            bytes = firmware.read(8)
            if len(bytes) == 0:
                break
            payload = bytearray([0xf2])
            for b in bytes:
                payload.append(b)
            i2c.writeto(ADDRESS, payload)
            print(binascii.hexlify(payload))
            # i2c.writeto_mem(ADDRESS, 0xf2, bytearray(bytes))
            utime.sleep_ms(50)

    # Verify application - this does not work always returns 0
    # Power off to complete
    print("Verify...")
    i2c.writeto_mem(ADDRESS, 0xf3, bytearray([0x01]))
    utime.sleep_ms(500)
    status = i2c.readfrom_mem(ADDRESS, 0x00, 1)
    print(status[0])
    print(status[0] & 0x30)

    # Set Wake low
    wake.value(1)
    print("Done - Power device off and on again")
