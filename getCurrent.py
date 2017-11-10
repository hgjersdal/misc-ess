#!/usr/bin/env python3

# written by grey@christoforo.net
# on 8 Nov 2017
# adapted by hgjersdal 10 nov 2017
# prints current from keithley 24xx connected via serial

import serial
import argparse
import signal
import sys
import time
import inspect
import numpy

port = '/dev/ttyUSB1'
baud = 9600
timeout = 3 # seconds

expectedDeviceString = b'KEITHLEY INSTRUMENTS INC.,MODEL 2410,4090615,C33   Mar 31 2015 09:32:39/A02  /J/K\r\n'

cmds = []

cmds.append(':SOUR:FUNC VOLT')
cmds.append(':SOUR:VOLT:MODE FIXED')
cmds.append(':SENS:FUNC "CURR"')
cmds.append(':SENS:CURR:NPLC 10')
cmds.append(':SOUR:VOLT:RANG MIN')
cmds.append(':SOUR:VOLT:LEV 0')
cmds.append(':FORM:ELEM CURR')
cmds.append(':OUTP ON')

def printError(k):
  k.write(b':SYST:ERR?\n')
  err = k.readline()
  print(err)

def initialize():
  k = serial.Serial(port,baud,timeout=timeout)

  k.write(b'*RST\n')
  k.write(b'*IDN?\n')
  deviceString = k.readline()

  if deviceString == expectedDeviceString:
    pass
  else:
    print('ERROR: Got unexpected device string:', deviceString.decode("utf-8"))
    raise Exception('Unexpected device string when trying to connect to ' + port)

  for cmd in cmds:
    #print('Sending', cmd)
    cmd = cmd.encode('utf-8') + b'\n'
    k.write(cmd)

  return(k)

def cleanup(k):
  cmd = ':OUTP OFF'
  k.write(cmd.encode('utf-8') + b'\n')
  k.close()

def signal_handler(signal, frame):
  #print('You pressed Ctrl+C!')
  #print (frame.f_locals)
  k = frame.f_locals['self']
  junk = k.readline()
  cleanup(k)
  sys.exit(0) 

def getNValues(nValues):
  k = initialize()
  measurements = []
  for i in range(nValues):
    measurements.append( getCurrent(k) )
  cleanup(k)
  return( numpy.array(measurements) )
  
def getCurrent(k):
  cmd = ':READ?'
  k.write(cmd.encode('utf-8') + b'\n')
  current = float(k.readline().decode('utf-8'))
  return(current)

def getCurrent():
  k = initialize()
  cmd = ':READ?'
  k.write(cmd.encode('utf-8') + b'\n')
  current = float(k.readline().decode('utf-8'))
  cleanup(k)
  return(current)
  
if __name__ == '__main__':
  # for cmd line arguments
  parser = argparse.ArgumentParser(description='Reads current from keithley 24xx sourcemeter.')
  parser.add_argument('-c','--continuous', dest='continuous', action='store_true', default=False, help="Operate continuously (forever)")
  args = parser.parse_args()

  k = initialize()
  
  # register handler for ctrl+c cleanup
  signal.signal(signal.SIGINT, signal_handler) 

  if args.continuous:
    print('Running continuously forever. Use Ctrl+c to terminate')

  # delay aftetr output on
  time.sleep(0.5)

  while True:
    current = getCurrent(k)
    print(current)

    if not args.continuous:
      break

  cleanup(k)

  sys.exit(0)
