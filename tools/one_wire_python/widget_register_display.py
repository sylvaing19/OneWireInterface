from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QVBoxLayout,
                             QScrollArea, QHBoxLayout, QComboBox, QFileDialog)
from widget_register_entry import WidgetRegisterEntryList
from reg_map.reg_map import get_register_map_list
from os.path import dirname, join
import json


class WidgetRegisterDisplay(QWidget):
    def __init__(self, master, cb_read, cb_write):
        super().__init__(master)
        self.reg_map_list = get_register_map_list()
        self.current_preset_dir = join(dirname(__file__), "presets")

        # Widgets
        title = QLabel("Registers editor", self)
        self.register_entries = WidgetRegisterEntryList(self, cb_read, cb_write)
        reg_map_combobox = QComboBox(self)
        reg_map_combobox.addItems([r[0] for r in self.reg_map_list])
        reg_map_combobox.currentIndexChanged.connect(self._update_reg_list)
        self.b_read_all = QPushButton("Read all", self)
        self.b_save_eeprom = QPushButton("Save EEPROM", self)
        self.b_save_eeprom.clicked.connect(self._save_eeprom)
        self.b_load_eeprom = QPushButton("Load EEPROM", self)
        self.b_load_eeprom.clicked.connect(self._load_eeprom)
        self.b_read_all.clicked.connect(self.register_entries.read_all)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.register_entries)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedWidth(self.register_entries.width() + 25)

        # Layout
        title_grid = QHBoxLayout()
        title_grid.addWidget(title)
        title_grid.addWidget(reg_map_combobox)
        title_grid.addWidget(self.b_read_all)
        title_grid.addWidget(self.b_save_eeprom)
        title_grid.addWidget(self.b_load_eeprom)
        title_grid.setStretch(0, 1)
        title_grid.setContentsMargins(10, 5, 0, 0)
        v_grid = QVBoxLayout()
        v_grid.addLayout(title_grid)
        v_grid.addWidget(self.scroll_area)
        v_grid.setStretch(1, 1)
        v_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(v_grid)

        # Init
        self._update_reg_list(reg_map_combobox.currentIndex())

    def set_enabled(self, e):
        self.b_read_all.setEnabled(e)
        self.b_save_eeprom.setEnabled(e)
        self.b_load_eeprom.setEnabled(e)
        self.register_entries.setEnabled(e)

    def _update_reg_list(self, index):
        self.register_entries.init(self.reg_map_list[index])
        self.scroll_area.setFixedWidth(self.register_entries.width() + 25)

    def _save_eeprom(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save EEPROM",
                                                self.current_preset_dir,
                                                "OW EEPROM (*.ow)")
        if len(file_name) > 0:
            self.current_preset_dir = dirname(file_name)
            with open(file_name, 'w') as file:
                json.dump(self.register_entries.export_eeprom(), file)

    def _load_eeprom(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load EEPROM",
                                                   self.current_preset_dir,
                                                   "OW EEPROM (*.ow)")
        if len(file_name) > 0:
            self.current_preset_dir = dirname(file_name)
            with open(file_name, 'r') as file:
                try:
                    self.register_entries.import_eeprom(json.load(file))
                except (ValueError, IndexError):
                    pass
