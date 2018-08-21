
class MovingAverageWithRate(object):
    """
    Computes the moving average (with optional sample rate) of supplied
    samples over a given window size.

    Add new samples with add()
    """

    def __init__(self, window_size):
        """
        :param window_size: int
            Window size (number of retained samples) for computing average.
            Must be > 0.
        """
        if not isinstance(window_size, int):
            raise TypeError("window_size must be int")
        if window_size < 1:
            raise ValueError("window_size must be > 0")

        self.window_size = window_size
        self.samples = []
        self.timestamps = []
        self.window_sum = 0.0

    def add(self, sample, timestamp):
        """
        Adds a new sample. The moving average and rate are updated.
        If the number of retained samples exceed the window_size,
        the oldest sample is discarded.

        :param sample: float
            Sample to add to the window.

        :param timestamp: int
            Timestamp of the the new sample (milliseconds).

        :return: (average, rate): (float, float)
            The updated moving average and sample rate.
        """

        if len(self.samples) == self.window_size:
            self.window_sum -= self.samples.pop(0)
            self.timestamps.pop(0)

        self.samples.append(sample)
        self.timestamps.append(timestamp)
        self.window_sum += sample

        average = float(self.window_sum) / len(self.samples)

        time_span = timestamp - self.timestamps[0]
        rate = 0 if time_span == 0 else self.window_sum * 1000. / time_span

        return average, rate
