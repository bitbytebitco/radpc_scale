#!/usr/bin/python3

import os
import subprocess
import sys
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

while True:
    result = subprocess.run(["/home/beckerz/envs/raven_interface/bin/python3","/home/beckerz/radpc_scale/callback_server/send_data_to_payload.py","--jwt-path","eric_jwt.txt","--payload-id","1","https://flights.ravenind.com/api"])
    time.sleep(300)
    result = subprocess.run(["/home/beckerz/envs/raven_interface/bin/python3","/home/beckerz/radpc_scale/callback_server/send_data_to_payload.py","--jwt-path","eric_jwt.txt","--payload-id","2","https://flights.ravenind.com/api"])
    time.sleep(300)
