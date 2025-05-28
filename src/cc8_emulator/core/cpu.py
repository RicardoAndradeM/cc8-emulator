from .bus import Bus
from random import Random
from time import perf_counter
from ..input.keys import Key
import logging
import sys

class CPU:
    """CPU Console emulation class"""

    _NIBBLE_BIT_DESLOCATION = 4
    _MASK_SECOND_NIBBLE_BYTE = 0X0F
    _MASK_REMOVE_CARRY = 0X00FF
    _LSB_MASK = 0b1
    _INDEX_MASK = 0X0FFF
    _MSB_DESLOCATION = 7
    _TICK_TIME = 1 / 60

    def __init__(self, bus: Bus, modernMode: bool = False):
        self.modernMode = modernMode
        self.lastUpdateTimerTime = perf_counter()
        self.randomNumber = Random()

        self.pc: int = 0x200
        self.i: int = 0
        self.delay: int = 0
        self.buzzer: int = 0 # TODO: implementar lógica de som
        self.bus: Bus = bus
        self.stack: list = []

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

        self.dispatch_main = {
            0x0: self._opc0,
            0x1: self._opc1,
            0x2: self._opc2,
            0x3: self._opc3,
            0x4: self._opc4,
            0x5: self._opc5,
            0x6: self._opc6,
            0x7: self._opc7,
            0x8: self._opc8,
            0x9: self._opc9,
            0xA: self._opcA,
            0xB: self._opcB,
            0xC: self._opcC,
            0xD: self._opcD,
            0xE: self._opcE,
            0xF: self._opcF,
        }

        self.dispatch_group8 = {
            0x0: self._opc8_variant0,
            0x1: self._opc8_variant1,
            0x2: self._opc8_variant2,
            0x3: self._opc8_variant3,
            0x4: self._opc8_variant4,
            0x5: self._opc8_variant5,
            0x6: self._opc8_variant6,
            0x7: self._opc8_variant7,
            0xE: self._opc8_variantE
        }

        self.dispatch_groupF = {
            0x07: self._opcF_variant07,
            0x0A: self._opcF_variant0A,
            0x15: self._opcF_variant15,
            0x18: self._opcF_variant18,
            0x1E: self._opcF_variant1E,
            0x29: self._opcF_variant29,
            0x33: self._opcF_variant33,
            0x55: self._opcF_variant55,
            0x65: self._opcF_variant65,
        }


    def cycle(self):
        instruction: bytearray =  self._readInstruction()
        self._incrementPC()
        fistNibble, secondNibble, thirdNibble, fourthNibble = self._decodeinstruction(instruction)
        self._execInstruction(fistNibble, secondNibble, thirdNibble, fourthNibble)
        self._updateTimers()
    
    def _readInstruction(self):
        instruction: bytearray = bytearray()
        instruction.append(self.bus.read(self.pc))
        instruction.append(self.bus.read(self.pc + 1))
        return instruction
    
    def _decodeinstruction(self, instruction: bytearray):
        fistNibble = instruction[0] >> self._NIBBLE_BIT_DESLOCATION
        secondNibble = instruction[0] & self._MASK_SECOND_NIBBLE_BYTE
        thirdNibble =  instruction[1] >> self._NIBBLE_BIT_DESLOCATION
        fourthNibble =  instruction[1] & self._MASK_SECOND_NIBBLE_BYTE
        return (fistNibble, secondNibble, thirdNibble, fourthNibble)
    
    def _execInstruction(self, opCode, secondNibble, thirdNibble, fourthNibble):
        try:
            self.dispatch_main[opCode](secondNibble, thirdNibble, fourthNibble)
        except:
            logging.warning("This operation is not supported")

    def _updateTimers(self):
        if (self.delay > 0) or (self.buzzer > 0):
            actualTime  = perf_counter()
            if actualTime - self.lastUpdateTimerTime >= self._TICK_TIME:
                if self.delay > 0:
                    self.delay -= 1
                if self.buzzer > 0:
                    self.delay -= 1
                self.lastUpdateTimerTime = actualTime

    def _opc0(self, secondNibble, thirdNibble, fourthNibble):
        # 00E0 Clear screen
        if self._getNNN(secondNibble, thirdNibble, fourthNibble) == 0x0E0 :
            self.bus.clearDisplay()
        # 00EE Returns from a subroutine
        elif self._getNNN(secondNibble, thirdNibble, fourthNibble) == 0x0EE:
            self.pc = self.stack.pop()
        else:
            # 0NNN is not supported
            logging.warning("0NNN is not supported")
    
    def _opc1(self, secondNibble, thirdNibble, fourthNibble):
        # 1NNN Jump to NNN address
        self.pc = self._getNNN(secondNibble, thirdNibble, fourthNibble)

    def _opc2(self, secondNibble, thirdNibble, fourthNibble):
        # 2NNN Call subroutine NNN
        self.stack.append(self.pc)
        self.pc = self._getNNN(secondNibble, thirdNibble, fourthNibble)

    def _opc3(self, x, thirdNibble, fourthNibble):
        # 3XNN Skips the next instruction if VX is equal to NN
        if self.registers[x] == self._getNN(thirdNibble, fourthNibble):
            self._incrementPC()

    def _opc4(self, x, thirdNibble, fourthNibble):
        # 4XNN Skips the next instruction if VX is not equal to NN
        if self.registers[x] != self._getNN(thirdNibble, fourthNibble):
            self._incrementPC()

    def _opc5(self, x, y, ignoredValue):
        #5XY0 Skips the next instruction if VX is equal to VY
        if self.registers[x] == self.registers[y]:
            self._incrementPC()

    def _opc6(self, x, thirdNibble, fourthNibble):
        # 6XNN Set register with value NN
        self.registers[x] = self._getNN(thirdNibble, fourthNibble)

    def _opc7(self, x, thirdNibble, fourthNibble):
        # 7XNN Add the value NN to VX
        sum = self.registers[x] + self._getNN(thirdNibble, fourthNibble)
        self.registers[x] = sum & self._MASK_REMOVE_CARRY

    def _opc8(self, secondNibble, thirdNibble, variant):
        # Dispatch and execulte group variant 8
        try:
            self.dispatch_group8[variant](secondNibble, thirdNibble)
        except:
            logging.warning("This operation is not supported")
    
    def _opc8_variant0(self, x, y):
        # 8XY0 Set VX to the value of VY
        self.registers[x] = self.registers[y]

    def _opc8_variant1(self, x, y):
        # 8XY1 set VX with OR between VX and VY
        self.registers[x] = self.registers[x] | self.registers[y]
    
    def _opc8_variant2(self, x, y):
        # 8XY2 set VX with AND between VX and VY
        self.registers[x] = self.registers[x] & self.registers[y]
    
    def _opc8_variant3(self, x, y):
        # 8XY3 set VX with AND between VX and VY
        self.registers[x] = self.registers[x] ^ self.registers[y]

    def _opc8_variant4(self, x, y):
        # 8XY4 set VX with XOR between VX and VY
        sum = self.registers[x] + self.registers[y]
        self.registers[x] = sum & self._MASK_REMOVE_CARRY
        self.registers[0xF] = 1 if sum > 0xFF else 0

    def _opc8_variant5(self, x, y):
        # 8XY5 subtract VX from VY,
        # VF is set to 0 if there is an underflow, set to 1 otherwise
        if self.registers[y] > self.registers[x]:
            self.registers[x] = 0x100 + self.registers[x] - self.registers[y]
            self.registers[0xF] = 0x00
        else:
            self.registers[x] = self.registers[x] - self.registers[y]
            self.registers[0xF] = 0x01

    def _opc8_variant6(self, x, y):
        # 8XY6 moves the value of VY to VX (original behavior only),
        # and shifts one bit to the right
        if not self.modernMode:
            self.registers[x] = self.registers[y]
        self.registers[0xF] = self.registers[x] & self._LSB_MASK
        self.registers[x] = self.registers[x] >> 1
    
    def _opc8_variant7(self, x, y):
        # 8XY7 subtract VY from VX,
        # VF is set to 0 if there is an underflow, set to 1 otherwise
        if self.registers[x] > self.registers[y]:
            self.registers[x] = 0x100 + self.registers[y] - self.registers[x]
            self.registers[0xF] = 0x00
        else:
            self.registers[x] = self.registers[y] - self.registers[x]
            self.registers[0xF] = 0x01
    
    def _opc8_variantE(self, x, y):
        # 8XYE moves the value of VY to VX (original behavior only),
        # and shifts one bit to the left
        if not self.modernMode:
            self.registers[x] = self.registers[y]
        self.registers[0xF] = self.registers[x] >> self._MSB_DESLOCATION
        self.registers[x] = (self.registers[x] << 1) & self._MASK_REMOVE_CARRY

    def _opc9(self, x, y, ignoredValue):
        #9XY0 Skips the next instruction if VX is not equal to VY
        if self.registers[x] != self.registers[y]:
            self._incrementPC()
    
    def _opcA(self, secondNibble, thirdNibble, fourthNibble):
        # ANNN Set index register
        self.i = self._getNNN(secondNibble, thirdNibble, fourthNibble)

    def _opcB(self, x, thirdNibble, fourthNibble):
        # BNNN jumps to address XNN + the value of register V0
        # (Modern Mode) BXNN jumps to address XNN + the value of register VX
        jumpAddress = self._getNNN(x, thirdNibble, fourthNibble)
        if self.modernMode:
            jumpAddress += self.registers[x]
        else:
            jumpAddress += self.registers[0x00]
        self.pc = jumpAddress

    def _opcC(self, x, thirdNibble, fourthNibble):
        # CXNN set random number in VX
        self.registers[x] = self.randomNumber.randint(0x00, 0xFF) & self._getNN(thirdNibble, fourthNibble)

    def _opcD(self, x, y, n):
        # DXYN draw sprite
        self.registers[0xF] = 0x01 if self.bus.drawnSprite(self.i, self.registers[x], self.registers[y], n) else 0x00

    def _opcE(self, x, thirdNibble, fourthNibble):
        # EX9E
        if self._getNN(thirdNibble, fourthNibble) == 0x9E:
            if self.bus.keyIsPressed(Key(self.registers[x] & self._MASK_SECOND_NIBBLE_BYTE)):
                self._incrementPC()
        # EXA1
        else:
            if not self.bus.keyIsPressed(Key(self.registers[x] & self._MASK_SECOND_NIBBLE_BYTE)):
                self._incrementPC()
    
    def _opcF(self, x, variant1, variant2):
        # Dispatch and execulte group variant F
        try:
            self.dispatch_groupF[self._getNN(variant1, variant2)](x)
        except:
            logging.warning("This operation is not supported")
    
    def _opcF_variant07(self, x):
        # FX07 sets VX to the delay timer value
        self.registers[x] = self.delay

    def _opcF_variant0A(self, x):
        # FX0A stops execution until a key is pressed, then stores it in vx
        DECREMENT_SIZE = 2
        pressedKeys = self.bus.getKeyStates()
        key_value = ''
        for key, status in pressedKeys.items():
            if status:
                key_value = key.value
                break
        if key_value:
            self.registers[x] = key_value
        else:
            self.pc -= DECREMENT_SIZE

    def _opcF_variant15(self, x):
        # FX15 sets the delay timer to the value of VX
        self.delay = self.registers[x]
        
    def _opcF_variant18(self, x):
        # FX18 sets the buzzer timer to the value of VX
        self.buzzer = self.registers[x]

    def _opcF_variant1E(self, x):
        # FX1E Adds VX value to I
        sum = self.i + self.registers[x]
        self.i = sum & self._INDEX_MASK
        # ambiguous instruction - some interpreters change the value of VF

    def _opcF_variant29(self, x):
        # FX29 set I for character sprite in vx
        CHARACTERE_ADDRESS_BASE = 0x050
        address = CHARACTERE_ADDRESS_BASE + ((self.registers[x] & self._MASK_SECOND_NIBBLE_BYTE) * 5)

    def _opcF_variant33(self, x):
        # FX33 Binary-coded decimal conversion
        characters = [
            int(self.registers[x] / 100),
            int((self.registers[x] % 100) / 10),
            self.registers[x] % 10
        ]
        for deslocation in range(3):
            self.bus.write(self.i + deslocation, characters[deslocation])
    
    def _opcF_variant55(self, x):
        # FX55 write data from v0 to VX to memory
        deslocation = 0
        for vIndex in range(x + 1):
            self.bus.write(self.i + deslocation, self.registers[vIndex])
            if self.modernMode:
                deslocation += 1
            else:
                self.i += 1

    def _opcF_variant65(self, x):
        # FX65 write memory data from v0 to VX
        deslocation = 0
        for vIndex in range(x + 1):
            self.registers[vIndex] = self.bus.read(self.i + deslocation)
            if self.modernMode:
                deslocation += 1
            else:
                self.i += 1

    def _getNN(self, thirdNibble, fourthNibble):
        return (thirdNibble << self._NIBBLE_BIT_DESLOCATION) + fourthNibble

    def _getNNN(self, secondNibble, thirdNibble, fourthNibble):
        return (secondNibble << (2 * self._NIBBLE_BIT_DESLOCATION)) + (thirdNibble << self._NIBBLE_BIT_DESLOCATION) + fourthNibble
    
    def _incrementPC(self):
        # Each institution has two bytes in memory, so the PC must be increased by 2
        INCREMENT_SIZE = 2
        self.pc += INCREMENT_SIZE

    def _updateDelay(self, valor):
        currentTime = perf_counter()
        self.delay = valor
        if self.buzzer == 0:
            self.lastUpdateTimerTime = currentTime

    def _updateBuzzer(self, valor):
        currentTime = perf_counter()
        self.buzzer = valor
        if self.delay == 0:
            self.lastUpdateTimerTime = currentTime