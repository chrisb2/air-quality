"""Store and retreive environment baseline values for the ccs811 sensor."""
import uio
import uos


class Baseline:
    """Store and retreive environment baseline values for the ccs811 sensor."""

    _BASELINE_FILE = 'ccs811_baseline.txt'

    def exists(self):
        """Check if baseline exists."""
        try:
            with uio.open(self._BASELINE_FILE, mode='r'):
                return True
        except OSError:
            return False

    def store(self, value):
        """Store baseline integer value."""
        with uio.open(self._BASELINE_FILE, mode='w') as baseline_file:
            baseline_file.write('%s\n' % str(value))

    def retrieve(self):
        """Retrieve baseline integer value."""
        with uio.open(self._BASELINE_FILE, mode='r') as baseline_file:
            return int(baseline_file.readline())

    def delete(self):
        """Delete the baseline."""
        try:
            uos.remove(self._BASELINE_FILE)
        except OSError:
            pass
