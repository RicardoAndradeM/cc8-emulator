from ..data.characters import characters

class Memory:
    """
    RAM memory console emulation

    The main memory ras has 4kB
    """

    def __init__(self, rom: bytes = None):
        # From 0x000 to 0x1FF, the memory is empyt, except for the fonts
        # The CHIP-8 fonts are load at the address 0x200
        self._memory: bytearray = bytearray(4096)
        self._loadCharacters(characters)
        if rom:
            self.loadRomOnMemory(rom)

    def loadRomOnMemory(self, rom: bytes):
        #The ROM is loaded at the adress 0x200
        for index in range(len(rom)):
            self.write(self._getLoadAddress(index), rom[index])
    
    def write(self, address, data):
        self._memory[address] = data

    def read(self, address) -> int:
        return self._memory[address]

    def getMemoryDump(self) -> bytearray:
        return self._memory
    
    def _loadCharacters(self, characters: dict):
        # Characters is loaded from 0x050 to 0x09F
        position: int = 0
        for characterIndex in characters:
            for characterByte in characters[characterIndex]:
                self.write(self._getCharactersAddress(position), characterByte)
                position += 1

    def _getCharactersAddress(self, position: int) -> int:
        return position + 0x050
    
    def _getLoadAddress(self, position: int) -> int:
        return position + 0x200