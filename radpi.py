#!/home/pi/envs/radpc_scale/bin/python

import zmq
import serial
import time
from  multiprocessing import Process, Queue

import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

def uart_client(rq, sq):
    while True:
        if not(rq.empty()):
            print('')
            print('TESTING UART')
            msg = rq.get()
            print(msg.data)

            try:
                ser.write(msg.data) 
                ser.flush()

                #time.sleep(3)
                #print('done sleeping')

                if ser.in_waiting > 0:
                    radpc_msg = ser.readline()

                    # put RadPC message into send_queue for transmission back through FCU
                    sq.put(radpc_msg)
                   
                    ''' 
                    print("UART COMM")
                    #print(ser.readline())
                    print('')
                    packet = radpc_msg.decode('ascii') # receive packet 
                    print(packet)
                    '''

                    '''
                    print("UART COMM: {}".format(ser.read()))
                    command = ser.read() # read a single byte
                    if(command == b'\x24'):
                        command = b'\x24' # '$' character in hex
                        ser.write(command) # respond with received byte
                        ser.flush()
                    else:
                        packet = ser.readline().decode('ascii') # receive packet 
                        print(packet)
                    '''
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
        print(msg)
        # instantiate Protobuf object
        FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()
        # load data from socket into Protobuf object
        FCUMessage.ParseFromString(msg)

        # send message to multiprocess Queue
        # for use by process that interfaces with RadPC
        rq.put(FCUMessage) 

        # print messages to STDOUT
        print(FCUMessage.messageSentTS)
        print(FCUMessage.data)

        #socket.send_string("received the message")

        # check if there are messages from RadPC
        if not(sq.empty()):
            radpc_msg = sq.get()

            print('')
            print('radpc_msg')
            print(radpc_msg)

            print('*** sending response')
            # send confirmation back to text menu
            try:
                protoBufMsg = getProtoBufMessage(radpc_msg) 
                protoBufMsg.SerializeToString()
                socket.send(protoBufMsg.SerializeToString())
            except Exception as e:
                print(e)
            print('next')
        
        #time.leep(1)

if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()

    receive_q = Queue()
    send_q = Queue()
    Process(target=zmqclient, args=(receive_q, send_q, )).start()
    Process(target=uart_client, args=(receive_q, send_q, )).start()
