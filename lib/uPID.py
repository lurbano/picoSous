import time
import json

class uPID:
    def __init__(self, setT=57.0, dt=10.0, Kp=1.0, Ki=0, Kd=100):
        self.state = {}
        self.state["setT"] = setT
        self.state["Kp"] = Kp
        self.state["Ki"] = Ki
        self.state["Kd"] = Kd 

        self.state["dt"] = dt
        self.state["startTime"] = -1
        self.state["T_data"] = []
        # number of current data points to keep
        self.state["nCurrent"] = 30 
        self.state["T_long"] = []
        # timestep for long term records (continue recording indefinitely)
        self.state["longDt"] = self.state['nCurrent'] * self.state['dt'] 
        #self.state["status"] = "None"
        self.state["runtime"] = 0.
        
        self.l_run = False
        self.initialized = False

        self.clock = 0
        self.longClock = 0
        
        self.err = 0
        self.prp = 0
        self.int = 0
        self.dif = 0
        self.ctrl = 0
        self.dTdt = 0
        self.storeParams()

        self.stateFileName = "state.json"


    def getError(self,T):
        return self.state["setT"] - T

    def check(self, T):
        if (not self.initialized): # initialize 
            self.state["T_data"].append([0,T])
            self.state["T_long"].append([0,T])
            self.state["startTime"] = time.monotonic()
            self.initialized = True

        else: 
            self.state['runtime'] = round(time.monotonic() - self.state["startTime"], 1)
            self.state["T_data"].append((self.state['runtime'], T))
            if len(self.state["T_data"]) > self.state["nCurrent"]:
                oldT = self.state["T_data"].pop(0)
                if (self.longClock + self.state["longDt"]) < time.monotonic():
                    self.state['T_long'].append(oldT)
                    print("record long:")
                    self.longClock = time.monotonic()

            print("calculating pid")
            #error
            self.err = self.getError(T) 
            #proportional
            self.prp = self.state['Kp'] * self.err
            #integral
            self.int += self.state['Ki'] * self.err
            #differential
            self.dTdt = (self.state['T_data'][-1][1] - self.state['T_data'][-2][1])/self.state['dt']
            self.dif = self.state['Kd'] * self.dTdt 

            self.ctrl = self.prp + self.int + self.dif

            self.storeParams()
            print(f'T={T} | e={self.err} | P={self.prp} | I={self.int} | dT/dt={self.dTdt} | D={self.dif} | C={self.ctrl}')
            
        return self.ctrl

    def saveState(self):
        with open(self.stateFileName, "w") as f:
            f.write(json.dumps(self.state))

    def loadState(self):
        try:
            with open(self.stateFileName, "r") as f:
                self.state = json.loads(f.read())
        except Exception as e:
            print(f'Error loading state file ({self.stateFileName}): {e}')

    def start(self):
        self.l_run = True

    def restart(self):
        self.loadState()
        self.l_run = True
        self.initialized = True

    def stop(self):
        self.l_run = False

    def storeParams(self):
        p = {}
        p["Error"] = self.err
        p["Prop"] = self.prp
        p["Int"] = self.int 
        p["dTdt"] = self.dTdt
        p["Dif"] = self.dif
        p["Control"] = self.ctrl
        self.params = p






