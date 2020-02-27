import serial
import time


ser = serial.Serial('/dev/ttyS3', 9600)
time.sleep(2)

b = ser.readline()
print(b.decode().rstrip())

ser.close()
