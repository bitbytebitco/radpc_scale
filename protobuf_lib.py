import time
import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 

DEBUG=False

def getProtoBufMessage(data):
    FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()

    FCUMessage.messageSentTS=time.time()
    FCUMessage.messageReceivedTS=time.time()
    FCUMessage.data=data

    if DEBUG:
        print(FCUMessage)
        print(dir(FCUMessage))
        print(FCUMessage.data)

    return FCUMessage


