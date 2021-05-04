#!/home/pi/envs/radpc_scale/bin/python

import time
import serial

SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200


if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()

    time.sleep(1)

    # heartbeat
    ser.write(b'\x24') 
    print(ser.read(12))
    
    # \x25  
    ser.write(b'\x22') 
    message = ser.read(128)
    print(message[0:24], end='')
    print(message[24:].hex())

        
