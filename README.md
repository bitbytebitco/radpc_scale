# RadPi (RadPC@Scale) Overview

## Installation
``` 
pip install requirements.txt 
```
## Running in Development Mode
### fcusim.py
* Simulation of the FCU 
* Use for sending commands to radpi.py

### radpi.py
* Makes UART connection to primitive RadPC simulation running on Arduino 
* Makes ZeroMQ connection to fcusim.py, and waits for commands

## Running Live
