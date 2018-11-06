import communicator
import netcommunicator

import pickle
import socket

from PyQt4.QtCore import QThread, SIGNAL

import time
import datetime

import os.path

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

millis = lambda: int(round(time.time() * 1000))

class middleware(QThread):
    def __init__(self, networked=False):
        QThread.__init__(self)
        if networked:
            self.coms = netcommunicator.communications()
        else:
            self.coms = communicator.communications() 

        TODAY = datetime.date.today() 

        FILENUMBER = 1
        self.FILENAME = '../Log/'+str(TODAY)+'-'+str(FILENUMBER)+'.log'
        while os.path.isfile(self.FILENAME):
            FILENUMBER = FILENUMBER + 1
            self.FILENAME = '../Log/'+str(TODAY)+'-'+str(FILENUMBER)+'.log'

        print(self.FILENAME)

    def command(self, comm):
        self.coms.command(comm)

    def writeData(self, value):
        # Open log file 2012-6-23.log and append
        with open(self.FILENAME, 'a') as f: 
            
            f.write(value) 
            # Write our integer value to our log
            
            f.write('\n') 
            # Add a newline so we can retrieve the data easily later

    def run(self):
        while True:
            print("Running")
            time = millis()
            
            values = self.coms.get_data()

            if values:
                self.writeData(",".join(map(str,values)))
                time = values.pop(0)
                self.emit(SIGNAL('plot_point(int, PyQt_PyObject)'), time, values)
                self.msleep(20)
            else:
                self.msleep(40)


    def get_parameters(self):
        return self.coms.get_parameters()

    def __del__(self):
        del self.coms
        self.wait()
