import numpy as np


def gauss_kernel(size=5):
    ax = np.linspace(-(size - 1) / 2.0, (size - 1) / 2.0, size)
    kernel = np.exp(-0.5 * np.square(ax))
    return kernel / np.sum(kernel)


def clamp(v: int, lower: int, upper: int):
    return max(min(v, upper), lower)


class SmoothingWindow:
    def __init__(self, size=5, init_value=0, kernell_func=None) -> None:
        self.data = np.full(shape=size, fill_value=init_value)
        self.kernel = kernell_func(size)

    def append(self, el):
        self.data = np.insert(self.data[1:], self.data.size - 1, el)

    def smoothed_value(self):
        return np.sum(self.data * self.kernel)


class MedianWindow:
    def __init__(self, size: int = 3, init_value: int = 0):
        self.data = np.full(shape=size, fill_value=init_value)

    def append(self, el: int) -> None:
        self.data = np.insert(self.data[1:], self.data.size - 1, el)

    def smoothed_value(self):
        return np.median(self.data)
