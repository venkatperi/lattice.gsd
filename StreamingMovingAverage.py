class StreamingMovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.timestamps = []
        self.sum = 0

    def process(self, value, timestamp):
        self.values.append(value)
        self.timestamps.append(timestamp)

        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
            self.timestamps.pop(0)

        average = float(self.sum) / len(self.values)
        diff = self.timestamps[len(self.timestamps) - 1] - self.timestamps[0]

        rate = 0 if diff == 0 else average * 1000. * len(self.timestamps) / diff
        return average, rate
