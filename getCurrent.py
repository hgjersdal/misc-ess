#!/usr/bin/env python3

# written by grey@christoforo.net
# on 8 Nov 2017

# prints current from keithley 24xx connected via serial

import serial
import argparse

port = '/dev/ttyUSB0'
baud = 9600
timeout = 3 # seconds

expectedDeviceString = b'KEITHLEY INSTRUMENTS INC.,MODEL 2410,4090615,C33   Mar 31 2015 09:32:39/A02  /J/K\r\n'

# for cmd line arguments
parser = argparse.ArgumentParser(description='Reads current from keithley 24xx sourcemeter.')
parser.add_argument('-c','--continuous', dest='continuous', action='store_true', default=False, help="Operate continuously (forever)")
args = parser.parse_args()

k = serial.Serial(port,baud,timeout=timeout)

k.write(b'*RST\n')
k.write(b'*IDN?\n')
deviceString = k.readline()

if deviceString == expectedDeviceString:
  pass
  #print('Conected to', deviceString.decode("utf-8"))
else:
  print('ERROR: Got unexpected device string:', deviceString.decode("utf-8"))
  exit()


cmds = []

cmds.append(':SOUR:FUNC VOLT')
cmds.append(':SOUR:VOLT:MODE FIXED')
cmds.append(':SENS:FUNC "CURR"')
cmds.append(':SENS:CURR:NPLC 10')
cmds.append(':SOUR:VOLT:RANG MIN')
cmds.append(':SOUR:VOLT:LEV 0')
cmds.append(':FORM:ELEM CURR')
cmds.append(':OUTP ON')

for cmd in cmds:
  #print('Sending', cmd)
  cmd = cmd.encode('utf-8') + b'\n'
  k.write(cmd)
  #k.write(b':SYST:ERR?\n')
  #err = k.readline()
  #print(err)

while True:
  cmd = ':READ?'
  k.write(cmd.encode('utf-8') + b'\n')
  current = float(k.readline().decode('utf-8'))

  print(current)

  if not args.continuous:
      break

cmd = ':OUTP OFF'
k.write(cmd.encode('utf-8') + b'\n')
#k.write(b':SYST:ERR?\n'); k.readline()

k.close()
