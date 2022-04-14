#!/usr/bin/env python
#
# Original program based upon Atlas Scientific sample code script:
# https://github.com/AtlasScientific/Raspberry-Pi-sample-code.git
#
# Edited by Will Bradford, Megan Caulfield, and Alex Kreitzer to use UART interface and connect to a locally hosted MySQL database, automatically collect data,
# and input the data into our database.

import serial
import sys
import time
import string 
from serial import SerialException
import re
import math
import RPi.GPIO as GPIO
import mysql.connector



def read_line():
    """
    taken from the ftdi library and modified to 
    use the ezo line separator "\r"
    """
    lsl = len(b'\r')
    line_buffer = []
    while True:
        next_char = ser.read(1)
        if next_char == b'':
        
            break
        
        line_buffer.append(next_char)
        if (len(line_buffer) >= lsl and line_buffer[-lsl:] == [b'\r']):
            break
    return b''.join(line_buffer)
    
def read_lines():
    """
    also taken from ftdi lib to work with modified readline function
    """
    lines = []
    try:
        while True:
            line = read_line()
            if not line:
                break
                ser.flush_input()
            lines.append(line)
        return lines
                               

    except SerialException as e:
        printcursor( "Error, ", e)
        return None	

def send_cmd(cmd):
    """
    Send command to the Atlas Sensor.
    Before sending, add Carriage Return at the end of the command.
    :param cmd:
    :return:
    """
    buf = cmd + "\r"     	# add carriage return
    try:
        ser.write(buf.encode('utf-8'))
        return True
    except SerialException as e:
        print ("Error, ", e)
        return None							

            
if __name__ == "__main__":
    
    real_raw_input = vars(__builtins__).get('raw_input', input) # used to find the correct function for python2/3
    
    print("\nWelcome to the 2021-22 JMU Section 1 DAQ team's temperature sensor code\n")
    print("    This code defaults to collect data every 10 seconds")
    # to get a list of ports use the command: 
    # python -m serial.tools.list_ports
    # in the terminal
    usbport = '/dev/ttyAMA1' # change to match your pi's setup
    
    # open serial port to sensors
    try:
        ser = serial.Serial(usbport, 9600, timeout=0)
    except serial.SerialException as e:
        print( "Error, ", e)
        sys.exit(0)

    # load up database and get cursor....
    db = mysql.connector.connect(host="localhost",user="JMUWAM",passwd="rockcity",database="Section1DAQ")

    cursor = db.cursor()
    
    # run in an infinite loop polling sensors and storing in database
    while True:
            #clear all previous data
            time.sleep(1)
            ser.flush()
            
            try:
                while True:
                    send_cmd("R")
                    lines = read_lines()
                    for i in range(len(lines)):
                        # print lines[i]
                        if lines[i][0] != b'*'[0]:
                            my_temp=lines[i].decode('utf-8')
                            print( "Temp Reading: " + lines[i].decode('utf-8'))
                              
                            #Trim the temperature output to only numerical values & decimals
                            FinalTemp = re.sub('[^0-9,.]', '',my_temp)
                        
                           #Insert temp values into mysql table 
                            mysql_insert= "INSERT INTO Temp (Deg_F, Sent) VALUES (%s, %s)"
                            data= [FinalTemp, 0]
                            cursor.execute(mysql_insert,data)
                            db.commit()
                            print('Data Saved')
                   
                   #Changes the time intervals (in seconds) between each measurement
                            time.sleep(10)
         
         #The below code is needed for functionality of the rest of the script but s not used in practice
            except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
                print("Continuous polling stopped")
