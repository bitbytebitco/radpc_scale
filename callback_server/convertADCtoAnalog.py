import warnings

"""
Author: Colter Barney
Date: 06/14/2021


This file contains the functions needed to convert ADC values from the RADPC Lunar experiment's telemetry packets to the analog values they represent
The intended use of this code is to be imported into another python script and used as a library. example below

import convertADCtoAnalog as cv
keyes = cv.getKeyes()
# Store ADC values as hex strings parsed from telemetry packets
ADC_strings = [DATA_GOES_HERE]
ADC_values = []
for i, key in enumerate(keyes):
    ADC_values.append((getDecimalValueFromADC(ADC_strings[i],key),key))
# ADC_values now is a list of tuples, where each tuple contains the analog value and the key associated
print(value[1],value[0],sep=" : ") # print all the analog values

"""
# Conversion Constants Declarations
ONE_BIT = 2.5/4096
CURRENT = 1/25
A7_TEMP_SLOPE = -337.36
A7_TEMP_OFFSET = 237.38
MSP_TEMP_SLOPE = 400
MSP_TEMP_OFFSET = -280
# Dictionary used to convert values
conversion_factors = {"1.0 V":1, "1.0 C":CURRENT, "1.8 V":1, "1.8 C":CURRENT, "2.5 V":2, "2.5 C":CURRENT, "3.3 V":2, "3.3 C":CURRENT, "5.0 V":4, "5.0 C":CURRENT, "28.0 V":16, "28.0 C":CURRENT,"A7 Temp":(A7_TEMP_SLOPE,A7_TEMP_OFFSET), "MSP Temp":(MSP_TEMP_SLOPE, MSP_TEMP_OFFSET)}

def getDecimalValueFromADC(ADC_value: str, value_converting: str) -> float:
    """Function for converting ADC values from the RADPC Lunar demonstration telemetry packet. The ADC_values come in as a hex string in the format "####" or "0x####". 
    The value converting is a string, used as a key to determine the correct scalings factors in the conversion. See getKeyes for more information"""

    if (not isinstance(value_converting,str)):
        warnings.warn("value_converting input not a string, attempting a type conversion")
        str(value_converting)

    ADC_value = int(ADC_value,16)*ONE_BIT
    print(ADC_value)
    if(value_converting not in conversion_factors.keys()):
        warnings.warn("value_converting key not found. Please check the spelling and use getKeyes() to obtain acceptable values")
        return -1;
    if((value_converting == "MSP Temp") or (value_converting == "A7 Temp")):
        value = ADC_value * conversion_factors[value_converting][0] + conversion_factors[value_converting][1]
    else:
        value = ADC_value * conversion_factors[value_converting]
    return value

def getKeyes():
    """Function for retrieving the keys used in the getDecimalValueFromADC function. This function returns a dict_keys object containing the keys as strings.
    The dict_keys object is enumerable, meaning it can be used in for loops to loop through all the keys."""
    return conversion_factors.keys()

# Below are methods for doing a sinle type of conversion if that is more desirable. They just call the above conversion function with hard coded keyes

def convert1V0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"1.0 V")

def convert1C0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"1.0 C")

def convert1V8(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"1.8 V")

def convert1C8(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"1.8 C")

def convert2V5(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"2.5 V")

def convert2C5(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"2.5 C")

def convert3V3(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"3.3 V")

def convert3C3(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"3.3 C")

def convert5V0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"5.0 V")

def convert5C0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"5.0 C")

def convert28V0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"28.0 V")

def convert28C0(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"28.0 C")

def convertMSPTemp(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"MSP Temp")

def convertA7Temp(ADC_value: str) -> float:
    return getDecimalValueFromADC(ADC_value,"A7 Temp")
