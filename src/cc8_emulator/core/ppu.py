from pygame.surface import Surface
import pygame

class PPU:

    _PIXEL_SIZE_BASE: int = 1
    _COLOR_DRAK: tuple = (0x33, 0x2c, 0x50) # 33 2c 50
    _COLOR_LIGHT: tuple = (0x46, 0x87, 0x8f) # 46 87 8f

    def __init__(self, width: int, height: int, scale):
        self.width: int = width
        self.height: int = height
        self.scale: int = scale
        self.pixel_size: int = self._PIXEL_SIZE_BASE * scale
        self.bus = None
        self.frameMap = []
        self.clearDisplay()
        self.frame = Surface((width * self.scale, height * self.scale))

    def conectBus(self, bus):
        self.bus = bus

    def clearDisplay(self):
        self.frameMap = [[0 for i in range(self.width)] for j in range(self.height)]

    def drawnSprite(self, address, x, y, lines) -> bool:
        collision = False
        sprite = bytearray()
        for i in range(lines):
            sprite.append(self.bus.read(address + i))
        indexY = y % self.height
        for byte in sprite:
            indexX = x % self.width
            for bit in f"{byte:08b}":
                if bit == '1' and (indexX < self.width and indexY < self.height):
                    if self.frameMap[indexY][indexX] == 1:
                        collision = True
                        self.frameMap[indexY][indexX] = 0
                    else:
                        self.frameMap[indexY][indexX] = 1
                indexX += 1
            indexY += 1
        return collision
    
    def getFrame(self):
        self.frame.fill(self._COLOR_DRAK)
        for i in range(self.height):
            for j in range(self.width):
                if self.frameMap[i][j] == 1:
                    pygame.draw.rect(self.frame,self._COLOR_LIGHT,(j * self.pixel_size, i * self.pixel_size, self.pixel_size, self.pixel_size))
        
        return self.frame