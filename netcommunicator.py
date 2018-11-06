import pickle
import socket

from PyQt4.QtCore import QMutex

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

class communications:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((TCP_IP, TCP_PORT))
        self.running = QMutex()
        self.send_command = '.'

    def command(self, comm):
        self.running.lock()
        self.send_command = comm
        self.running.unlock()

    def get_data(self):
        self.running.lock()
        self.s.send(self.send_command.encode())
        values = pickle.loads(self.s.recv(BUFFER_SIZE))
        self.send_command = '.'
        self.running.unlock()

        return values

    def get_parameters(self):
        self.running.lock()
        self.s.send(b"?")
        params = pickle.loads(self.s.recv(BUFFER_SIZE))
        self.running.unlock()
        return params

    def __del__(self):
        self.s.close()
