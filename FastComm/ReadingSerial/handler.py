import serial
import time


# The port can be found in Arduino Text Editor -> Tools -> The port of your arduino nano.
port = '/dev/cu.usbmodem14101'
baud = 2000000
max_data_count = 1000


# Data buffer, where all the data is stored before the program terminated.
binary_buffer = []
decoded_buffer = []


# Timer to measure the time the serial port connection establishment.
start_time = time.time()

# Connect to serial port.
ser = serial.Serial(port, baud)
binary_data = ser.readline()
count = 0

end_time = time.time()
print("Time to read open the serial port is " + str(end_time - start_time) + " Seconds.")

# Timer to measure actual data receiving time.
start_time = time.time()

# Add received binary data to buffer.
while binary_data and count < max_data_count:
    binary_buffer.append(binary_data)
    binary_data = ser.readline()
    count += 1


end_time = time.time()
print("Time to read " + str(max_data_count) + " pieces of data took " + str(end_time - start_time) + " Seconds.")


# Converts binary data to utf-8 data.
for b in binary_buffer:
    try:
        # Converts string "a,b,c,d" to a list of integer [a,b,c,d]
        decoded_data = b.decode().rstrip().split(",")
    except UnicodeDecodeError:
        # There might have garbage in serial port at the beggining,
        # Just skip the garbage data.
        continue

    decoded_buffer.append(decoded_data)


# ALWAYS CLOSE THE SERIAL PORT WHEN FINISHED!!!!
ser.close()


# Writing data to file.
file = open("data.csv", "w")

for data in decoded_buffer:
    file.write(",".join(data) + "\n")

file.close()
