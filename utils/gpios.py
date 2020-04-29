#!/usr/bin/env python3

from utils.utils import is_jetson_platform
import time

if is_jetson_platform():
    import Jetson.GPIO as GPIO  # prevents GPIO to be imported on non jetson devices


def activate_jetson_board():
    
    """
    Activates jetson GPIO 18
    """
    
    # Pin 18 == 12 on the header
    output_pin = 18
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BCM)
    # set pin as an output pin with optional initial state of LOW
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.LOW)


def deactivate_jetson_board():
    
    """
    deactivates jetson GPIOs
    """
    
    GPIO.cleanup()


def security_OFF():
    """
    dummy function mimic GPIO OFF in Jetson devices
    """
    # print("SECURITY OFF")
    pass


def security_ON():
    """
    dummy function mimic GPIO ON in Jetson devices
    """
    # print("SECURITY ON")
    pass


def warning_ON(output_pin=18):
    
    """
    turns selected GPIO ON
    :param output_pin: int, GPIO position
    """
    
    GPIO.output(output_pin, GPIO.HIGH)


def warning_OFF(output_pin=18):
    
    """
    turns selected GPIO OFF
    :param output_pin: int, GPIO position
    """
    
    GPIO.output(output_pin, GPIO.LOW)


if __name__ == '__main__':
    
    """
    Quick check of GPIO 18
    """
    
    activate_jetson_board()
    try:
        while True:
            print('warnings activated')
            warning_ON()
            time.sleep(2)
            print('warnings OFF')
            warning_OFF()
            time.sleep(2)
    finally:
        deactivate_jetson_board()
