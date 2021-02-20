#!/home/pi/envs/radpc_scale/bin/python

import zmq
import serial
import time
from  multiprocessing import Process, Queue

import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

#SERIAL_PORT = '/dev/ttyACM0'
SERIAL_PORT = '/dev/tty.usbmodem14203'
#BAUD_RATE = 9600
BAUD_RATE = 115200 

def uart_client(rq, sq):
    while True:
        if not(rq.empty()):
            msg = rq.get()

            try:
                ser.write(msg) 
                #ser.flush()

                #if ser.in_waiting > 0:
                #radpc_msg = ser.readline()
                radpc_msg = ser.read(256)
		
                # put RadPC message into send_queue for transmission back through FCU
                sq.put(radpc_msg)
                   
            except Exception as e:
                print('error')
                print(e)   
            print('testend')

def zmqclient(rq, sq, port="5555"):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:%s" % port)

    while True:
        ''' RECEIVE FROM FCU ''' 
        # receive data from zmq socket
        msg = socket.recv()
        print("## MSG from fcusim.py")
        print(msg)
        # instantiate Protobuf object
        FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()
        # load data from socket into Protobuf object
        FCUMessage.ParseFromString(msg)

        # send message to multiprocess Queue
        # for use by process that interfaces with RadPC
        rq.put(FCUMessage.data) 
        
        #time.sleep(2)

        # print messages to STDOUT
        print(FCUMessage.messageSentTS)
        print(FCUMessage.data)

        #socket.send_string("received the message")

        # check if there are messages from RadPC
        if not(sq.empty()):
            radpc_msg = sq.get()

            print('')
            print('UART: radpc_msg')
            print(radpc_msg)

            print('*** sending response')
            # send confirmation back to text menu
            try:
                protoBufMsg = getProtoBufMessage(radpc_msg) 
                protoBufMsg.SerializeToString()
                socket.send(protoBufMsg.SerializeToString(), zmq.NOBLOCK)
            except Exception as e:
                print(e)
            print('next')
        else:
            print('empty at the moment')
        
        #time.leep(1)

if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    #ser.flush()
    ser.reset_input_buffer()


    #ser.write(b'\x24') 
    #print(ser.read(10))

    '''
    try:
        print('test run')
        ser.write(b"0x24") 
        ser.flush()

        time.sleep(1)
        #if ser.in_waiting > 0:
        radpc_msg = ser.readline()
        print('radpc_msg')
        print(radpc_msg)
    except Exception as e:
        print(e)
    '''

        

    receive_q = Queue()
    send_q = Queue()


    receive_q.put(b"0x24") 

    Process(target=zmqclient, args=(receive_q, send_q, )).start()
    Process(target=uart_client, args=(receive_q, send_q, )).start()
