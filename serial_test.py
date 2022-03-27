import serial

data = {
    "667047883-vuvip": {
        "name": "Gabriella",
        "languagePreference": "English",
        "IC": "T0012345A",
        "address": "Blk 884 yishun street 81",
        "DOB": "1-1-2000",
        "bloodType": "O+",
        "emergencyContact": "81234567",
        "relationshipOfEmergencyContact": "Mother"
    }
}

# Set up the Serial connection to capture the Microbit communications
ser = serial.Serial()
ser.baudrate = 115200
ser.port = "COM8"
ser.open()

while True:

    if ser.in_waiting > 0:

        microbitdata = str(ser.readline())
        uniqueIdentifier = microbitdata[3:22].strip()
        # print(microbitdata)
        print(uniqueIdentifier)
        if(uniqueIdentifier == data[0]):
            print(data)