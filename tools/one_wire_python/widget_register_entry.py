from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QLabel, QFrame,
                             QComboBox, QHBoxLayout)
from input_field import InputField


class WidgetRegisterEntry(QWidget):
    def __init__(self, master, address, min_val, max_val, name, cb_read,
                 docstring="", cb_write=None):
        super().__init__(master)
        # Callbacks
        self.cb_read = cb_read
        self.cb_write = cb_write

        # Widgets
        l_addr = QLabel(str(address), self)
        l_name = QLabel(name, self)
        self.field = InputField(self, min_val, max_val)
        self.field.set_callback_value_changed(self.update_gui_value)
        self.b_read = QPushButton("Read", self)
        self.b_read.clicked.connect(self.read)
        if self.cb_write is not None:
            self.b_write = QPushButton("Write", self)
            self.b_write.clicked.connect(self.write)
            self.field.set_callback_value_valid(self.b_write.setEnabled)
        else:
            self.b_write = None

        # Layout
        grid = QHBoxLayout()
        grid.addWidget(l_addr)
        grid.addWidget(l_name)
        grid.addWidget(self.field)
        grid.addWidget(self.b_read)
        if self.b_write is not None:
            grid.addWidget(self.b_write)
        self.setLayout(grid)

        # Members
        self.address = address
        self.device_value = None
        self.gui_value = self.field.get_value()

        # Init
        self.update_boldness()
        if len(docstring) > 0:
            self.setWhatsThis(docstring)

    def read(self):
        self.device_value = self.cb_read(self.address)
        self.field.set_value(self.device_value)
        self.update_gui_value(self.device_value)

    def write(self):
        if self.cb_write(self.address, self.gui_value):
            self.device_value = self.gui_value
            self.update_boldness()

    def update_gui_value(self, value):
        self.gui_value = value
        self.update_boldness()

    def update_boldness(self):
        if self.device_value is None:
            self.b_read.setStyleSheet(
                """QPushButton { font: bold }""")
            if self.b_write is not None:
                self.b_write.setStyleSheet("")
        else:
            self.b_read.setStyleSheet("")
            if self.b_write is not None:
                if self.device_value != self.gui_value:
                    self.b_write.setStyleSheet(
                        """QPushButton { font: bold }""")
                else:
                    self.b_write.setStyleSheet("")

