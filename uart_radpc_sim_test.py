#!/home/pi/envs/radpc_scale/bin/python

import time
import serial

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600 

if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    ser.reset_input_buffer()

    time.sleep(2)

    # heartbeat
    #ser.write(b'\x24') 
    #print(ser.read(10))
    
    # \x25  
    ser.write(b'\x25') 
    print(ser.readline())
        
