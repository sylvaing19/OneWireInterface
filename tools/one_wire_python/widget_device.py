from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QLabel, QFrame,
                             QComboBox, QVBoxLayout)
from input_field import InputField
from one_wire_def import (OW_BAUDRATE, OW_RETURN_LEVEL, OW_COM_STATUS,
                          OW_DEVICE_STATUS)


class WidgetDevice(QWidget):
    def __init__(self, master, cbPing, cbSoftReset, cbFactoryReset,
                 cbBaudrateUpdate=None):
        super().__init__(master)
        # Members

        # Callbacks
        self.cb_baudrate_update = cbBaudrateUpdate

        # Widgets
        frame = QFrame(self)
        frame.setFrameStyle(QFrame.StyledPanel)
        self.label_status = QLabel(self)
        self.label_status.setAlignment(Qt.AlignCenter)
        l_model = QLabel("Model", self)
        self.model_nb = QLabel(self)
        self.model_nb.setAlignment(Qt.AlignRight)
        l_firmware = QLabel("Firmware", self)
        self.firmware_v = QLabel(self)
        self.firmware_v.setAlignment(Qt.AlignRight)
        l_id = QLabel("ID", self)
        self.field_id = InputField(self, 0x00, 0xFD)
        l_baudrate = QLabel("Baudrate", self)
        self.field_baudrate = QComboBox(self)
        self.field_baudrate.addItems([e.name for e in OW_BAUDRATE])
        self.field_baudrate.currentIndexChanged.connect(self._baudrate_changed)
        l_return_level = QLabel("Return level", self)
        self.field_return_level = QComboBox(self)
        self.field_return_level.addItems([e.name for e in OW_RETURN_LEVEL])
        b_ping = QPushButton("Ping", self)
        b_ping.clicked.connect(cbPing)
        b_soft_reset = QPushButton("Soft reset", self)
        b_soft_reset.clicked.connect(cbSoftReset)
        b_factory_reset = QPushButton("Factory reset", self)
        b_factory_reset.clicked.connect(cbFactoryReset)
        self.ow_status = WidgetStatusDisplay(self, OW_COM_STATUS)
        self.device_status = WidgetStatusDisplay(self, OW_DEVICE_STATUS)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self.label_status, 0, 0, 1, 2)
        grid.addWidget(l_model, 1, 0)
        grid.addWidget(self.model_nb, 1, 1)
        grid.addWidget(l_firmware, 2, 0)
        grid.addWidget(self.firmware_v, 2, 1)
        grid.addWidget(l_id, 3, 0)
        grid.addWidget(self.field_id, 3, 1)
        grid.addWidget(l_baudrate, 4, 0)
        grid.addWidget(self.field_baudrate, 4, 1)
        grid.addWidget(l_return_level, 5, 0)
        grid.addWidget(self.field_return_level, 5, 1)
        grid.addWidget(b_ping, 6, 0, 1, 2)
        grid.addWidget(b_soft_reset, 7, 0, 1, 2)
        grid.addWidget(b_factory_reset, 8, 0, 1, 2)
        grid.addWidget(self.ow_status, 9, 0, 1, 2)
        grid.addWidget(self.device_status, 10, 0, 1, 2)
        grid.setColumnStretch(1, 1)
        frame.setLayout(grid)
        m_grid = QGridLayout()
        m_grid.addWidget(frame)
        m_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(m_grid)

        # Init
        self.set_device(1, 400000, 2)

    def set_device(self, aId, aBaudrate, aSRL, aStatus=0, aModelNb=None,
                   aFirmwareV=None):
        try:
            self.label_status.setText("Device")
            self.field_id.set_value(aId)
            self.set_baudrate(aBaudrate)
            self.set_return_level(aSRL)
            self.ow_status.set_status(aStatus)
            self.set_model_nb(aModelNb)
            self.set_firmware_version(aFirmwareV)
        except (ValueError, IndexError):
            self.set_device(1, 400000, 2)

    def get_id(self):
        return self.field_id.get_value()

    def get_baudrate(self):
        return OW_BAUDRATE[self.field_baudrate.currentIndex()].hl_value

    def set_baudrate(self, baudrate):
        for i in range(self.field_baudrate.count()):
            if OW_BAUDRATE[i].hl_value == baudrate:
                self.field_baudrate.setCurrentIndex(i)
                return
        raise ValueError

    def get_return_level(self):
        return OW_RETURN_LEVEL[self.field_return_level.currentIndex()].hl_value

    def set_return_level(self, return_level):
        for i in range(self.field_return_level.count()):
            if OW_RETURN_LEVEL[i].hl_value == return_level:
                self.field_return_level.setCurrentIndex(i)
                return
        raise ValueError

    def set_ow_status(self, status):
        if status == 0:
            self.label_status.setText("Connected device")
        else:
            self.label_status.setText("Unreachable device")
        self.ow_status.set_status(status)

    def set_device_status(self, status):
        self.device_status.set_status(status)

    def set_model_nb(self, model_nb):
        if model_nb is None:
            self.model_nb.setText("unknown")
        else:
            self.model_nb.setText(str(model_nb))

    def set_firmware_version(self, firmware_v):
        if firmware_v is None:
            self.firmware_v.setText("unknown")
        else:
            self.firmware_v.setText(str(firmware_v))

    def _baudrate_changed(self, _):
        if self.cb_baudrate_update is not None:
            self.cb_baudrate_update(self.get_baudrate())


class WidgetStatusDisplay(QWidget):
    def __init__(self, master, field_list):
        super().__init__(master)
        self.entries = []
        grid = QVBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        for entry in field_list:
            if len(entry) > 0:
                w = WidgetStatusDisplayEntry(self, entry)
                grid.addWidget(w)
                self.entries.append(w)
            else:
                self.entries.append(None)
        self.setLayout(grid)

    def set_status(self, status):
        mask = 1
        for entry in self.entries:
            if entry is not None:
                if status & mask:
                    entry.mark_wrong()
                else:
                    entry.mark_ok()
                mask *= 2


class WidgetStatusDisplayEntry(QFrame):
    def __init__(self, master, text):
        super().__init__(master)
        label = QLabel(text, self)
        label.setAlignment(Qt.AlignCenter)
        grid = QGridLayout()
        grid.addWidget(label)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)
        # self.setFrameStyle(QFrame.StyledPanel)
        self.mark_ok()

    def mark_ok(self):
        self.setStyleSheet(
            """ QFrame { border: 1px solid rgb(201, 201, 201); }""")

    def mark_wrong(self):
        self.setStyleSheet(
            """ QFrame {
            border: 1px solid rgb(155, 5, 5);
            background-color: rgb(249, 83, 83); }""")
