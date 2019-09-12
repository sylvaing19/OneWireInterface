class OneWirePacket:
    def __init__(self, device_id: int, instruction: int):
        self.id = device_id
        self.instruction = instruction
        self.address = None
        self.data = bytearray()

    def length(self) -> int:
        l = len(self.data) + 2
        if self.address is not None:
            l += 1
        return l

    def toBytes(self) -> bytes:
        out = bytearray()
        out.append(self.id)
        out.append(self.length())
        out.append(self.instruction)
        if self.address is not None:
            out.append(self.address)
        out += self.data
        checksum = self.checksum(out)
        out.append(checksum)
        return bytes(out)

    @staticmethod
    def checksum(data: bytes) -> int:
        acc = 0
        for b in data:
            acc += b
        acc = acc & 0xFF  # keep only the 8 lower weight bits
        return 0xFF - acc  # bitwise not on 8 bits
