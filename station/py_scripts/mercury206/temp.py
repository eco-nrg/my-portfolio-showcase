import serial
import time

# Initialize the serial port
ser = serial.Serial('COM4', baudrate=9600, parity=serial.PARITY_NONE,
    bytesize=8, stopbits=1, timeout=0.2)  # Replace 'COM4' with your port and 9600 with your baud rate


raw = """
38   IRP_MJ_WRITE      DOWN     02 d9 4d b6 2f c1 37 
44   IRP_MJ_WRITE      DOWN     02 d9 4d b6 66 00 c1 
50   IRP_MJ_WRITE      DOWN     02 d9 4d b6 28 80 f5 
56   IRP_MJ_WRITE      DOWN     02 d9 4d b6 29 41 35 
62   IRP_MJ_WRITE      DOWN     02 d9 4d b6 87 c0 89 
70   IRP_MJ_WRITE      DOWN     02 d9 4d b6 69 40 c5 
76   IRP_MJ_WRITE      DOWN     02 d9 4d b6 2c 81 36 
82   IRP_MJ_WRITE      DOWN     02 d9 4d b6 2b c0 f4 
88   IRP_MJ_WRITE      DOWN     02 d9 4d b6 61 41 03 
94   IRP_MJ_WRITE      DOWN     02 d9 4d b6 62 01 02 
100  IRP_MJ_WRITE      DOWN     02 d9 4d b6 86 ff c8 80 """

rwa2 = """
41   IRP_MJ_READ        UP                  02 d9 4d b6 2f 02 d9 4d b6 e8 97 
47   IRP_MJ_READ        UP                     02 d9 4d b6 66 09 01 23 c1 db 
53   IRP_MJ_READ        UP            02 d9 4d b6 28 01 00 00 06 04 15 b1 0a 
59   IRP_MJ_READ        UP                        02 d9 4d b6 29 03 60 f0 9f 
65   IRP_MJ_READ        UP                                                NaN
67   IRP_MJ_READ        UP  02 d9 4d b6 87 ea c8 f0 9f 04 15 b1 0a 37 00 0...
73   IRP_MJ_READ        UP            02 d9 4d b6 69 00 03 37 00 47 47 fb 67 
79   IRP_MJ_READ        UP         02 d9 4d b6 2c 03 13 11 00 09 08 23 cf 25 
85   IRP_MJ_READ        UP         02 d9 4d b6 2b 03 13 08 45 09 08 23 86 0d 
91   IRP_MJ_READ        UP         02 d9 4d b6 61 04 14 59 03 25 05 23 58 e8 
97   IRP_MJ_READ        UP         02 d9 4d b6 62 04 14 58 29 25 05 23 2d 25 
103  IRP_MJ_READ        UP  02 d9 4d b6 86 ff 08 02 00 00 03 00 00 00 00 0..."""

arrays = [
    [0x02, 0xd9, 0x4d, 0xb6, 0x2f, 0xc1, 0x37],
    [0x02, 0xd9, 0x4d, 0xb6, 0x66, 0x00, 0xc1],
    [0x02, 0xd9, 0x4d, 0xb6, 0x28, 0x80, 0xf5],
    [0x02, 0xd9, 0x4d, 0xb6, 0x29, 0x41, 0x35],
    [0x02, 0xd9, 0x4d, 0xb6, 0x87, 0xc0, 0x89],
    [0x02, 0xd9, 0x4d, 0xb6, 0x69, 0x40, 0xc5],
    [0x02, 0xd9, 0x4d, 0xb6, 0x2c, 0x81, 0x36],
    [0x02, 0xd9, 0x4d, 0xb6, 0x2b, 0xc0, 0xf4],
    [0x02, 0xd9, 0x4d, 0xb6, 0x61, 0x41, 0x03],
    [0x02, 0xd9, 0x4d, 0xb6, 0x62, 0x01, 0x02],
    [0x02, 0xd9, 0x4d, 0xb6, 0x86, 0xff, 0xc8, 0x80],
]
for arr in arrays:
    ser.write(arr)
    time.sleep(0.1)
    data = ser.read(32)
    print(data.hex())
