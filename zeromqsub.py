import zmq
import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage
from  multiprocessing import Process
import time

def client(port="5555"):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:%s" % port)

    while True:
        # receive data from zmq socket
        msg = socket.recv()
        # instantiate Protobuf object
        FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()
        # load data from socket into Protobuf object
        FCUMessage.ParseFromString(msg)

        # print messages to STDOUT
        print(FCUMessage.messageSentTS)
        print(FCUMessage.data)

        # SEND COMMAND TO RADPC

        #

        socket.send_string("received the message")
        time.sleep(1)

if __name__ == "__main__":

    #Process(target=client, args=(server_ports,)).start()
    Process(target=client).start()
