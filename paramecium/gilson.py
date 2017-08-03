'''
Controller for Gilson Minipulse 3
from
https://github.com/echo-oddly/gsioc_controller

Doesn' work: probably need to plug on the rs232
'''

# gsioc defines a class used for controlling gsioc devices
# ID is an integer
# immediate commands are an ascii string
# buffered commands are an ascii string

import datetime, time
import serial
import binascii
from devices import *

def to_bytes(n, length, byteorder='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if byteorder == 'big' else s[::-1]

class gsioc:
    def __init__(self,serial=None):
        self.serial = serial

    def createSerial(self,port=0,timeout=0.1):
        self.port = port
        self.timeout = timeout
        # Initiate serial connection
        s = serial.Serial(port)
        #s = serial.serial_for_url("loop://")  # loop for testing
        s.baudrate = 9600
        s.bytesize = 8
        s.parity = serial.PARITY_NONE
        s.stopbits = 1
        s.timeout = timeout
        self.serial = s
        try :
            s.open()
            print "opened"
            print(s)
        except :
            print(s)

    def closeSerial(self):
        self.serial.close()

    def connect(self,ID=0):
        if( int(ID) not in range(64) ):
            raise Exception("ID out of range [0,63]")
        ID += 128
        s = self.serial
        s.flushInput()
        #s.write(bytes.fromhex('ff'))
        s.write('xff')
        time.sleep(self.timeout)   # Passively wait for all devices to disconnect
        s.write(to_bytes(ID,1,byteorder='big'))
        resp = s.read(1)    # Will raise serialTimoutException after timeout
        print(str(datetime.datetime.now()) + " -- Connected to device ", ID-128)

    # returns byte array
    # Use str(resp,'ascii') or resp.decode('ascii') to get ascii string
    def iCommand(self,commandstring):
        command = binascii.a2b_qp(commandstring)
        #if(command[0] not in range(0,255)):     # Change this to correct range
        #    raise Exception("Command out of range")
        s = self.serial
        s.flushInput()
        s.write(command[0:1])
        resp = bytearray(0)
        while(True):
            resp.append(s.read(1)[0])
            if(resp[len(resp)-1] > 127):
                resp[len(resp)-1] -= 128
                print(str(datetime.datetime.now()) + " -- Immediate response complete")
                break
            else:
                s.write('\x06')
        return resp.decode("ascii")

    def bCommand(self,commandstring):
        data = binascii.a2b_qp("\n" + commandstring + "\r")
        s = self.serial
        s.flushInput()
        resp = bytearray(0)

        # begin buffered command by sending \n until the device echos \n or times out
        firstErrorPrinted = False # This is used to prevent repetitive printing
        # begin loop
        while(True):
            s.write(data[0:1])    # send line feed
            readySig = s.read(1)[0]
            if(readySig == 10):
                print(str(datetime.datetime.now()) + " -- Starting Buffered command")
                break
            elif(readySig == 35):
                if(not firstErrorPrinted):
                    print("Device busy. Waiting...")
                    firstErrorPrinted = True
            else:
                raise Exception("Did not recieve \\n (0x0A) or # as response")
        resp.append(readySig)

        # Send buffered data
        for i in range(1,len(data)):
            s.write(data[i:i+1])
            resp.append(s.read(1)[0])
            if( resp[i] != data[i] ):
                raise Exception("Recieved " + str(resp,'ascii') + " instead of " + str(data[i:i+1]))
            if( resp[i] == 13 ):
                print(str(datetime.datetime.now()) + " -- Buffered command complete")
                return resp

        # This will happen if sending the data failed
        print(str(datetime.datetime.now()) + " -- Buffered command FAILED")
        resp_no_whitespace = resp[1:len(resp)-2]
        return resp_no_whitespace.decode("ascii")


if __name__ == '__main__':
    '''
    g = gsioc()
    g.createSerial(port='COM4', timeout=0.1)
    g.connect(ID=30)
    #g.serial.write('%')
    print g.iCommand('%')
    #print g.serial.read(6)
    #g.bCommand("Text to display")
    g.closeSerial()
    '''

    s=SerialDevice('COM4')
    s.port.timeout=1
    s.port.open()
    s.port.write('xff')
    s.port.write(to_bytes(30+128, 1, byteorder='big'))
    s.port.flushInput()
    s.port.write(binascii.a2b_qp('?')) # ?\r ?
    x=s.port.read()
    print x,len(x)
    s.port.close()
