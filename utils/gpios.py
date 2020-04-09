#!/usr/bin/env python3
from utils.utils import is_jetson_platform

if is_jetson_platform():
    import Jetson.GPIO as GPIO
import time


def activate_jetson_board():
    # Pin 18 == 12 on the header
    output_pin = 18
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BCM)
    # set pin as an output pin with optional initial state of LOW
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.LOW)


def deactivate_jetson_board():
    GPIO.cleanup()


def warning_ON(output_pin=18):
    GPIO.output(output_pin, GPIO.HIGH)


def warning_OFF(output_pin=18):
    GPIO.output(output_pin, GPIO.LOW)


if __name__ == '__main__':
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
