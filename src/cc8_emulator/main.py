from .rom.load_rom import LoadRom
from .core.console import Console
from .video.renderer import Renderer
import sys, pygame, logging

FRAMERATE: int = 60
DISPLAY_SCALE: int = 10

def main():
    if len(sys.argv) > 1:
        romPath = sys.argv[1]
    else:
        logging.error("No ROM provided by the user")
        sys.exit(1)
    rom = LoadRom(romPath)
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