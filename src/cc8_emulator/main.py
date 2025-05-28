from .rom.load_rom import LoadRom
from .core.console import Console
from .video.renderer import Renderer
import sys, pygame

FRAMERATE: int = 60
#ROM_PATH = "assets/IBM_Logo.ch8"
DISPLAY_SCALE: int = 10

def main():
    # TODO: create a system for the user to choose the ROM file
    rom = LoadRom(ROM_PATH)
    console = Console(rom.data)
    renderer = Renderer(console.DISPLAY_WIDTH, console.DISPLAY_HEIGHT, DISPLAY_SCALE)
    isRuning = True

    while isRuning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRuning = False
        for i in range(int(700 / FRAMERATE)):
            console.step()
        frame = console.ppu.getFrame()
        renderer.renderFrame(frame)
        renderer.tick(FRAMERATE)

    pygame.quit()
    sys.exit(0)