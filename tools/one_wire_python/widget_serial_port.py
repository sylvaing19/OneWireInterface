from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QLabel, QFrame,
                             QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from img.load_img import img


class WidgetSerialPort(QWidget):
    def __init__(self, master, cbConnect, cbDisconnect, cbEnable, cbListPorts):
        super().__init__(master)
        # Members
        self.connected = False

        # Callbacks
        self.cb_connect = cbConnect
        self.cb_disconnect = cbDisconnect
        self.cb_enable_gui = cbEnable
        self.cb_list_ports = cbListPorts

        # Icons
        self.icon_connect = QIcon(img("connect.png"))
        self.icon_disconnect = QIcon(img("disconnect.png"))

        # Widgets
        frame = QFrame(self)
        frame.setFrameStyle(QFrame.StyledPanel)
        title = QLabel("Serial port", self)
        self.combo_box = ComboBox(self)
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().returnPressed.connect(self.connect_disconnect)
        self.combo_box.popupAboutToBeShown.connect(self.scan_ports)
        self.b_connect = QPushButton(self.icon_connect, "", self)
        self.b_connect.clicked.connect(self.connect_disconnect)

        # Layout
        grid = QGridLayout()
        grid.addWidget(title, 0, 0, 1, 2)
        grid.addWidget(self.combo_box, 1, 0)
        grid.addWidget(self.b_connect, 1, 1)
        grid.setColumnStretch(0, 1)
        frame.setLayout(grid)
        m_grid = QGridLayout()
        m_grid.addWidget(frame)
        m_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(m_grid)

        # Init
        self.scan_ports()

    def connection_lost(self):
        if self.connected:
            self.cb_enable_gui(False)
            self.display_failure()
            self.combo_box.setEnabled(True)
            self.b_connect.setIcon(self.icon_connect)
            self.connected = False

    def connect_disconnect(self):
        if self.connected:
            self.cb_disconnect()
            self.cb_enable_gui(False)
            self.reset_display()
            self.combo_box.setEnabled(True)
            self.b_connect.setIcon(self.icon_connect)
            self.connected = False
        elif self.cb_connect(self.get_current_port()):
            self.cb_enable_gui(True)
            self.display_success()
            self.combo_box.setEnabled(False)
            self.b_connect.setIcon(self.icon_disconnect)
            self.connected = True
        else:
            self.display_failure()
            self.scan_ports()

    def scan_ports(self):
        for i in range(self.combo_box.count()):
            self.combo_box.removeItem(i)
        self.combo_box.addItems(self.cb_list_ports())

    def get_current_port(self):
        strList = self.combo_box.currentText().split()
        if len(strList) > 0:
            return strList[0]
        else:
            return ""

    def reset_display(self):
        self.combo_box.setStyleSheet("")

    def display_success(self):
        self.combo_box.setStyleSheet(
            """QComboBox { background-color: rgb(203, 230, 163) }""")

    def display_failure(self):
        self.combo_box.setStyleSheet(
            """QComboBox { background-color: rgb(249, 83, 83) }""")


class ComboBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()
