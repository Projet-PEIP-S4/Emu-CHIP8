import traceback
import time
import random
import os

# Disable pygame print
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

from utils.localDataManager import getGames, getGameFile
from utils.displayManager import DisplayManager

gameOn: bool = True # Control wether the game is running or not
logging: bool = True # Set to True to enable logging message into console

def log(log: str) -> None:
    """
        Wrapper around the print function to control console logging.
    """

    if logging:
        print(log)

class Mem:
    """
        Mem class will hold all the variables and functions related to memory management.
    """

    instance: object | None = None

    @staticmethod
    def getInstance() -> object:
        """
            Static function to allow to be used as a singleton.
        """

        if Mem.instance == None: Mem.instance = Mem()
        return Mem.instance

    def __init__(self):
        log("New memory instance")
        
        self.reset()

    def reset(self) -> None:
        """
            Reset all variables to their default state.
        """

        self.mem = bytearray(4096)
        self.dataOffset = 0x200

        self.fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        self.loadFonts()

        self.registers = [0] * 16 # Genral purpose registers
        self.stack = [0] * 16
        self.pc = self.dataOffset # Programm counter
        self.sp = 0 # Stack pointer
        self.i = 0 # Draw offset register

        self.instructionCode = ""
        self.incrementPC = True

        self.st = 0 # Sound timer register
        self.dt = 0 # Delay timer register

    def loadFonts(self):
        """
            Load fonts into memory starting at 0x0
        """

        for index, value in enumerate(self.fonts):
            self.mem[index] = value

    def fillMemory(self, gameData: str) -> None:
        """
            Fill the game memory with gameData content.

            gameData: string of hex numbers
        """

        try:
            for index, value in enumerate(gameData):
                self.mem[index + self.dataOffset] = value
        except Exception as e:
            print("Memory overflow error.")

    def freezePC(self):
        self.incrementPC = False

    def updatePC(self):
        if self.incrementPC:
            self.pc += 2

        self.incrementPC = True

    def decrementTimers(self):
        if self.st > 0:
            self.st -= 1

        if self.dt > 0:
            self.dt -= 1

    def getpointedMemory(self, offset = 0):
        return self.mem[self.pc + offset]

    def getValuesAt(self, address):
        return self.mem[address]

    def getCurrentInstruction(self):
        instruction = (self.getpointedMemory() << 8) + self.getpointedMemory(1)
        self.instructionCode = hex(instruction)

        return instruction

    def __str__(self):
        allVarsFormated: str = ""

        log("Mem class instance:")
        for var in vars(self):
            if var == "mem": continue
            allVarsFormated += "  -" + var + ": " + str(self.__dict__[var]) + "\n"

        return allVarsFormated

