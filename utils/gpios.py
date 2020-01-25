#!/usr/bin/env python3

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


def activate_warnings(output_pin=18):
    GPIO.output(output_pin, GPIO.HIGH)


def deactivate_warnings(output_pin=18):
    GPIO.output(output_pin, GPIO.LOW)


if __name__ == '__main__':
    activate_jetson_board()
    try:
        while True:
            print('warnings activated')
            activate_warnings()
            time.sleep(2)
            print('warnings OFF')
            deactivate_warnings()
            time.sleep(2)
    finally:
        deactivate_jetson_board()
