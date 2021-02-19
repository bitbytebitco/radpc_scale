#!/home/pi/envs/radpc_scale/bin/python

import os
import zmq
import random
import sys
import time
import multiprocessing
from multiprocessing import Process, Queue
 
import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def display_menu():
    print(70 * "*")
    #print("{0} Options: {0}".format(30 * "*"))
    print("{0}{2}FCU (sim.){1}{1} <-- 0MQ (Protobuf) --> {0}{2}RPI{1}{1} <-- UART --> {0}{2}Arduino (RadPC sim.){1}{1} ".format(color.BOLD, color.END, color.DARKCYAN))
    print(70 * "*")
    print("Options:")
    print(8 * "*")
    print("1. Request Packet")
    print("2. Exit")
    print(70 * "-")

def text_menu(socket, rq, sq, kq, newstdin): 
        sys.stdin = newstdin
        try:
            display_menu() 
            choice = input("Enter your choice [1-2]:")
            try:
                choice = int(choice)
            except Exception as e:
                print(e)
                print('input exception')
            if choice == 1:
                print("{0}Requesting Packet{1}".format(color.BLUE,color.END))
                #sq.put(b'\x25\x01')    
                sq.put(b'\x25')    
            elif choice == 2:
                kq.put('1') 
            else:
                text_menu(socket, rq, sq, kq, newstdin)
        except EOFError:
            return 

class MyProcess(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, **kwargs)
        self.exit = multiprocessing.Event()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return_value = self._target( *self._args )
        while not self.exit.is_set():
           pass
        #print("You exited!")

    def shutdown(self):
        #print("Shutdown initiated")
        self.exit.set()

if __name__ == "__main__":
    try:
        kq = Queue()
        sq = Queue()
        rq = Queue()
        newstdin = os.fdopen(os.dup(sys.stdin.fileno()))

        port = "5555"
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.bind("tcp://*:%s" % port)

        p = MyProcess(target=text_menu, args=(socket, rq, sq, kq, newstdin , ))
        p.start()

        running = True
        while running:
            if not(sq.empty()):
                try:
                    p.shutdown()

                    msg = sq.get()
                    print(msg)

                    protoBufMsg = getProtoBufMessage(msg) 
                    protoBufMsg.SerializeToString()
                    socket.send(protoBufMsg.SerializeToString())
                    
                    #time.sleep(1)
     
                    print('### listening')
                except Exception as e:
                    print('here happened')
                    print(e) 
                try:
                    #msg = socket.recv(flags=zmq.NOBLOCK)
                    msg = socket.recv()
                    FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()

                    # load data from socket into Protobuf object
                    FCUMessage.ParseFromString(msg)

                    print("{0}MESSAGE FROM RADPC:{1}".format(color.RED, color.END))
                    print(FCUMessage.messageSentTS)
                    print(FCUMessage.data)
                except zmq.Again as e:
                    print("No message received yet")

                p = MyProcess(target=text_menu, args=(socket, rq, sq, kq, newstdin , ))
                p.start()

            if not(kq.empty()):
                socket.close()
                p.shutdown() 
                print("Goodbye")
                exit()

    except Exception as e:
        print(e)
        print("Goodbye")
        exit()
