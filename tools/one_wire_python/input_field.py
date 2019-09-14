from PyQt5.QtWidgets import (QWidget, QGridLayout, QLineEdit)


class InputField(QWidget):
    def __init__(self, master, aMin, aMax):
        super().__init__(master)
        # Members
        self._min = int(aMin)
        self._max = int(aMax)
        assert self._min <= self._max
        self._value = self._min

        # Callbacks
        self._cb_value_changed = None
        self._cb_value_valid = None
        self._cb_return_pressed = None

        # Widgets
        self._field = QLineEdit(self)
        self._field.textEdited.connect(self._user_edit)
        self._field.returnPressed.connect(self._return_pressed)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self._field)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

        # Init
        self.clear()

    def set_value(self, value):
        val = int(value)
        if not self._min <= val <= self._max:
            raise ValueError
        self._value = val
        self._field.setText(str(val))
        self.display_ok()

    def get_value(self):
        return self._value

    def clear(self):
        self._value = self._min
        self._field.setText("")
        self.display_wrong()

    def set_callback_value_changed(self, callback):
        self._cb_value_changed = callback

    def set_callback_value_valid(self, callback):
        self._cb_value_valid = callback

    def set_callback_return_pressed(self, callback):
        self._cb_return_pressed = callback

    def display_ok(self):
        self._field.setStyleSheet("")
        if self._cb_value_valid is not None:
            self._cb_value_valid(True)

    def display_wrong(self):
        self._field.setStyleSheet(
            """QLineEdit { background-color: rgb(249, 83, 83) }""")
        if self._cb_value_valid is not None:
            self._cb_value_valid(False)

    def set_read_only(self, read_only):
        self._field.setReadOnly(read_only)

    def _user_edit(self, text):
        try:
            self.set_value(text)
            if self._cb_value_changed is not None:
                self._cb_value_changed(self._value)
            self.display_ok()
        except ValueError:
            self.display_wrong()

    def _return_pressed(self):
        if self._cb_return_pressed is not None:
            self._cb_return_pressed()
