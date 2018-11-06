import qthreader

import sys

from PyQt4 import QtGui
from PyQt4.QtCore import QThread, SIGNAL, Qt

import pyqtgraph as pg

key_dict = {
            Qt.Key_Q : "o",
            Qt.Key_Z : "O",
            Qt.Key_E : "i",
            Qt.Key_C : "I",
            Qt.Key_T : "p",
            Qt.Key_B : "P",
            Qt.Key_U : "f",
            Qt.Key_M : "F",
            Qt.Key_O : "d",
            Qt.Key_Period : "D",}

DATA_COUNT = 5

class plotter(QtGui.QDialog):
    class figureholder:
        def __init__(self, title):
            self.canvas = pg.PlotWidget()
            self.canvas.setTitle(title)
            self.canvas.setMinimumWidth(500)

            self.ax = self.canvas.plot(pen = 'y')
            self.xdata = []
            self.ydata = []

            self.title = QtGui.QLabel(title)
            self.title.setFont(QtGui.QFont("Arial", 20))

            self.label = QtGui.QLabel(title)
            self.label.setFont(QtGui.QFont("Arial", 24))

            self.avg_vals = []

        def plot_point(self, time, newvalue):
            self.avg_vals.append(newvalue)
            if len(self.avg_vals) == DATA_COUNT:
                value = sum(self.avg_vals) / DATA_COUNT
                self.avg_vals = []
            else:
                return
            self.xdata.append(time)
            self.ydata.append(value)

            if len(self.xdata) > 10:
                self.xdata.pop(0)
                self.ydata.pop(0)
            self.ax.setData(self.xdata, self.ydata)

            self.label.setText("{:.2f}".format(value))
            #self.canvas.draw()

    def __init__(self, arguments, parent=None):
        super(plotter, self).__init__(parent)

        # Initialize Communicator
        if "net" in arguments:
            self.coms = qthreader.middleware(networked=True)
        else:
            self.coms = qthreader.middleware(networked = False)

        params = sorted(self.coms.get_parameters())

        self.figures = {}

        for p in params:
            if not p == "ValveStat":
                self.figures[p] = self.figureholder(p)
        self.counter = 0

        self.keys_locked = True
        self.init_layout()

        self.connect(self.coms,
                    SIGNAL('plot_point(int, PyQt_PyObject)'),
                    self.plot_point)
        self.coms.start()

    def plot_point(self, time, params):
        print("Plotting")
        for (p, y) in list(params):
            if not p == "ValveStat":
                self.figures[p].plot_point(time, y)
            else:
                self.parse_valves(y)
        self.counter = (self.counter + 1) % DATA_COUNT

    def solenoid(self):
        self.coms.solenoid()
        print("Solenoid")

    def command(self, comm):
        if not self.keys_locked:
            self.coms.command(comm)
            print("Clicked", comm)

    def lf(self, comm):
        return lambda: self.command(comm)

    def toggle_locked(self):
        if self.keys_locked:
                text, ok = QtGui.QInputDialog.getText(self,
                                                      'Enable Input',
                                                      'Input "Launch"')
                if ok and text == "Launch":
                    self.keys_locked = False
                    self.lock_button.setText("LOCK BUTTONS")
        else:
            self.keys_locked = True
            self.lock_button.setText("UNLOCK")

    def parse_valves(self, valves):
        valves = str(int(valves))
        zeros = "0" * (len(self.button_labels) - len(valves))
        valves = zeros + valves
        for i in range(len(self.button_labels)):
            n = i
            if i == 1:
                n = 4
            elif i == 4:
                n = 1
            if valves[n] == "1":
                self.button_labels[i].setText("open")
            else:
                self.button_labels[i].setText("CLOSED")

    def init_layout(self):
        # set the layout
        parent_layout = QtGui.QVBoxLayout()
        button_layout = QtGui.QGridLayout()
        graph_layout = QtGui.QGridLayout()

        num_graphs = len(self.figures.values())
        smaller_dim = int(num_graphs ** 0.5)
        bigger_dim = (num_graphs + smaller_dim - 1) // smaller_dim
        graphx = 0
        graphy = 0

        for k in sorted(self.figures.keys()):
            fig = self.figures[k]
            figure_layout = QtGui.QVBoxLayout()
            labels_layout = QtGui.QHBoxLayout()
            figure_layout.addWidget(fig.canvas)
            labels_layout.addWidget(fig.title)
            labels_layout.addWidget(fig.label)
            figure_layout.addLayout(labels_layout)
            graph_layout.addLayout(figure_layout, graphx, graphy)
            graphx = graphx + 1
            if graphx >= smaller_dim:
                graphy = graphy + 1
                graphx = 0

        self.button_labels = []

        button_array = [("N2O", "O"),
                        ("N2ODrain", "I"),
                        ("N2", "P"),
                        ("N2Fill", "F"),
                        ("N2OBubb", "D")]

        for index, (button, comm) in enumerate(button_array):
            opener = QtGui.QPushButton("Open " + button)
            opener.clicked.connect(self.lf(comm.lower()))

            label = QtGui.QLabel("CLOSED")
            label.setFont(QtGui.QFont("Arial", 18))
            self.button_labels.append(label)

            closer = QtGui.QPushButton("Close " + button)
            closer.clicked.connect(self.lf(comm.upper()))

            button_layout.addWidget(opener, 0, index)
            button_layout.addWidget(label, 1, index)
            button_layout.addWidget(closer, 2, index)

        self.lock_button = QtGui.QPushButton("UNLOCK")
        self.lock_button.clicked.connect(self.toggle_locked)
        button_layout.addWidget(self.lock_button, 0, len(button_array), 3, 1)


        parent_layout.addLayout(graph_layout)
        parent_layout.addLayout(button_layout)
        self.setLayout(parent_layout)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            comm = key_dict.get(event.key(), None)
            if comm:
                self.command(comm)
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = plotter(sys.argv)
    main.show()

    sys.exit(app.exec_())
