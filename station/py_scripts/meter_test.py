import time

import libscrc
import serial
from config import get_settings

settings = get_settings()

def convert_bytes(bytes_raw):
    crc16 = libscrc.modbus(bytearray(bytes_raw))

    new_list = bytes_raw + [0, 0]
    new_list[-2] = crc16 & 0xff
    new_list[-1] = crc16 >> 8

    return new_list

def main():
  port = settings.com_port
  serial_number = settings.serial_number

  stream = serial.Serial(port, 9600, timeout=1)
  time.sleep(0.1)

  stream.write(convert_bytes([serial_number, 0x00]))
  time.sleep(0.2)
  buf = list(stream.read(32))
  print(f"Test {buf}")

  password = [0x32, 0x32, 0x32, 0x32, 0x32, 0x32]
  stream.write(convert_bytes([serial_number, 0x01, 0x02] + password))
  time.sleep(0.2)
  buf = list(stream.read(32))
  print(f"Auth {buf}")


if __name__ == '__main__':
  main()
