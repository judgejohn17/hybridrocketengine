import serial
import serial.tools.list_ports as lp

import time
import datetime

import random

millis = lambda: int(round(time.time() * 1000))

valve_order = "ODPFI"

class communications:
    class fake_serial2:
        def __init__(self):
            self.initialized = True
            self.fields = ["N2OTemp", "N2Temp"]
        def initialize(self):
            True
        def close(self):
            True
        def command(self, comm):
            True
        def check_read(self):
            return True
        def read(self):
            return ",".join([
                str(millis()),
                "N2OTemp", str(random.random()),
                "N2Temp", str(random.random())])


    class fake_serial:
        def __init__(self):
            self.initialized = True
            self.fields = ["N2Pressure", "N2OPressure", "InjectorPressure"]
            self.valves = ["0","0","0","0","0"]

        def initialize(self):
            True
        def close(self):
            True

        def read(self):
            return ",".join([
                str(millis()),
                "N2Pressure", str(random.random()),
                "N2OPressure", str(random.random()),
                "InjectorPressure", str(random.random()),
                "ValveStat", "".join(self.valves)])

        def check_read(self):
            return True

        def command(self, comm):
            i = valve_order.find(comm.upper())
            self.valves[i] = str(int(comm == comm.lower()))

    class serial_device:
        def __init__(self, device):
            self.device = device
            self.initialized = 0
            self.fields = []
            self.offset = 0
            self.data = ""

        def read(self):
            return self.data

        def check_read(self):
            if self.device.inWaiting() > 2:
                value = self.device.readline().decode()
                self.data = value.strip('\r\n')
                return True
            return False

        def command(self, comm):
            self.device.write(comm.encode())

        def initialize(self):
            print("Initializing Serial Device")
            initial_reads = 10

            while initial_reads > 0:
                if self.check_read():
                    initial_reads = initial_reads - 1
            readline = None
            
            while not readline:
                readline = self.read()

            readline = readline

            tokens = readline.split(",")
            self.fields = tokens[1::2]
            print("Found Parameters:")
            print(self.fields)
            self.initialized = 0
            self.offset = millis() - int(tokens[0])

        def close(self):
            self.device.close()


    def __init__(self):
        self.devices = []
        self.ready = False
        self.values = []
        self.new_values = False

        for p in lp.comports():
            desc = p.description
            if any([y in desc for y in ["Arduino","USB Serial", "USB UART"]]):
#            if ('Arduino' in desc or 'USB Serial' in desc):
                try:
                    print("Connecting to: ",p.device," - ",desc)
                    new_ser = serial.Serial(p.device, 9600)
                    the_device = self.serial_device(new_ser)
                    self.devices.append(the_device)
                    the_device.initialize()
                except:
                    print("Could not connect to: ",p.device," - ",desc)

        if not self.devices:
            self.devices.append(self.fake_serial())
            self.devices.append(self.fake_serial2())

    def command(self, comm):
        for dev in self.devices:
            dev.command(comm)

    def get_data(self):
        if not self.new_values:
            return None
        time = millis()
        values = []
        self.new_values = False
        for dev in self.devices:
            try:
                output = dev.read()
                if (output):
                    tokens = output.split(",")
                    tokens = tokens[1:]
                    while tokens:
                        values.append((tokens.pop(0),float(tokens.pop(0))))
            except Exception as e:
                print(e)
        
        if values:
            return [time, *values]
        return None

    def check_data(self):
        print("Checking")
        for dev in self.devices:
            try:
                output = dev.check_read()
                if (output):
                    self.new_values = True
            except Exception as e:
                print(e)

    def get_parameters(self):
        fields = []
        for dev in self.devices:
            fields = fields + dev.fields
        return fields

    def __del__(self):
        for dev in self.devices:
            dev.close()
