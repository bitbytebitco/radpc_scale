#!/home/pi/envs/radpc_scale/bin/python

import zmq
import serial
import time
from  multiprocessing import Process, Queue, Lock

import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

DEBUG=True

if DEBUG:
    SERIAL_PORT = '/dev/ttyACM0'
    BAUD_RATE = 9600
else:
    SERIAL_PORT = '/dev/tty.usbmodem14203'
    BAUD_RATE = 115200 
    
def uart_client(rq, sq, lock):
    while True:
        if not(rq.empty()):
            msg = rq.get()

            try:
                #lock.acquire()
                ser.write(msg) 
                #ser.flush()

                #if ser.in_waiting > 0:
                #radpc_msg = ser.readline()
                radpc_msg = ser.read(256)
                print('UART RESPONSE:')
                print(radpc_msg)
		
                # put RadPC message into send_queue for transmission back through FCU
                sq.put(radpc_msg)
                   
            except Exception as e:
                print('error')
                print(e)   

def zmqclient(rq, sq, socket):
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
    
    # print messages to STDOUT
    print(FCUMessage.messageSentTS)
    print(FCUMessage.data)
    
def check_send_q(sq, socket ):
    try:
        #if not(sq.empty()):
        radpc_msg = sq.get()
        
        print('check_send_q')
        print(radpc_msg)
        #if len(radpc)>0:
        #    print('')
        #    print('UART: radpc_msg')
        #    print(radpc_msg)

        print('*** sending response')
        # send confirmation back to text menu
        protoBufMsg = getProtoBufMessage(radpc_msg) 
        protoBufMsg.SerializeToString()
        socket.send(protoBufMsg.SerializeToString(), zmq.NOBLOCK)
        #lock.release()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    lock = Lock()

    # Serial 
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    #ser.flush()
    ser.reset_input_buffer()

    # 0MQ 
    port = "5555"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:%s" % port)

    
    rq = Queue()
    sq = Queue()

    Process(target=uart_client, args=(rq, sq, lock, )).start()
    #Process(target=zmqclient, args=(receive_q, send_q, socket,)).start()
    #Process(target=check_send_q, args=(send_q, socket, lock, )).start()

    while True:
        zmqclient(rq, sq, socket) 
        
        check_send_q(sq, socket) 


