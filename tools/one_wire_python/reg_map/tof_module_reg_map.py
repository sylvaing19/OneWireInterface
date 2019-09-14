"""
Structure typing:
OneWireRegisterMap: ([OneWireRegisterEntry, ...], [OneWireRegisterEntry, ...])
OneWireRegisterEntry: (int, int, str, bool, int, int, str)

Structure meaning:
OneWireRegisterMap: ([EEPROM_register, ...], [RAM_register, ...])
OneWireRegisterEntry: (address, size, name, writable, min, max, docstring)
"""

OneWireRegisterMap = (
[  # EEPROM Area
    (0, 2, "Model number", False, 0, 65535, ""),
    (2, 1, "Firmware version", False, 0, 255, ""),
    (3, 1, "Device ID", True, 0, 253, ""),
    (4, 1, "Baudrate", True, 1, 207, ""),
    (5, 1, "Return delay time", True, 0, 254, ""),
    (6, 1, "Status return level", True, 0, 2, ""),
    (7, 2, "Minimum range", True, 4, 65534, ""),
    (9, 2, "Maximum range", True, 4, 65534, ""),
    (11, 2, "Quality threshold", True, 0, 65534, ""),
    (13, 4, "Inter-measurement period", True, 0, 2 ** 32 - 1, ""),
    (17, 2, "Minimum range (Aux)", True, 4, 65534, ""),
    (19, 2, "Maximum range (Aux)", True, 4, 65534, ""),
    (21, 2, "Quality threshold (Aux)", True, 0, 65534, ""),
    (23, 4, "Inter-measurement period (Aux)", True, 0, 2 ** 32 - 1, ""),
    (27, 1, "Auto-start measurements", True, 0, 1, ""),
    (28, 1, "Polling mode", True, 0, 1, ""),
    (29, 1, "Polling mode (Aux)", True, 0, 1, ""),
],
[  # RAM Area
    (32, 1, "Main sensor enabled", True, 0, 1, ""),
    (33, 1, "Auxiliary sensor enabled", True, 0, 1, ""),
    (34, 1, "Wiring status", False, 0, 3, ""),
    (35, 1, "Measurement count since last read", False, 0, 254, ""),
    (36, 2, "Range", False, 0, 65534, ""),
    (38, 2, "Raw range", False, 0, 65534, ""),
    (40, 2, "Quality", False, 0, 65534, ""),
    (42, 1, "Measurement count since last read (Aux)", False, 0, 254, ""),
    (43, 2, "Range (Aux)", False, 0, 65534, ""),
    (45, 2, "Raw range (Aux)", False, 0, 65534, ""),
    (47, 2, "Quality (Aux)", False, 0, 65534, ""),
    (49, 1, "Input voltage", False, 0, 175, ""),
    (50, 1, "Lock", True, 0, 1, ""),
])
