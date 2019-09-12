import serial
import struct
from typing import Tuple, List, Optional

from one_wire_packet import OneWirePacket

ONE_WIRE_BROADCAST_ID = 0xFD

class OneWireException(Exception):
    pass
class OneWireTimeout(OneWireException):
    pass
class OneWireDataMissing(OneWireException):
    pass
class OneWireChecksumError(OneWireException):
    pass
class OneWireComError(OneWireException):
    pass


class OneWireMasterInterface:
    Instructions = {
        "PING": 1,
        "READ": 2,
        "WRITE": 3,
        "REG_WRITE": 4,
        "ACTION": 5,
        "FACTORY_RESET": 6,
        "SOFT_RESET": 7,
        "SYNC_WRITE": 131,
    }

    def __init__(self, port, baudrate=400000, timeout=0.1):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        assert timeout is not None  # do not allow blocking mode
        self.serial.timeout = timeout

    def open(self, port=None, baudrate=None, timeout=None):
        if port is not None:
            self.serial.port = port
        if baudrate is not None:
            self.serial.baudrate = baudrate
        if timeout is not None:
            self.serial.timeout = timeout
        self.serial.open()

    def close(self):
        self.serial.close()

    def readU8(self, device_id: int, addr: int) -> Tuple[int, int]:
        return self._read(device_id, addr, "<B")

    def readU16(self, device_id: int, addr: int) -> Tuple[int, int]:
        return self._read(device_id, addr, "<H")

    def readU32(self, device_id: int, addr: int) -> Tuple[int, int]:
        return self._read(device_id, addr, "<I")

    def writeU8(self, device_id: int, addr: int, data: int, expect_answer: bool = True) -> Optional[int]:
        return self._write(device_id, addr, data, "<B", expect_answer)

    def writeU16(self, device_id: int, addr: int, data: int, expect_answer: bool = True) -> Optional[int]:
        return self._write(device_id, addr, data, "<H", expect_answer)

    def writeU32(self, device_id: int, addr: int, data: int, expect_answer: bool = True) -> Optional[int]:
        return self._write(device_id, addr, data, "<I", expect_answer)

    def regWrite(self, device_id: int, addr: int, data: int, expect_answer: bool = True) -> Optional[int]:
        pass

    def syncWrite(self, id_list: List[int], addr: int, data: int) -> None:
        pass

    def ping(self, device_id: int) -> int:
        p = OneWirePacket(device_id, self.Instructions["PING"])
        return self._transaction(p, True)[0]

    def action(self, device_id: int, expect_answer: bool = True) -> Optional[int]:
        pass

    def factoryReset(self, device_id: int, expect_answer: bool = True) -> Optional[int]:
        p = OneWirePacket(device_id, self.Instructions["FACTORY_RESET"])
        err, _ = self._transaction(p, expect_answer)
        if expect_answer:
            return err
        else:
            return None

    def softReset(self, device_id: int, expect_answer: bool = True) -> Optional[int]:
        p = OneWirePacket(device_id, self.Instructions["SOFT_RESET"])
        err, _ = self._transaction(p, expect_answer)
        if expect_answer:
            return err
        else:
            return None

    def _read(self, device_id: int, addr: int, data_format: str) -> Tuple[int, int]:
        p = OneWirePacket(device_id, self.Instructions["READ"])
        p.address = addr
        p.data.append(struct.calcsize(data_format))
        err, data = self._transaction(p, True)
        if len(data) == 0:
            raise OneWireDataMissing
        try:
            val, = struct.unpack(data_format, data)
        except struct.error:
            raise OneWireComError
        return err, val

    def _write(self, device_id: int, addr: int, data: int, data_format: str, expect_answer: bool) -> Optional[int]:
        p = OneWirePacket(device_id, self.Instructions["WRITE"])
        p.address = addr
        p.data = struct.pack(data_format, data)
        err, _ = self._transaction(p, expect_answer)
        if expect_answer:
            return err
        else:
            return None

    def _transaction(self, packet: OneWirePacket, expect_answer: bool) -> Tuple[int, bytes]:
        self._sendPacket(packet)
        if expect_answer and packet.id != ONE_WIRE_BROADCAST_ID:
            return self._receivePacket(packet.id)
        return 0, bytes()

    def _sendPacket(self, packet: OneWirePacket) -> None:
        self.serial.write(bytes([0xFF, 0xFF]))
        self.serial.write(packet.toBytes())

    def _receivePacket(self, expected_id: int) -> Tuple[int, bytes]:
        header = self.serial.read(4)
        if len(header) != 4:
            raise OneWireTimeout
        if header[0] != 0xFF or header[1] != 0xFF:
            raise OneWireComError
        if header[2] != expected_id:
            raise OneWireComError
        if header[3] < 2:
            raise OneWireComError
        data = self.serial.read(header[3])
        if len(data) != header[3]:
            raise OneWireTimeout
        status = data[0]
        if data[-1] != OneWirePacket.checksum(header[2:] + data[:-1]):
            raise OneWireChecksumError
        return status, data[1:-1]
