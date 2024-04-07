import os
import time
import ipaddress
import wifi
import socketpool
import busio
import board
import microcontroller
from DS18x20.uDS18x20m import *

sensorTypes = []

thermo = uDS18X20(board.GP5)
sensorTypes.append(thermo)
T = thermo.readAll()
print(f"Temperature = {T}")

dt = 10
t = 0

while True:
    T = thermo.readAll()
    print(t, T[0])
    t += dt
    time.sleep(dt)