from .memory import Memory
from .cpu import CPU
from .bus import Bus
from .ppu import PPU
from ..input.keyboard import Keyboard

class Console:
    """Console emulation class"""
    
    DISPLAY_WIDTH: int = 64
    DISPLAY_HEIGHT: int = 32

    def __init__(self, rom: bytes):

        self.ram = Memory(rom)
        self.ppu = PPU(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, 10)
        self.keyboard = Keyboard()
        self.bus = Bus(self.ram, self.ppu, self.keyboard)
        self.ppu.conectBus(self.bus)
        self.cpu = CPU(self.bus)

    def step(self):            
        self.keyboard.updateKeysPressed()
        self.cpu.cycle()
        return 0