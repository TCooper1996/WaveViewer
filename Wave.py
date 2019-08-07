from numpy import sin, pi, cos


class SinWave:
    def __init__(self, phase, amplitude, period):
        self.phase = phase
        self.amplitude = amplitude
        self.period = period

    def get_range(self, samples, periods):
        phase = self.phase
        amp = self.amplitude
        freq = (1/self.period) if self.period > 0 else 0
        angles = [pi * j / samples for j in range(samples*2*periods)]
        return [amp * sin(2*pi*freq*i + phase) for i in angles]
