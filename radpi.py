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
    
def uart_client(rq, sq):
    while True:
        if not(rq.empty()):
            msg = rq.get()

            try:
                ser.write(msg) 

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

def listen_for_command(rq, sq, socket):
    ''' RECEIVE FROM FCU ''' 
    # receive data from zmq socket
    msg = socket.recv()
    
    # instantiate Protobuf object
    FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()
    # load data from socket into Protobuf object
    FCUMessage.ParseFromString(msg)

    # Enter msg into Queue (To send to RadPC)
    rq.put(FCUMessage.data) 
   
    # messages to STDOUT
    if DEBUG: 
        print("## MSG from fcusim.py")
        print(msg)
        print(FCUMessage.messageSentTS)
        print(FCUMessage.data)
    
def respond_to_fcusim(sq, socket ):
    try:
        #if not(sq.empty()):
        radpc_msg = sq.get()
        
        print('respond_to_fcusim')
        print(radpc_msg)

        print('*** sending response')
        protoBufMsg = getProtoBufMessage(radpc_msg) 
        protoBufMsg.SerializeToString()
        socket.send(protoBufMsg.SerializeToString(), zmq.NOBLOCK)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    # Serial 
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    #ser.flush()
    ser.reset_input_buffer()

    # 0MQ 
    port = "5555"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.setsockopt(zmq.SNDHWM, 0)
    socket.setsockopt(zmq.RCVHWM, 0)
    socket.connect("tcp://localhost:%s" % port)

    # Thread-safe Queues 
    rq = Queue()
    sq = Queue()

    Process(target=uart_client, args=(rq, sq, )).start()
    #Process(target=listen_for_command, args=(receive_q, send_q, socket,)).start()
    #Process(target=respond_to_fcusim, args=(send_q, socket, )).start()

    while True:
        listen_for_command(rq, sq, socket) 
        respond_to_fcusim(sq, socket) 


