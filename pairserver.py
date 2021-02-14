import zmq
import random
import sys
import time

import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

port = "5555"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

while True:
    #msg_data = b"this is a test"
    msg_data = b"0x24"
    protoBufMsg = getProtoBufMessage(msg_data) 
    protoBufMsg.SerializeToString()

    socket.send(protoBufMsg.SerializeToString())
    msg = socket.recv()
    print(msg)
    print('')
    time.sleep(1)