class CPU:
    instance: object | None = None

    @staticmethod
    def getInstance() -> object:
        """
            Static function to allow to be used as a singleton.
        """

        if CPU.instance == None: CPU.instance = CPU()
        return CPU.instance

    def __init__(self) -> None:
        log("New CPU instance")

        self.lookupTable = {
            0x0: self._00NN,
            0x1: self._1NNN,
            0x2: self._2NNN,
            0x3: self._3XNN,
            0x4: self._4XNN,
            0x6: self._6XNN,
            0x7: self._7XNN,
            0x8: self._8XYN,
            0x9: self._9XY0,
            0xA: self._ANNN,
            0xC: self._CXNN,
            0xD: self._DXYN,
            0xE: self._EXNN,
            0xF: self._FXNN,
        }

        self.hTable = {
            0x0: self._8XY0,
            0x2: self._8XY2,
            0x4: self._8XY4,
            0x5: self._8XY5,
        }

        self.fTable = {
            0x07: self._FX07,
            0x15: self._FX15,
            0x18: self._FX18,
            0x29: self._FX29,
            0x33: self._FX33,
            0x65: self._FX65,
            0x1E: self._FX1E,
        }

        self.keyTable = {
            0x0: pygame.K_a,
            0x1: pygame.K_z,
            0x2: pygame.K_e,
            0x3: pygame.K_r,
        }

        self.reset()

    def reset(self) -> None:
        """
            Reset all variables to their default state.
        """

        self.code = 0
        self.vx = 0
        self.vy = 0
        self.n = 0

    def decode(self, instruction : int):
        """
            Break down the instruction to analyse it later,
        """

        self.code = (instruction & 0xf000) >> 12
        self.vx = (instruction & 0x0f00) >> 8
        self.vy = (instruction & 0x00f0) >> 4
        self.n = instruction & 0x000f

    def exec(self):
        self.lookupTable[self.code]()

    def _00NN(self):
        if self.n == 0:
            a = "&" + 1

        if self.n == 14:
            Mem.getInstance().sp -= 1
            Mem.getInstance().pc = Mem.getInstance().stack[Mem.getInstance().sp]
            Mem.getInstance().stack[Mem.getInstance().sp] = 0

    def _1NNN(self):
        """
            Jump to NNN
        """

        Mem.getInstance().pc = (self.vx << 8) + (self.vy << 4) + self.n
        Mem.getInstance().freezePC()

    def _2NNN(self):
        """
            Call subroutine
        """

        Mem.getInstance().stack[Mem.getInstance().sp] = Mem.getInstance().pc
        Mem.getInstance().sp += 1
        Mem.getInstance().pc = (self.vx << 8) + (self.vy << 4) + self.n
    
    def _3XNN(self):
        """
            if vx != NN then
        """

        if Mem.getInstance().registers[self.vx] == (self.vy << 4) + self.n:
            Mem.getInstance().pc += 2 
    
    def _4XNN(self):
        """
            if vx == NN then
        """

        if Mem.getInstance().registers[self.vx] != (self.vy << 4) + self.n:
            Mem.getInstance().pc += 2

    def _6XNN(self):
        """
            vx := NN
        """

        Mem.getInstance().registers[self.vx] = (self.vy << 4) + self.n

    def _7XNN(self):
        """
            vx += NN
        """

        Mem.getInstance().registers[self.vx] += (self.vy << 4) + self.n

        if Mem.getInstance().registers[self.vx] > 0xFF:
            Mem.getInstance().registers[self.vx] -= 0x100

    def _8XYN(self):
        """
            Instruction type 8 
        """

        self.hTable[self.n]()

    def _8XY0(self):
        """
            vx := vy
        """

        Mem.getInstance().registers[self.vx] = Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY2(self):
        """
            vx &= vy
        """

        Mem.getInstance().registers[self.vx] &= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY4(self):
        """
            vx += vy and vf = 1 on carry
        """

        Mem.getInstance().registers[15] = 0

        if Mem.getInstance().registers[self.vx] + Mem.getInstance().registers[self.vy] > 0xff:
            Mem.getInstance().registers[15] = 1

        Mem.getInstance().registers[self.vx] += Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY5(self):
        """
            vx -= vy and vf = 0 on borrow
        """

        Mem.getInstance().registers[15] = 1

        if Mem.getInstance().registers[self.vx] < Mem.getInstance().registers[self.vy]:
            Mem.getInstance().registers[15] = 0

        Mem.getInstance().registers[self.vx] -= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _9XY0(self):
        """
            If vx == vy then
        """

        if Mem.getInstance().registers[self.vx] != Mem.getInstance().registers[self.vy]:
            Mem.getInstance().pc += 2

    def _ANNN(self):
        """
            i := NNN
        """

        Mem.getInstance().i = (self.vx << 8) + (self.vy << 4) + self.n
        Mem.getInstance().i &= 0xfff

    def _CXNN(self):
        """
            Random number between 0 and 255 loaded into vx
        """

        rint = random.randint(0, 255)
        Mem.getInstance().registers[self.vx] = rint & ((self.vy << 4) + self.n)
        Mem.getInstance().registers[self.vx] &= 0xff

    def _DXYN(self):
        mem = Mem.getInstance()
        dm = DisplayManager.getInstance()

        xOffset = mem.registers[self.vx]
        yOffset = mem.registers[self.vy]

        mem.registers[15] = 0 # Reset last register

        for n in range(0, self.n):
            binString = format(mem.getValuesAt(mem.i + n), "08b")
            for i in range(0, 8):
                result = dm.drawPixel(xOffset + i, yOffset + n, binString[i])

                if result == 1:
                    mem.registers[15] = 1

    def _EXNN(self):
        """
            Related to key event
        """

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        if self.vy == 9:
            """
                if key not pressed then
            """

            if keys[self.keyTable[self.vx]]:
                Mem.getInstance().pc += 2

        if self.vy == 11:
            a = "&" + 1

    def _FXNN(self):
        """
            Instruction type F
        """

        self.fTable[(self.vy << 4) + self.n]()

    def _FX07(self):
        """
            vx := delay
        """

        Mem.getInstance().registers[self.vx] = Mem.getInstance().dt

    def _FX15(self):
        """
            delay := vx
        """

        Mem.getInstance().dt = Mem.getInstance().registers[self.vx]

    def _FX18(self):
        """
            Buzzer
        """

        Mem.getInstance().st = Mem.getInstance().registers[self.vx]

    def _FX29(self):
        """
            Set i to the start location of the fonts for vx
        """

        Mem.getInstance().i = Mem.getInstance().registers[self.vx] * 5

    def _FX33(self):
        """
            Decode vx into binary-coded decimal
        """

        mem = Mem.getInstance()
        vx = Mem.getInstance().registers[self.vx]

        mem.mem[mem.i] = vx // 100
        mem.mem[mem.i +1] = (vx % 100) // 10
        mem.mem[mem.i +2] = vx % 10

    def _FX65(self):
        """
            Load v0-vx from i through (i+x)
        """

        for j in range(self.vx + 1):
            Mem.getInstance().registers[j] = Mem.getInstance().mem[Mem.getInstance().i + j]

        Mem.getInstance().i += self.vx + 1

    def _FX1E(self):
        """
            i += vx
        """

        Mem.getInstance().i += Mem.getInstance().registers[self.vx]
        Mem.getInstance().registers[15] = 0

        if Mem.getInstance().i > 0xfff:
            Mem.getInstance().registers[15] = 1
            Mem.getInstance().i &= 0xfff
        
    def __str__(self) -> str:
        allVarsFormated: str = ""

        log("CPU class instance:")
        for var in vars(self):
            if var == "lookupTable" or var == "fTable" or var == "hTable": continue
            allVarsFormated += "  -" + var + ": " + str(self.__dict__[var]) + "\n"

        return allVarsFormated

def loop():
    global gameOn

    mem = Mem.getInstance()
    cpu = CPU.getInstance()
    dm = DisplayManager().getInstance()

    timer = pygame.time.Clock()

    while gameOn:
        # Get the current instruction to execute
        instruction = mem.getCurrentInstruction()

        # Tell the CPU to decode the instruction
        cpu.decode(instruction)
        
        # Execute the instruction
        cpu.exec()

        # Increment the pc if needed
        mem.updatePC()

        # Update the screen
        dm.update()

        # log(mem.instructionCode)

        mem.decrementTimers()
        timer.tick(500)

def main():
    fileData = getGameFile("TETRIS")
    
    Mem.getInstance().fillMemory(fileData)
    CPU.getInstance() # Init CPU class

    display = DisplayManager.getInstance() # Init display

    loop()

try: # Enable global error handling
    main()
except Exception: # If an error occur print the error code, the Mem singleton vars content and the CPU vars content
    print("\n" + traceback.format_exc())

    log(Mem.getInstance())
    log(CPU.getInstance())