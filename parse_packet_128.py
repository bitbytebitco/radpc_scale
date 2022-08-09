#!/usr/bin/env python
""" Parse information from the 128-byte sized packet.
"""

import base64

__author__ = "Colter Barney, Zachary Becker"
__maintainer__ = "Zachary Becker"
__email__ = "bitbytebitco@gmail.com"
__status__ = "Development"

ONE_BIT = 2.5/4096
CURRENT = 1/25
# FPGA Temperature constant multipliers
A7_TEMP_SLOPE = -337.36
A7_TEMP_OFFSET = 237.38
# MSP430 Temperature constant multipliers
MSP_TEMP_SLOPE = 400
MSP_TEMP_OFFSET = -280

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

def fdisp(key, value):
    print("{0}{2}{1} {3}".format(color.GREEN, color.END, key, value))

def get_packet_length(base64str):
    bytes_str = base64.b64decode(base64str)
    return len(bytes_str)

def parse_from_base64str(base64str):
    
    data = {} 
    bytes_str = base64.b64decode(base64str)

    ''' TESTING different parsing methods
    # Colter's Method 
    hex_str = bytes_str[51:53]
    print(hex_str.hex())
    print("decimal value: {}".format(int(hex_str.hex(), 16)))
    print(int(hex_str.hex(), 16)*ONE_BIT*MSP_TEMP_SLOPE+MSP_TEMP_OFFSET)

    # from_bytes method
    print('')
    print("decimal val:{}".format(int.from_bytes(bytes_str[51:53], byteorder="big", signed=False)))
    print(int.from_bytes(bytes_str[51:53], byteorder="big", signed=False)*ONE_BIT*MSP_TEMP_SLOPE+MSP_TEMP_OFFSET)
    '''

    #print(bytes_str[51:53])
    #print(bytes_str[51:53].hex())
    
    print(int(bytes_str[55:56].hex()[0], 16))
    print(int(bytes_str[55:56].hex()[1], 16))
    #if bytes_str[0:24] == b'Montana State Univ-RADPC' or :
    try:
        data = {
            'header': bytes_str[0:24],
            '1VV': int.from_bytes(bytes_str[27:29], byteorder="big", signed=False)*ONE_BIT,
            '1VC': int.from_bytes(bytes_str[29:31], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            '1.8VV': int.from_bytes(bytes_str[31:33], byteorder="big", signed=False)*ONE_BIT,
            '1.8VC': int.from_bytes(bytes_str[33:35], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            '2.5VV': int.from_bytes(bytes_str[35:37], byteorder="big", signed=False)*ONE_BIT*2,
            '2.5VC': int.from_bytes(bytes_str[37:39], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            '3.3VV': int.from_bytes(bytes_str[39:41], byteorder="big", signed=False)*ONE_BIT*2,
            '3.3VC': int.from_bytes(bytes_str[41:43], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            '5VV': int.from_bytes(bytes_str[43:45], byteorder="big", signed=False)*ONE_BIT*4,
            '5VC': int.from_bytes(bytes_str[45:47], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            '28VV': int.from_bytes(bytes_str[47:49], byteorder="big", signed=False)*ONE_BIT*16,
            '28VC': int.from_bytes(bytes_str[49:51], byteorder="big", signed=False)*ONE_BIT*CURRENT,
            'mcu_temp': int.from_bytes(bytes_str[51:53], byteorder="big", signed=False)*ONE_BIT*MSP_TEMP_SLOPE+MSP_TEMP_OFFSET,
            'fpga_temp': int.from_bytes(bytes_str[53:55], byteorder="big", signed=False)*ONE_BIT*A7_TEMP_SLOPE+A7_TEMP_OFFSET,
            'tile_00_cnt':int(bytes_str[55:56].hex()[0], 16),
            'tile_01_cnt':int(bytes_str[55:56].hex()[1], 16),
            'tile_02_cnt':int(bytes_str[56:57].hex()[0], 16),
            'tile_03_cnt':int(bytes_str[56:57].hex()[1], 16),
            'fpga_port_out_vote_cnt':int(bytes_str[57:58].hex(), 16),
            'fpga_port_in_vote_cnt':int(bytes_str[58:59].hex(), 16),
            'tile_00_fault_cnt':int(bytes_str[59:61].hex(), 16),
            'tile_01_fault_cnt':int(bytes_str[61:63].hex(), 16),
            'tile_02_fault_cnt':int(bytes_str[63:65].hex(), 16),
            'tile_03_fault_cnt':int(bytes_str[65:67].hex(), 16),
            #'fpga_temp2': int(bytes_str[53:55].hex(), 16)*ONE_BIT*A7_TEMP_SLOPE+A7_TEMP_OFFSET,
        }
        return data
    except Exception as e:
        print('ISSUE:Problem parsing packet')
        print(e)
        return None

def main():
    #data = parse_from_base64str("TW9udGFuYSBTdGF0ZSBVbml2LVJBRFBDAAVEBnYKowuhC0MICQRvCr0A8w//DcMKfQY9A8sAAMzMvAAAAAAAAAAAAAAAAAAAAAAABQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    data = parse_from_base64str("TW9udGFuYSBTdGF0ZSBVbml2LVJBRFBDAAvlBoIKHguLCkwIBwNfCrACNA//DiMEtwhUA8gAAN3dnQAAAAAAAAAAAAAAAAAAAAAABRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")

    # 1 Volt Rail
    fdisp("Header:", data['header'])
    fdisp("1.0V Rail Voltage:", data['1VV']) # Voltage
    fdisp("1.0V Rail Current:", data['1VC']) # Current

    # 1.8 Volt Rail
    fdisp("1.8V Rail Voltage:", data['1.8VV']) 
    fdisp("1.8V Rail Current:", data['1.8VC'])
    
    # 2.5 Volt Rail
    fdisp("2.5V Rail Voltage:", data['2.5VV']) 
    fdisp("2.5V Rail Current:", data['2.5VC'])

    # 3.3 Volt Rail
    fdisp("3.3V Rail Voltage:", data['3.3VV']) 
    fdisp("3.3V Rail Current:", data['3.3VC'])

    # 5 Volt Rail
    fdisp("5V Rail Voltage:", data['5VV']) 
    fdisp("5V Rail Current:", data['5VC'])

    # 28 Volt Rail
    fdisp("28V Rail Voltage:", data['28VV']) 
    fdisp("28V Rail Current:", data['28VC'])

    # temperatures
    fdisp("MCU Temp:", data['mcu_temp'])
    fdisp("FPGA Temp:", data['fpga_temp'])

    fdisp("tile 00:", data['tile_00_cnt'])
    fdisp("tile 01:", data['tile_01_cnt'])
    fdisp("tile 02:", data['tile_02_cnt'])
    fdisp("tile 03:", data['tile_03_cnt'])
    
    fdisp("fpga_port_out_vote_cnt:", data['fpga_port_out_vote_cnt'])
    fdisp("fpga_port_in_vote_cnt:", data['fpga_port_in_vote_cnt'])
   
    # tile fault count 
    fdisp("tile_00_fault_cnt:", data['tile_00_fault_cnt'])
    fdisp("tile_01_fault_cnt:", data['tile_01_fault_cnt'])
    fdisp("tile_02_fault_cnt:", data['tile_02_fault_cnt'])
    fdisp("tile_03_fault_cnt:", data['tile_03_fault_cnt'])

if __name__ == "__main__":
    main()
