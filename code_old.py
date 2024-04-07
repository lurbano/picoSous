

import os
import time
import ipaddress
import wifi
import socketpool
import busio
import board
import microcontroller

import traceback
import json
# from uLogger import uLogger


from digitalio import DigitalInOut, Direction
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType
#from adafruit_onewire.bus import OneWireBus
#from adafruit_ds18x20 import DS18X20

from DS18x20.uDS18x20m import *

# Parameters
sensorID = "beesWax"
wifiName = "TFS Students"
wifiPass = "Fultoneagles"

# DS18x20 Wiring:
#   Red: 3.3 V (3V0)
#   Black: Ground
#   Yellow: Data: GP5 (default)

thermo = uDS18X20(board.GP5)
T = thermo.readAll()
print(f"Temperature = {T}")

#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False


#  connect to network
print()
print("Connecting to WiFi")


#  set static IP address
# ipv4 =  ipaddress.IPv4Address("192.168.1.42")
# netmask =  ipaddress.IPv4Address("255.255.255.0")
# gateway =  ipaddress.IPv4Address("192.168.1.1")
# wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
#  connect to your SSID
#wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
wifi.radio.connect(wifiName, wifiPass)

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

# load web page
def getWebpage():
    with open("logToPage.html", "r") as f:
        html = f.read()
    return html

#  route default static IP
@server.route("/")
def base(request: HTTPRequest):  # pylint: disable=unused-argument
    #  serve the HTML 
    #  with content type text/html
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:

        response.send(getWebpage())
        

#@server.route("/", method=HTTPMethod.GET)
#def getResponse(request: HTTPRequest):
#    raw_text = request.raw_request.decode("utf8")
#    print(raw_text)

def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/led", method=HTTPMethod.POST)
def ledButton(request: HTTPRequest):
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']}")
    rData = {}
    
    if (data['action'] == 'ON'):
        led.value = True
        
    if (data['action'] == 'OFF'):
        led.value = False
    
    rData['item'] = "led"
    rData['status'] = led.value
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/T", method=HTTPMethod.POST)
def getTemperature(request: HTTPRequest):
    T = thermo.readAll()
    print(f"Temperature = {T}")
    rData = {}
    rData["id"] = sensorID
    rData['value'] = T
    rData['units'] = '°C'
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/getT", method=HTTPMethod.POST)
def getTemperatureRecords(request: HTTPRequest):
    data = requestToArray(request)
    print(f"data: {data}")
    rData = {}
    if (data['timeFrame'] == "current"):
        rData["item"] = "currentT"
        rData['value'] = pid.state['T_data']
    elif (data['timeFrame'] == 'long'):
        rData["item"] = "longT"
        rData['value'] = pid.state['T_long']
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/getChartData", method=HTTPMethod.POST)
def getTemperatureRecords(request: HTTPRequest):
    data = requestToArray(request)
    print(f"data /getChartData: {data}")
    rData = {}
    rData['state'] = pid.state
    rData['params'] = pid.params
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/startCtrl", method=HTTPMethod.POST)
def startController(request: HTTPRequest):
    data = requestToArray(request)
    print(f"data: {data}")
    rData = {}
    if (data['action'] == "start"):
        # set state from webpage
        print('data["state"]', data['state'])
        pid.state.update(data['state'])
        pid.start()
        rData["status"] = "started"
    elif (data['action'] == "restart"):
        pid.restart()
        rData["status"] = "started"
    elif (data['action'] == "stop"):
        pid.stop()
        relay.value = False
        rData["status"] = "stopped"
    else:
        rData["status"] = f"Recieved: {data['action']}"
    rData["state"] = pid.state
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))
        

@server.route("/relay", method=HTTPMethod.POST)
def relaySwitch(request: HTTPRequest):
    if relay.value:
        relay.value = False
    else:
        relay.value = True
    print(f'Relay: {relay.value}')
    rData = {}
    rData["item"] = "relay"
    rData['value'] = relay.value
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))
    
#  if a button is pressed on the site
@server.route("/", method=HTTPMethod.POST)
def buttonpress(request: HTTPRequest):
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)
    #  if the led on button was pressed
    if "ON" in raw_text:
        #  turn on the onboard LED
        led.value = True
    #  if the led off button was pressed
    if "OFF" in raw_text:
        #  turn the onboard LED off
        led.value = False
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")

print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")


#uThermoController(thermo, relay, pid)

print("starting 30sec loop")
print()

clock = time.monotonic() #  time.monotonic() holder for server ping
while True:
    try:
        #  every 30 seconds, ping server & update temp reading
        if (clock + 30) < time.monotonic():
            if wifi.radio.ping(ping_address) is None:
                print("lost connection")
            else:
                print("connected")
            clock = time.monotonic()
            #  comment/uncomment for desired units
        server.poll()
        
    # pylint: disable=broad-except
    except Exception as e:
        print(f'server error: {e}')
        continue
    

    


