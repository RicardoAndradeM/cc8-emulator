class Memory:
    """
    RAM memory console emulation

    The main memory ras has 4kB
    """

    def __init__(self):
        self.memory: bytearray = bytearray(4096)