# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

#  function to convert celcius to fahrenheit
def c_to_f(temp):
    temp_f = (temp * 9/5) + 32
    return temp_f

# thermometer class
class uDS18X20:
    def __init__(self, dataPin = board.GP5, units="°C", type="thermometer"):
        # keep track of units
        self.units = units
        self.type = type

        # one-wire bus for DS18B20
        self.ow_bus = OneWireBus(dataPin)

        # scan for temp sensor
        self.scan = self.ow_bus.scan()
        self.sensors = []
        for sensor in self.scan:
            self.sensors.append(DS18X20(self.ow_bus, sensor))
        print("Sensors:", self.sensors)


    def read(self):

        T = self.sensors[0].temperature
        return T
        
    def readAll(self):
        T = []
        for sensor in self.sensors:
            T.append(sensor.temperature)
        return T
    
    def writeLine(self, t, fname):
        with open(fname, "a") as logFile:
            txt = f'{t}'
            for T in self.readAll():
                txt += f',{T}'
            print(txt)
            logFile.write(txt+"\n")


    def log_to_file(self, fname="log.csv", dt=5):
        startTime = time.monotonic() 
        mesTime = startTime
        print(f"startTime: {startTime}")
        print(mesTime + dt)
        
        self.writeLine(0, fname)
            

        while True:
            try:
                currentTime = time.monotonic()
                if (mesTime + dt) <= currentTime:
                    mesTime = currentTime
                    runTime = mesTime - startTime
                    self.writeLine(runTime, fname)
                    
            except Exception as E:
                print(E)
                continue






