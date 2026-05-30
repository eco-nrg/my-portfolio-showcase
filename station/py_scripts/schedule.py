import time


class Interval:
    def __init__(self, interval: int) -> None:
        self.interval = interval
        self.elapsed = 0
        self.__last_check = time.time()

    def check(self) -> bool:
        now = time.time()  # in seconds
        dt = now - self.__last_check
        self.__last_check = now
        self.elapsed += dt
        if self.elapsed >= self.interval:
            self.elapsed = 0
            return True
        return False
