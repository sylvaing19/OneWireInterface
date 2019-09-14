from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QFrame, QVBoxLayout,
                             QScrollArea, QHBoxLayout)
from widget_register_entry import WidgetRegisterEntryList

from reg_map.tof_module_reg_map import OneWireRegisterMap


class WidgetRegisterDisplay(QWidget):
    def __init__(self, master, cb_read, cb_write):
        super().__init__(master)
        # Widgets
        title = QLabel("Registers editor", self)
        b_read_all = QPushButton("Read all", self)
        b_save_eeprom = QPushButton("Save EEPROM", self)
        b_save_eeprom.clicked.connect(self._save_eeprom)
        b_load_eeprom = QPushButton("Load EEPROM", self)
        b_load_eeprom.clicked.connect(self._load_eeprom)
        self.register_entries = WidgetRegisterEntryList(self, cb_read, cb_write)
        self.register_entries.init(OneWireRegisterMap) #todo allow to change reg map from gui
        b_read_all.clicked.connect(self.register_entries.read_all)
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.register_entries)
        scroll_area.setWidgetResizable(False)
        scroll_area.setFixedWidth(self.register_entries.width() + 25)

        # Layout
        title_grid = QHBoxLayout()
        title_grid.addWidget(title)
        title_grid.addWidget(b_read_all)
        title_grid.addWidget(b_save_eeprom)
        title_grid.addWidget(b_load_eeprom)
        title_grid.setStretch(0, 1)
        title_grid.setContentsMargins(10, 5, 0, 0)
        v_grid = QVBoxLayout()
        v_grid.addLayout(title_grid)
        v_grid.addWidget(scroll_area)
        v_grid.setStretch(1, 1)
        v_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(v_grid)

    def _save_eeprom(self):
        pass

    def _load_eeprom(self):
        pass
