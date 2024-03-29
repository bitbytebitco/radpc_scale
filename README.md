# RadPi Overview

RadPi (radpi.py) is a python program built act as an interconnect between the [RadPC Hardware Platform](https://www.montana.edu/blameres/research_overview.html) and the Raven Aerostar FCU that serves a ground-to-payload communications link using the Iridium Satellite network. This program is intended to be run throughout the duration of the **RadPC@Scale test**, which involve high altitude ballooning missions with RadPC as its payload.

## High-level block diagram
![alt text](https://github.com/bitbytebitco/radpc_scale/blob/master/radpi_diagram.png "Logo Title Text 1")

## Installation

Create virtual environment with python 
```
python3 -m venv radpc_scale
```
Activate virtual environment 
```
cd radpc_scale/bin
source activate
```
Install dependencies
``` 
pip install requirements.txt 
```

## Usage
```
usage: radpi.py [-h] fcu_ip fcu_port

RadPC communication interlink (for use with Raven Thunderhead FCU and RadPC
Lunar)

positional arguments:
  fcu_ip      FCU IP address
  fcu_port    FCU port

optional arguments:
  -h, --help  show this help message and exit
```

## Important note about Static IP
In the /etc/dhcpcd.conf file there is a line towards the bottom of the file which holds the static ip:
```
interface eth0
static ip_address=10.1.3.7/24
```

## Functional Descriptions 
### fcusim.py
* Simulation of the FCU 
* Use for sending commands to radpi.py

### radpi.py
* Makes UART connection to primitive RadPC simulation running on Arduino 
* Makes ZeroMQ connection to fcusim.py, and waits for commands

### radpi_callback.py
* Python Tornado webserver for receiving callback messages and providing visualization
* Visualization done with charts.js (see radpc_scale/callback_server/static/charting.js)


