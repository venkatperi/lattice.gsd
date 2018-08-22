import time


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
        self.time_stamps = []
        self.accumulator = 0.0
        self.average = 0.0
        self.rate = 0.0

    def add(self, sample, time_stamp=None):
        """
        Adds a new sample. The moving average and rate are updated.
        If the number of retained samples exceed the window_size,
        the oldest sample is discarded.

        :param sample: float
            Sample to add to the window.

        :param time_stamp: int, optional
            Timestamp of the the new sample (nanoseconds).

        :return: (average, rate): (float, float)
            The updated moving average and sample rate.
        """

        time_stamp = time.time_ns() if time_stamp is None else time_stamp

        if len(self.samples) == self.window_size:
            self.accumulator -= self.samples.pop(0)
            self.time_stamps.pop(0)

        self.samples.append(sample)
        self.time_stamps.append(time_stamp)
        self.accumulator += sample

        self.average = float(self.accumulator) / len(self.samples)

        time_span = time_stamp - self.time_stamps[0]
        self.rate = 0
        if time_span != 0:
            self.rate = self.accumulator * 1000000000. / time_span

        return self.average, self.rate
