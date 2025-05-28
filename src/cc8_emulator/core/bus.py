from .memory import Memory
from .ppu import PPU
from ..input.keyboard import Keyboard

class Bus:
    def __init__(self, ram: Memory, ppu: PPU, keyboard: Keyboard):
        self.ram = ram
        self.ppu = ppu
        self.keyboard = keyboard

    def read(self, address):
        return self.ram.read(address)
    
    def write(self, address, data):
        self.ram.write(address, data)
    
    def clearDisplay(self):
        self.ppu.clearDisplay()

    def drawnSprite(self, address, x, y, lines):
        return self.ppu.drawnSprite(address, x, y, lines)
    
    def keyIsPressed(self, key):
        return self.keyboard.keyIsPressed(key)
    
    def getKeyStates(self):
        return self.keyboard.keys