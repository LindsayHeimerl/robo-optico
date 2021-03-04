import serial

ser = serial.Serial('/dev/ttyACM0', baudrate=115200)
print(ser.read(4))

def SetMotors(left, right):
    print(left, right)
    left *= 128
    right *= 128

    left += 128
    right += 128

    if left < 0:
        left = 0
    elif left > 255:
        left = 255

    if right < 0:
        right = 0
    elif right > 255:
        right = 255

    ser.write(bytearray([int(left), int(right)]))

def QueryIrSensor():
    return 1000
