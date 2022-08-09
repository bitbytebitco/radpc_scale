"""
general

    Script to send messages to the SWICD payload interface on an FCU. A single message can
    be sent, or messages can be sent in a loop periodically.

    Example:
        # python send_data_from_payload.py 10.32.40.179

    When sending messages, tail the log of flightcontroller on the FCU to see when it is
    received:
        vriuser@sem122:~$ tail -F /opt/vista/log/flightcontrol.log | grep SWICD | grep -v "INS"
        WARN 2018-09-11 18:22:39,522 [SWICDManager:468] - Received a payload message from id 1 with length of 0
        INFO 2018-09-11 18:22:39,522 [SWICDManager:485] - Payload message to send to ground: data size=0
        WARN 2018-09-11 18:22:39,522 [SWICDManager:515] - Sending out payload 1 message. Time since last message 865.208586 secs
        INFO 2018-09-11 18:22:39,523 [SWICDManager:520] - Successfully send payload 1 message via Iridium

    Also, watch the sirs-monitor log to see if the message was received on the Reachback:
        Sep 11 18:23:18.422     --> M: DADA Src: 0133/08 Dst: 000A/08 Via: 02 Len:  28 Type: User Subtype: Payload
"""
from argparse import ArgumentParser
import logging
import sys
from time import gmtime, sleep

import zmq

import FCU_SWICD_PayloadMessage_pb2

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s():%(lineno)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO)
logging.Formatter.converter = gmtime

log = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description='FCU payload data test application.')
    parser.add_argument('host',
                        help='host (FCU) IP address to connect to')
    parser.add_argument('-c', dest='count', default=1, type=int,
                        help='number of times to send the message. '
                             'A value of 0 will repeat forever until Ctl-C is received. '
                             '(default: 1)')
    parser.add_argument('-d', dest='delay', default=60, type=int,
                        help='delay between messages in seconds. '
                             '(default: 60)')
    parser.add_argument('-m', dest='message', default="", type=str,
                        help='the message to send (as text). '
                             '(default: empty)')
    parser.add_argument('-p', dest='port', default=5561, type=int,
                        help='host (FCU) port to connect to'
                             '(default: 5561)')
    args = parser.parse_args()
    addr = f"tcp://{args.host}:{args.port}"

    log.info(f"ADDR:    {addr}")
    log.info(f"COUNT:   {args.count}")
    log.info(f"DELAY:   {args.delay}")
    log.info(f"MESSAGE: {args.message}")

    log.info(f"Connect to {addr}")
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.linger = 1000  # One second wait before giving up
    socket.connect(addr)
    log.info("Connected")

    message_count = 1
    while args.count is 0 or message_count <= args.count:
        log.info(f"Send Message {message_count} of {args.count}")
        try:
            payloadMsg = FCU_SWICD_PayloadMessage_pb2.FCU_SWICD_PayloadMessage()
            payloadMsg.data = args.message.encode('utf-8')
            socket.send(payloadMsg.SerializeToString())
            if message_count != args.count:
                sleep(args.delay)
            message_count += 1
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.exception(str(e))
            sys.exit(1)

    log.info("Disconnect")
    socket.disconnect(addr)
    socket.close()
    context.term()
    log.info("Done")


if __name__ == '__main__':
    main()
