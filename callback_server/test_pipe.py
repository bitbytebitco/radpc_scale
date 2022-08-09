import logging
import signal
import subprocess
import time
from os import kill

import numpy as np
from PIL import Image

''' Description
This script is used in junciton with proto_subprocess.py.
Parent: proto_parentprocess.py
Sub   : proto_subprocess.py

Parent create Sub using subprocess. Sub generates images and sends to PIPE. Parent gets images from PIPE and saves it.
This process is running in loop.
'''

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger()


def main():
    # Some settings
    cmd = ['/media/kent/DISK2/virtualenv_gallery/py27_tf1_10/bin/python', './proto_subprocess.py']
    final_shape = [151, 100, 3]
    sleep_time = 0.5  # in sec
    save_dir = './protoParentProcessOutput.jpeg'

    # Create the subprocess
    talkpipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    logger.info('Subprocess PID: {}'.format(talkpipe.pid))
    try:
        while True:
            line = talkpipe.stdout.readline()
            line = line.decode('utf-8')
            line = line.strip()
            if line:
                line = line.replace('[', '')
                line = line.replace(']', '')
                np_output = np.fromstring(line, dtype=np.int, sep=' ')
                img = np.reshape(np_output, final_shape)
                img = img.astype('uint8')
                im = Image.fromarray(img)
                im.save(save_dir)
                logger.info('Image saved to {}'.format(save_dir))
            else:
                logger.warning('No data.')
            time.sleep(sleep_time)  # for stabilization purpose
    except KeyboardInterrupt:
        logger.warning('Killing child...')
        kill(talkpipe.pid, signal.SIGTERM)
    finally:
        kill(talkpipe.pid, signal.SIGTERM)
        logger.warning('Killed.')


if __name__ == '__main__':
    main()


