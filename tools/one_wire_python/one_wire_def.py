class OWDef:
    def __init__(self, ll_value, hl_value, name):
        self.ll_value = int(ll_value)
        self.hl_value = int(hl_value)
        self.name = str(name)


OW_RETURN_LEVEL = [
    OWDef(2, 2, "ALL"),
    OWDef(1, 1, "READ"),
    OWDef(0, 0, "PING"),
]

OW_BAUDRATE = [
    OWDef(1, 1000000, "1M"),
    OWDef(3, 500000, "500k"),
    OWDef(4, 400000, "400k"),
    OWDef(7, 250000, "250k"),
    OWDef(9, 200000, "200k"),
    OWDef(16, 115200, "115200"),
    OWDef(34, 57600, "57600"),
    OWDef(103, 19200, "19200"),
    OWDef(207, 9600, "9600"),
]

OW_COM_STATUS = [
    "timeout",          # 1
    "data missing",     # 2
    "",                 # 4
    "",                 # 8
    "checksum err"      # 16
    "",                 # 32
    "",                 # 64
    "communication err",# 128
]

OW_DEVICE_STATUS = [
    "main sensor err",  # 1
    "aux sensor err",   # 2
    "input voltage err",# 4
    "range err",        # 8
    "checksum err"      # 16
    "",                 # 32
    "instruction err",  # 64
    "",                 # 128
]
