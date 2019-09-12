from PyQt5.QtWidgets import (QWidget, QGridLayout, QApplication)
from PyQt5.QtGui import QIcon
import sys, glob
from img.load_img import img
from widget_serial_port import WidgetSerialPort


class OneWireGui:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

    def run(self):
        sys.exit(self.app.exec_())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Members
        self.baudrate = 400000

        # Widgets
        self.w_serial_port = WidgetSerialPort(self, self.openConnection,
                                              self.closeConnection,
                                              self.enableGUI,
                                              self.listSerialPorts)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self.w_serial_port, 0, 0)
        self.setLayout(grid)

        self.setWindowTitle('One-wire device controller')
        self.setWindowIcon(QIcon(img('intech.ico')))
        # self.resize(100, 100)
        self.show()

    def openConnection(self, port):
        # self.com.connect(port, self.baudrate)
        # return True on connection success, False otherwise
        return False

    def closeConnection(self):
        # self.com.disconnect()
        pass

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        #todo update baudrate (open close stream)

    def enableGUI(self, e):
        pass

    def listSerialPorts(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            p = port.split()[0]
            if self.openConnection(p):
                self.closeConnection()
                result.append(p)
        return sorted(result)

    def closeEvent(self, event):
        self.closeConnection()
        super().closeEvent(event)


def except_hook(t, value, traceback):
    sys.__excepthook__(t, value, traceback)


if __name__ == "__main__":
    sys.excepthook = except_hook
    g = OneWireGui()
    g.run()
