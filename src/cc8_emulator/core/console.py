from .memory import Memory
from .cpu import CPU

class Console:
    """Console emulation class"""
    
    def __init__(self):
        self.CPU = CPU()
        self.RAM = Memory()