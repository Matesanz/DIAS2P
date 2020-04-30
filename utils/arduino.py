import serial
import time


class arduino():
    
    """
    Connects to usb plugged arduino for PC testing
    """
    ser = None


    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", 9600)
        print('conecting to arduino')
        time.sleep(2)

    def turn_on_arduino(self):
        self.ser.write(b'H')

    def turn_off_arduino(self):
        self.ser.write(b'L')

    def close(self):
        self.ser.close()

    def trial(self):
        # Define the serial port and baud rate.
        # Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager

        def led_on_off():
            user_input = input("\n Type on / off / quit : ")
            if user_input == "on":
                print("LED is on...")
                time.sleep(0.1)
                self.ser.write(b'H')
                led_on_off()
            elif user_input == "off":
                print("LED is off...")
                time.sleep(0.1)
                self.ser.write(b'L')
                led_on_off()
            elif user_input == "quit" or user_input == "q":
                print("Program Exiting")
                time.sleep(0.1)
                self.ser.write(b'L')
                self.ser.close()
            else:
                print("Invalid input. Type on / off / quit.")
                led_on_off()

        led_on_off()

if __name__ == "__main__":
    arduino().trial()
