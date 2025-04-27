from .bus import Bus
import sys

class CPU:
    """CPU Console emulation class"""

    _MASK_FIST_NIBBLE_BYTE = 0b11110000
    _MASK_SECOND_NIBBLE_BYTE = 0b00001111
    _MASK_REMOVE_CARRY = 0b0000000011111111

    def __init__(self, bus: Bus):
        self.pc: int = 0x200
        self.i: int = 0
        self.delay: int = 0
        self.buzzer: int = 0
        self.bus: Bus = bus
        self.registers: dict = {
            0x0: 0x00,
            0x1: 0x00,
            0x2: 0x00,
            0x3: 0x00,
            0x4: 0x00,
            0x5: 0x00,
            0x6: 0x00,
            0x7: 0x00,
            0x8: 0x00,
            0x9: 0x00,
            0xA: 0x00,
            0xB: 0x00,
            0xC: 0x00,
            0xD: 0x00,
            0xE: 0x00,
            0xF: 0x00
        }
        self.stack: list = []

    def cycle(self):
        instruction: bytearray =  self._readInstruction()
        self.pc += 2
        fistNibble, secondNibble, thirdNibble, fourthNibble = self._decodeinstruction(instruction)
        self._execInstruction(fistNibble, secondNibble, thirdNibble, fourthNibble)
    
    def _readInstruction(self):
        instruction: bytearray = bytearray()
        instruction.append(self.bus.read(self.pc))
        instruction.append(self.bus.read(self.pc + 1))
        return instruction
    
    def _decodeinstruction(self, instruction: bytearray):
        fistNibble = instruction[0] & self._MASK_FIST_NIBBLE_BYTE
        secondNibble = instruction[0] & self._MASK_SECOND_NIBBLE_BYTE
        thirdNibble =  instruction[1] & self._MASK_FIST_NIBBLE_BYTE
        fourthNibble =  instruction[1] & self._MASK_SECOND_NIBBLE_BYTE
        return (fistNibble, secondNibble, thirdNibble, fourthNibble)
    
    def _execInstruction(self, opCode, secondNibble, thirdNibble, fourthNibble):
        instructions = {
            0x00: self._opc0,
            0x10: self._opc1,
            0x60: self._opc6,
            0x70: self._opc7,
            0xA0: self._opcA,
            0xD0: self._opcD
        }
        instructions[opCode](secondNibble, thirdNibble, fourthNibble)

    def _opc0(self, secondNibble, thirdNibble, fourthNibble):
        # 00E0 Clear screen
        if self._getNNN(secondNibble, thirdNibble, fourthNibble) == 0x0E0 :
            self.bus.clearDisplay()
    
    def _opc1(self, secondNibble, thirdNibble, fourthNibble):
        # 1NNN Jump
        self.pc = self._getNNN(secondNibble, thirdNibble, fourthNibble)

    def _opc6(self, x, thirdNibble, fourthNibble):
        # 6XNN Set register with value NN
        self.registers[x] = self._getNN(thirdNibble, fourthNibble)

    def _opc7(self, x, thirdNibble, fourthNibble):
        # 7XNN Add the value NN to VX
        sum = self.registers[x] + self._getNN(thirdNibble, fourthNibble)
        self.registers[x] = sum & self._MASK_REMOVE_CARRY
    
    def _opcA(self, secondNibble, thirdNibble, fourthNibble):
        # ANNN Set index register
        self.i = self._getNNN(secondNibble, thirdNibble, fourthNibble)

    def _opcD(self, x, y, n):
        # DXYN draw sprite
        self.registers[0xF] = 0x01 if self.bus.drawnSprite(self.i, self.registers[x], self.registers[y >> 4], n) else 0x00

    def _getNN(self, thirdNibble, fourthNibble):
        return thirdNibble + fourthNibble

    def _getNNN(self, secondNibble, thirdNibble, fourthNibble):
        return (secondNibble << 8) + thirdNibble + fourthNibble