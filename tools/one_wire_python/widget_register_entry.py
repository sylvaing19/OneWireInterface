from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QHBoxLayout,
                             QVBoxLayout)
from functools import partial
from input_field import InputField
from one_wire_python import OneWireDataMissing


class WidgetRegisterEntry(QWidget):
    def __init__(self, master, address, min_val, max_val, name, cb_read,
                 docstring="", cb_write=None):
        super().__init__(master)
        # Callbacks
        self.cb_read = cb_read
        self.cb_write = cb_write

        # Widgets
        l_addr = QLabel(hex(address), self)
        l_addr.setEnabled(False)
        l_name = QLabel(name, self)
        l_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.field = InputField(self, min_val, max_val)
        self.field.setFixedWidth(77)
        self.field.set_callback_value_changed(self._update_gui_value)
        self.b_read = QPushButton("Read", self)
        self.b_read.setFixedSize(55, 28)
        self.b_read.clicked.connect(self.read)
        self.b_write = QPushButton("Write", self)
        self.b_write.setFixedSize(55, 28)
        self.b_write.setEnabled(False)
        if self.cb_write is not None:
            self.b_write.clicked.connect(self.write)
            self.field.set_callback_value_valid(self.b_write.setEnabled)
            self.field.set_callback_return_pressed(self.write)
        else:
            self.field.set_read_only(True)

        # Layout
        grid = QHBoxLayout()
        grid.addWidget(l_addr)
        grid.addWidget(l_name)
        grid.addSpacing(5)
        grid.addWidget(self.field)
        grid.addWidget(self.b_read)
        grid.addWidget(self.b_write)
        grid.setStretch(1, 1)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

        # Members
        self.address = address
        self.device_value = None
        self.gui_value = self.field.get_value()
        self._std_style = "QPushButton {}"
        self._bold_style = "QPushButton { font: bold; }"

        # Init
        self._update_boldness()
        if len(docstring) > 0:
            l_name.setToolTip(docstring)

    def read(self):
        try:
            try:
                self.device_value = self.cb_read(self.address)
                self.field.set_value(self.device_value)
            except ValueError:
                print("Value read from device at address", self.address,
                      "is out of range")
                raise
        except (ValueError, OneWireDataMissing):
            self.device_value = None
            self.field.clear()
        finally:
            self._update_gui_value(self.field.get_value())

    def write(self):
        if self.b_write.isEnabled():
            if self.cb_write(self.address, self.gui_value):
                self.device_value = self.gui_value
                self._update_boldness()

    def set_gui_value(self, value):
        try:
            self.field.set_value(value)
        except ValueError:
            self.field.clear()
        finally:
            self._update_gui_value(self.field.get_value())

    def get_gui_value(self):
        return self.gui_value

    def _update_gui_value(self, value):
        self.gui_value = value
        self._update_boldness()

    def _update_boldness(self):
        if self.device_value is None:
            self.b_read.setStyleSheet(self._bold_style)
            self.b_write.setStyleSheet(self._std_style)
        else:
            self.b_read.setStyleSheet(self._std_style)
            if self.device_value != self.gui_value:
                self.b_write.setStyleSheet(self._bold_style)
            else:
                self.b_write.setStyleSheet(self._std_style)


class WidgetRegisterEntryList(QWidget):
    def __init__(self, master, cbRead, cbWrite):
        super().__init__(master)
        # Callbacks
        self.cb_read = cbRead
        self.cb_write = cbWrite

        # Layout
        self.grid = QVBoxLayout()
        self.grid.setSpacing(3)
        self.setLayout(self.grid)

        # Members
        self.entries = []
        self.addresses = []
        self.sizes = []
        self.eeprom_size = 0

    def init(self, register_map):
        self.entries = []
        self.addresses = []
        self.sizes = []
        self.eeprom_size = len(register_map[1])
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                self.grid.removeItem(item)
        if len(register_map[1]) > 0:
            label_eeprom = QLabel("EEPROM Area", self)
            label_eeprom.setAlignment(Qt.AlignCenter)
            label_eeprom.setStyleSheet("QLabel { font: bold; }")
            self.grid.addWidget(label_eeprom)
            for e in register_map[1]:
                self._add_reg_entry(e)
        if len(register_map[2]) > 0:
            label_ram = QLabel("RAM Area", self)
            label_ram.setAlignment(Qt.AlignCenter)
            label_ram.setStyleSheet("QLabel { font: bold; }")
            self.grid.addWidget(label_ram)
            for e in register_map[2]:
                self._add_reg_entry(e)
        self.grid.addStretch(1)

    def read_all(self):
        for entry in self.entries:
            entry.read()

    def export_eeprom(self):
        output = []
        for i in range(self.eeprom_size):
            output.append(
                (self.addresses[i],
                 self.sizes[i],
                 self.entries[i].get_gui_value()))
        return output

    def import_eeprom(self, value_list):
        i = 0
        for entry in value_list:
            if len(entry) != 3:
                raise IndexError
            if entry[0] != self.addresses[i]:
                raise ValueError
            if entry[1] != self.sizes[i]:
                raise ValueError
            self.entries[i].set_gui_value(entry[2])
            i += 1

    #  Wrapper to make the use of 'partial' clearer
    def _read(self, address, size):
        return self.cb_read(address, size)

    #  Wrapper to make the use of 'partial' clearer
    def _write(self, address, value, size):
        return self.cb_write(address, size, value)

    def _add_reg_entry(self, reg_entry):
        r_cb = partial(self._read, size=reg_entry[1])
        if reg_entry[3]:
            w_cb = partial(self._write, size=reg_entry[1])
        else:
            w_cb = None
        w = WidgetRegisterEntry(self, reg_entry[0], reg_entry[4], reg_entry[5],
                                reg_entry[2], r_cb, reg_entry[6], w_cb)
        self.entries.append(w)
        self.addresses.append(reg_entry[0])
        self.sizes.append(reg_entry[1])
        self.grid.addWidget(w)
