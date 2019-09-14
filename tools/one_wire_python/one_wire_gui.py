from PyQt5.QtWidgets import (QWidget, QGridLayout, QApplication)
from PyQt5.QtGui import QIcon
import sys, glob
from img.load_img import img
from one_wire_python import (OneWireMasterInterface, OneWireException,
                             OneWireDataMissing, OneWireComError,
                             OneWireChecksumError, OneWireTimeout)
from widget_serial_port import WidgetSerialPort
from widget_device import WidgetDevice
from widget_register_display import WidgetRegisterDisplay


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
        self.ow_interface = OneWireMasterInterface()

        # Widgets
        self.w_device = WidgetDevice(self, self.ping, self.soft_reset,
                                     self.factory_reset, self.set_baudrate)
        self.w_register_display = WidgetRegisterDisplay(self, self.read, self.write)
        self.w_serial_port = WidgetSerialPort(self, self.openConnection,
                                              self.closeConnection,
                                              self.enableGUI,
                                              self.listSerialPorts)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self.w_serial_port, 0, 0)
        grid.addWidget(self.w_device, 1, 0)
        grid.addWidget(self.w_register_display, 0, 1, 3, 1)
        grid.setColumnStretch(2, 1)
        grid.setRowStretch(2, 1)
        self.setLayout(grid)

        self.setWindowTitle('One-wire device controller')
        self.setWindowIcon(QIcon(img('intech.ico')))
        self.show()

    def openConnection(self, port):
        try:
            self.ow_interface.open(port, self.w_device.get_baudrate())
            return True
        except IOError:
            return False

    def closeConnection(self):
        self.ow_interface.close()

    def connectionLost(self):
        self.w_serial_port.connection_lost()

    def set_baudrate(self, baudrate):
        try:
            self.ow_interface.setBaudrate(baudrate)
        except IOError:
            self.connectionLost()

    def enableGUI(self, e):
        self.w_device.setEnabled(e)
        self.w_register_display.setEnabled(e)

    def ping(self):
        try:
            self.w_device.set_ow_status(0)
            d_id = self.w_device.get_id()
            err = self.ow_interface.ping(d_id)
            try:
                err, srl = self.ow_interface.readU8(d_id, 6)
            except OneWireTimeout:
                srl = 0
            else:
                try:
                    err, model = self.ow_interface.readU16(d_id, 0)
                    self.w_device.set_model_nb(model)
                    err, firmware = self.ow_interface.readU8(d_id, 2)
                    self.w_device.set_firmware_version(firmware)
                except OneWireException:
                    pass
            self.w_device.set_return_level(srl)
            self.w_device.set_device_status(err)
        except IOError:
            self.connectionLost()
        except OneWireException as e:
            self.handle_ow_error(e)

    def soft_reset(self):
        try:
            err = self.ow_interface.softReset(self.w_device.get_id(),
                                        self.w_device.get_return_level() > 1)
            if err is not None:
                self.w_device.set_device_status(err)
            self.w_device.set_ow_status(0)
        except IOError:
            self.connectionLost()
        except OneWireException as e:
            self.handle_ow_error(e)

    def factory_reset(self):
        try:
            err = self.ow_interface.factoryReset(self.w_device.get_id(),
                                           self.w_device.get_return_level() > 1)
            if err is not None:
                self.w_device.set_device_status(err)
            self.w_device.set_ow_status(0)
        except IOError:
            self.connectionLost()
        except OneWireException as e:
            self.handle_ow_error(e)

    def read(self, address, size):
        if self.w_device.get_return_level() == 0:
            raise OneWireDataMissing
        try:
            d_id = self.w_device.get_id()
            if size == 1:
                err, val = self.ow_interface.readU8(d_id, address)
            elif size == 2:
                err, val = self.ow_interface.readU16(d_id, address)
            elif size == 4:
                err, val = self.ow_interface.readU32(d_id, address)
            else:
                raise RuntimeError("Read function not implemented for size=" +
                                   str(size))
        except IOError:
            self.w_device.set_ow_status(0)
            self.connectionLost()
            raise OneWireDataMissing
        except OneWireException as e:
            self.handle_ow_error(e)
            raise OneWireDataMissing
        self.w_device.set_device_status(err)
        self.w_device.set_ow_status(0)
        return val

    def write(self, address, size, value):
        try:
            d_id = self.w_device.get_id()
            e_answer = self.w_device.get_return_level() > 1
            if size == 1:
                err = self.ow_interface.writeU8(d_id, address, value, e_answer)
            elif size == 2:
                err = self.ow_interface.writeU16(d_id, address, value, e_answer)
            elif size == 4:
                err = self.ow_interface.writeU32(d_id, address, value, e_answer)
            else:
                raise RuntimeError("Write function not implemented for size=" +
                                   str(size))
        except IOError:
            self.w_device.set_ow_status(0)
            self.connectionLost()
            return False
        except OneWireException as e:
            self.handle_ow_error(e)
            return False
        self.w_device.set_ow_status(0)
        if err is not None:
            self.w_device.set_device_status(err)
            if err & 88:
                return False
        return True

    def handle_ow_error(self, e):
        if isinstance(e, OneWireTimeout):
            s = 1
        elif isinstance(e, OneWireDataMissing):
            s = 2
        elif isinstance(e, OneWireChecksumError):
            s = 16
        elif isinstance(e, OneWireComError):
            s = 128
        else:
            s = 255
        self.w_device.set_ow_status(s)

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
