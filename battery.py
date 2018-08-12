"""Reads the battery voltage of the Lolin D32 development board."""
from machine import ADC


class Battery:
    """Reads the battery voltage of the Lolin D32 development board."""

    # See Lolin D32 schematic 'Battery' section
    _RESISTOR_RATIO = (100000 + 100000) / 100000
    _REFERENCE_VOLTAGE = 3.296  # measured for individual Lolin D32
    _ADC_READS = 100

    def __init__(self, adcpin):
        """Create with the supplied adc pin."""
        self._pin = adcpin

    def volts(self):
        """Read voltage as float."""
        adc = ADC(self._pin)
        adc.atten(adc.ATTN_11DB)
        sum = 0
        for x in range(0, self._ADC_READS):
            sum += adc.read()
        return self._RESISTOR_RATIO * (sum * self._REFERENCE_VOLTAGE / 4096 /
                                       self._ADC_READS)
