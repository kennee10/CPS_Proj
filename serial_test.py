import serial

# Set up the Serial connection to capture the Microbit communications
ser = serial.Serial()
ser.baudrate = 115200
ser.port = "COM9"
ser.open()

while True:

    microbitdata = str(ser.readline())
    uniqueIdentifier = microbitdata[3:22].strip()
    # print(microbitdata)
    print(uniqueIdentifier)