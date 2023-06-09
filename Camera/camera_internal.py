# Test following https://learn.adafruit.com/ttl-serial-camera/circuitpython-python-usage
# Updated by Charis Houston


# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""VC0706 image capture to local storage.
You must wire up the VC0706 to a USB or hardware serial port.
Primarily for use with Linux/Raspberry Pi but also can work with Mac/Windows"""

import time
import busio
import board
from datetime import datetime;
import adafruit_vc0706
import serial

class Internal_Camera:
    camera = None
    IMAGE_FILE = ''
    IMAGE_FILE_PREFIX = '/home/trapsat/Desktop/Janus_Photos/image'
    IMAGE_EXTENSION = '.jpg'  
    image_no = 0

    def update_image_file(self):
        self.IMAGE_FILE = self.IMAGE_FILE_PREFIX + datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + self.IMAGE_EXTENSION
        print(self.IMAGE_FILE)
        #self.image_no += 1
    
    def __init__(self):
        uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.25)
        # Setup VC0706 camera
        self.camera = adafruit_vc0706.VC0706(uart)
        print("VC0706 version:")
        print(self.camera.version)
        self.camera.image_size = adafruit_vc0706.IMAGE_SIZE_640x480
        size = self.camera.image_size
        if size == adafruit_vc0706.IMAGE_SIZE_640x480:
            print("Using 640x480 size image.")
        elif size == adafruit_vc0706.IMAGE_SIZE_320x240:
            print("Using 320x240 size image.")
        elif size == adafruit_vc0706.IMAGE_SIZE_160x120:
            print("Using 160x120 size image.")

    def reset(self):
        print("Error capturing image, retaking picture")
        time.sleep(3)
        self.take_picture()

    def take_picture(self):
        self.update_image_file()
        if not self.camera.take_picture():
            print("Camera Internal Error: Could not take picture.")
            return
        # Print size of picture in bytes.
        frame_length = self.camera.frame_length
        print("Picture size (bytes): {}".format(frame_length))

        # Open a file for writing (overwriting it if necessary).
        # This will write 50 bytes at a time using a small buffer.
        # You MUST keep the buffer size under 100!
        #print("Writing image: {}".format(self.IMAGE_FILE), end="", flush=True)
        stamp = time.monotonic()
        # Pylint doesn't like the wcount variable being lowercase, but uppercase makes less sense
        # pylint: disable=invalid-name
        with open(self.IMAGE_FILE, "wb") as outfile:
            wcount = 0
            while frame_length > 0:
                t = time.monotonic()
                # Compute how much data is left to read as the lesser of remaining bytes
                # or the copy buffer size (32 bytes at a time).  Buffer size MUST be
                # a multiple of 4 and under 100.  Stick with 32!
                to_read = min(frame_length, 32)
                copy_buffer = bytearray(to_read)
                # Read picture data into the copy buffer.
                if self.camera.read_picture_into(copy_buffer) == 0:
                    print("Camera Internal Error: Could not take picture.")
                    return
                # Write the data to SD card file and decrement remaining bytes.
                outfile.write(copy_buffer)
                frame_length -= 32
                # Print a dot every 2k bytes to show progress.
                wcount += 1
                if wcount >= 64:
                    #print(".", end="", flush=True)
                    wcount = 0
        print()
        # pylint: enable=invalid-name
        print("Finished in %0.1f seconds!" % (time.monotonic() - stamp))
        # Turn the camera back into video mode.
        self.camera.resume_video()

