from .memory import Memory
from .ppu import PPU

class Bus:
    def __init__(self, ram: Memory, ppu: PPU):
        self.ram = ram
        self.ppu = ppu

    def read(self, address):
        return self.ram.read(address)
    
    def clearDisplay(self):
        self.ppu.clearDisplay()

    def drawnSprite(self, address, x, y, lines):
        return self.ppu.drawnSprite(address, x, y, lines)