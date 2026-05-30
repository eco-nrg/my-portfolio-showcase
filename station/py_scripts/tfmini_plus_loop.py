"""Чтение даных лидара TFmini Plus и запись в Redis

# спецификация

see: https://cdn.sparkfun.com/assets/1/4/2/1/9/TFmini_Plus_A02_Product_Manual_EN.pdf

Byte0 Byte1 Byte2  Byte3  Byte4      Byte5      Byte6  Byte7  Byte8
0x59  0x59  Dist_L Dist_H Strength_L Strength_H Temp_L Temp_H Checksum

Byte0 0x59, frame header, same for each frame
Byte1 0x59, frame header, same for each frame
Byte2 Dist_L distance value lower by 8 bits
Byte3 Dist_L distance value higher by 8 bits
Byte4 Strength_L low 8 bits
Byte5 Strength_L high 8 bits
Byte6 Temp_L low 8 bits (suit for version later than V1.3.0)
Byte7 Temp_H high 8 bits (suit for version later than V1.3.0)
Byte8 Checksum is the lower 8 bits of the cumulative sum of the numbers of the first 8 bytes.
"""
import time
from datetime import datetime
from struct import unpack
from typing import Generator, Tuple

import serial

from kv.redis_kv import models
from py_scripts.custom_logger import logger
from py_scripts.smoothing_window import MedianWindow, clamp

HEADER_BYTE = 0x59
TFMINI_BAUDRATE = 115200

# Timeouts
TFMINI_MAX_MEASUREMENT_ATTEMPTS = 10
TFMINI_MAX_BYTES_BEFORE_HEADER = 10

# packet = [0x59, 0x59, distL, distH, strL, strH, tempL, tempH, checksum]
# The frame size is nominally 9 characters, but we don't include
# the first two 0x59's marking the start of the frame
TFMINI_FRAME_HEADER_SIZE = 2
TFMINI_FRAME_CONTENT_SIZE = 7
TFMINI_FRAME_SIZE = TFMINI_FRAME_HEADER_SIZE + TFMINI_FRAME_CONTENT_SIZE

MIN_DISTANCE = 0
MAX_DISTANCE = 1000

READ_TIMEOUT = 1


class TFminiError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TFMiniReader:
    def __init__(self, ser: serial.Serial) -> None:
        self.ser = ser

    def _flush_buffer(self) -> None:
        # custom buffer flush to keep some frames ahead
        # 5 frames ahead, ok.
        skip_bytes = self.ser.in_waiting - TFMINI_FRAME_SIZE * 5
        if skip_bytes > 0:
            self.ser.read(skip_bytes)

    def _find_header(self) -> None:
        numBytesRead = 0
        last = 0x00
        while True:
            bytes = self.ser.read(1)
            if len(bytes) != 1:
                raise TFminiError(f"ERROR_BAD_FRAME_SIZE(n={len(bytes)})")
            cur = bytes[0]
            if last == HEADER_BYTE and cur == HEADER_BYTE:
                return
            last = cur
            numBytesRead += 1
            if numBytesRead > TFMINI_MAX_BYTES_BEFORE_HEADER:
                raise TFminiError("ERROR_SERIAL_NOHEADER")

    def _read(self) -> Tuple[int, int, int]:
        self._find_header()
        frame = self.ser.read(TFMINI_FRAME_CONTENT_SIZE)
        if len(frame) != TFMINI_FRAME_CONTENT_SIZE:
            raise TFminiError(f"ERROR_BAD_FRAME_SIZE(n={len(frame)})")

        distance, strength, temperature, checksumByte = unpack("<HHHB", frame)
        temperature = temperature / 8 - 256
        checksum = (HEADER_BYTE + HEADER_BYTE + sum(frame[0:-1])) & 0xFF

        if checksum != checksumByte:
            msg = f"ERROR_BAD_CHECKSUM(chkb={checksumByte}, chk={checksum})"
            raise TFminiError(msg)

        return distance, strength, temperature

    def read_iter(
        self,
    ) -> Generator[Tuple[int, int, int], None, None]:
        time.sleep(0.2)  # Give port 200ms to initialize
        if self.ser.in_waiting == 0:
            raise TFminiError("Port is not ready")

        self._flush_buffer()
        while self.ser.in_waiting >= TFMINI_FRAME_SIZE:
            try:
                # все равно не успеваем вычитывать весь трафик,
                # так как спим 100мс, а лидар отправляет раз в 10мс
                data = self._read()
                yield data
            except TFminiError as err:
                logger.info("TFmini retry", cause=str(err))


class Cooldown:
    def __init__(self, dt: float) -> None:
        # dt in seconds
        self.dt = dt
        self.prev_time = time.time()

    def check(self) -> bool:
        dt = time.time() - self.prev_time
        if dt > self.dt:
            self.prev_time = time.time()
            return True
        return False


def process(
    redis_cooldown: Cooldown,
    window: MedianWindow,
    log_buf: "list[int]",
    buff: "list[int]",
) -> None:
    # TODO: get path to the serial port from the Settings
    port = "/dev/ttyUSB1"
    with serial.Serial(
        port,
        baudrate=TFMINI_BAUDRATE,
        timeout=READ_TIMEOUT,
    ) as ser:
        tfmini = TFMiniReader(ser)
        for distance, strength, temperature in tfmini.read_iter():
            if distance == 0 and strength < 100:
                distance = MAX_DISTANCE

            log_buf.append(distance)

            range = int(clamp(distance, MIN_DISTANCE, MAX_DISTANCE))

            if len(buff) == 0 or len(buff) == 8 or buff[-1] < range:
                buff.clear()
                buff.append(range)
                window.append(range)
                avg_range = int(window.smoothed_value())

                if redis_cooldown.check():
                    last_time = str(datetime.now().isoformat())
                    models.set_prop_value("LIDAR__TEMPERATURE", temperature)
                    models.set_prop_value("LIDAR__STRENGTH", strength)

                    models.set_prop_value("LIDAR__DISTANCE", range)
                    models.set_prop_value("LIDAR__RANGE_AVG", avg_range)
                    models.set_prop_value("LIDAR__LAST_TIME", last_time)

                    models.set_prop_value("DISTANCE", range)
                    models.set_prop_value("DISTANCE__AVG", avg_range)
                    models.set_prop_value("DISTANCE__LAST_TIME", last_time)
                    logger.info(
                        "Redis save",
                        avg_range=avg_range,
                        last_time=last_time,
                        history=log_buf,
                    )
                    logger.info(
                        "Lidar stats",
                        temperature=temperature,
                        strength=strength,
                        range=range,
                    )
                    log_buf.clear()
            else:
                buff.append(range)


def main() -> None:
    redis_cooldown = Cooldown(1)
    lidar__range_avg = int(
        models.get_prop_value("LIDAR__RANGE_AVG", "0") or "0",
    )
    window: MedianWindow = MedianWindow(
        size=5,
        init_value=lidar__range_avg,
    )

    log_buf = [lidar__range_avg]
    buff: list[int] = []
    while True:
        try:
            process(redis_cooldown, window, log_buf, buff)
        except KeyboardInterrupt:
            logger.info("Aborted by user")
            return
        except TFminiError as err:
            logger.warn("TFmini", err=str(err))
            time.sleep(5)
            # retry...
        except Exception:
            logger.exception("Failed to process TFmini")
            time.sleep(5)
            # retry...

        time.sleep(1)


if __name__ == "__main__":
    main()
