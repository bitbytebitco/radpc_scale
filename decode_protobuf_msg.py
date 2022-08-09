import base64
import FCU_SWICD_PayloadMessage_pb2 as PayloadMessage 
from protobuf_lib import getProtoBufMessage

ONE_BIT = 2.5/4096

def main(msg):
    # instantiate Protobuf object
    FCUMessage = PayloadMessage.FCU_SWICD_PayloadMessage()
    # load data from socket into Protobuf object
    FCUMessage.ParseFromString(msg)

    print(FCUMessage.data)

if __name__ == "__main__":
    
    #protoBufMsg = getProtoBufMessage(b"0x22") 
    #print(protoBufMsg.SerializeToString())
    #print('')
    bytes_str = base64.b64decode("TW9udGFuYSBTdGF0ZSBVbml2LVJBRFBDAAVEBnYKowuhC0MICQRvCr0A8w//DcMKfQY9A8sAAMzMvAAAAAAAAAAAAAAAAAAAAAAABQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    print('')
    print("{}{}".format(bytes_str[0:24], bytes_str[24:].hex()))
    
