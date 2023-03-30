import time, random
import os, sys, traceback

# Disable pygame init print
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from utils.displayManager import DisplayManager
from utils.localDataManager import getGames, getGameFile

from menu import Menu

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
        self.reset()
        self.loadFonts()

    def reset(self) -> None:
        """
            Reset all variables to their default state.
        """

        self.mem = bytearray(4096) # Memory is composed of 4096 8-bit value
        self.dataOffset = 0x200 # A small part at the beginnig of the memory is reserved for fonts. Actual memory start at 0x200

        self.pc = self.dataOffset # Programm counter
        self.instructionCode = "" # Plain text code instruction, used for debuging
        self.incrementPC = True # Define whether or not the pc should be incremented

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

        self.registers = [0] * 16 # General purpose registers

        self.sp = 0 # Stack pointer
        self.stack = [0] * 16 # List of 16 8-bit adress

        self.i = 0 # General index register

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
            Emu.log("Memory overflow error.")

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

        Emu.log("Mem class instance:")
        for var in vars(self):
            if var == "mem" or var == "fonts" or var == "dataOffset": continue
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
        self.reset()

    def reset(self) -> None:
        """
            Reset all variables to their default state.
        """

        self.code = 0
        self.vx = 0
        self.vy = 0
        self.n = 0

        self.lookupTable = {
            0x0: self._0NNN,
            0x1: self._1NNN,
            0x2: self._2NNN,
            0x3: self._3XNN,
            0x4: self._4XNN,
            0x5: self._5XNN,
            0x6: self._6XNN,
            0x7: self._7XNN,
            0x8: self._8XYN,
            0x9: self._9XY0,
            0xA: self._ANNN,
            0xB: self._BNNN,
            0xC: self._CXNN,
            0xD: self._DXYN,
            0xE: self._EXNN,
            0xF: self._FXNN,
        }

        self.hTable = {
            0x0: self._8XY0,
            0x1: self._8XY1,
            0x2: self._8XY2,
            0x3: self._8XY3,
            0x4: self._8XY4,
            0x5: self._8XY5,
            0x6: self._8XY6,
            0x7: self._8XY7,
            0xE: self._8XYE,
        }

        self.fTable = {
            0x07: self._FX07,
            0x0A: self._FX0A,
            0x15: self._FX15,
            0x18: self._FX18,
            0x29: self._FX29,
            0x33: self._FX33,
            0x55: self._FX55,
            0x65: self._FX65,
            0x1E: self._FX1E,
        }

        self.keyTable = {
            0x1: pygame.K_1,
            0x2: pygame.K_2,
            0x3: pygame.K_3,
            0xc: pygame.K_4,

            0x4: pygame.K_a,
            0x5: pygame.K_z,
            0x6: pygame.K_e,
            0xd: pygame.K_r,

            0x7: pygame.K_q,
            0x8: pygame.K_s,
            0x9: pygame.K_d,
            0xe: pygame.K_f,

            0xa: pygame.K_w,
            0x0: pygame.K_x,
            0xb: pygame.K_c,
            0xf: pygame.K_v,
        }

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

    def _0NNN(self):
        if self.vy == 14 and self.n == 0:
            """
                Clear the display
            """

            DisplayManager.getInstance().clear()
            DisplayManager.getInstance().shouldUpdate = True

        elif self.vy == 14 and self.n == 14:
            """
                Exit subroutine
            """

            Mem.getInstance().sp -= 1
            Mem.getInstance().pc = Mem.getInstance().stack[Mem.getInstance().sp]

        else:
            a = "&" + 1

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
        Mem.getInstance().freezePC()
    
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

    def _5XNN(self):
        """
            if vx != vy then
        """

        if Mem.getInstance().registers[self.vx] == Mem.getInstance().registers[self.vy]:
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

    def _8XY1(self):
        """
            vx |= vy
        """

        Mem.getInstance().registers[self.vx] |= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY2(self):
        """
            vx &= vy
        """

        Mem.getInstance().registers[self.vx] &= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY3(self):
        """
            vx ^= vy
        """

        Mem.getInstance().registers[self.vx] ^= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY4(self):
        """
            vx += vy and vf = 1 on carry
        """

        if Mem.getInstance().registers[self.vx] + Mem.getInstance().registers[self.vy] > 0xFF:
            Mem.getInstance().registers[15] = 1
        else:
            Mem.getInstance().registers[15] = 0

        Mem.getInstance().registers[self.vx] += Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY5(self):
        """
            vx -= vy and vf = 0 on borrow
        """

        if Mem.getInstance().registers[self.vy] > Mem.getInstance().registers[self.vx]:
            Mem.getInstance().registers[15] = 0
        else:
            Mem.getInstance().registers[15] = 1

        Mem.getInstance().registers[self.vx] -= Mem.getInstance().registers[self.vy]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XY6(self):
        """
            vx >> 1, vf = old least significant bit
        """

        Mem.getInstance().registers[15] = Mem.getInstance().registers[self.vx] & 0x01
        Mem.getInstance().registers[self.vx] = Mem.getInstance().registers[self.vx] >> 1

    def _8XY7(self):
        """
            vx = vy - vx, vf = 0 on borrow
        """

        if Mem.getInstance().registers[self.vx] > Mem.getInstance().registers[self.vy]:
            Mem.getInstance().registers[15] = 0
        else:
            Mem.getInstance().registers[15] = 1

        Mem.getInstance().registers[self.vx] = Mem.getInstance().registers[self.vy] - Mem.getInstance().registers[self.vx]
        Mem.getInstance().registers[self.vx] &= 0xff

    def _8XYE(self):
        """
            vx << 1, vf = old most significant bit
        """

        Mem.getInstance().registers[15] = Mem.getInstance().registers[self.vx] >> 7
        Mem.getInstance().registers[self.vx] = Mem.getInstance().registers[self.vx] << 1
        Mem.getInstance().registers[self.vx] &= 0xFF

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

    def _BNNN(self):
        """
            jump0 NNN, Jump to address NNN + v0
        """

        Mem.getInstance().pc = (self.vx << 8) + (self.vy << 4) + self.n + Mem.getInstance().registers[0]
        Mem.getInstance().freezePC()

    def _CXNN(self):
        """
            Random number between 0 and 255 then XORed with NN then loaded into vx
        """

        rint = random.randint(0, 255)
        Mem.getInstance().registers[self.vx] = rint & ((self.vy << 4) + self.n)
        Mem.getInstance().registers[self.vx] &= 0xff

    def _DXYN(self):
        """
            Draw function
        """

        mem = Mem.getInstance()
        dm = DisplayManager.getInstance()

        dm.shouldUpdate = True

        xOffset = mem.registers[self.vx]
        yOffset = mem.registers[self.vy]

        mem.registers[15] = 0
        
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

            key = Mem.getInstance().registers[self.vx]

            if keys[self.keyTable[key]]:
                Mem.getInstance().pc += 2

        elif self.vy == 10:
            """
                if key is pressed then
            """

            key = Mem.getInstance().registers[self.vx]

            if keys[self.keyTable[key]] == False:
                Mem.getInstance().pc += 2

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

    def _FX0A(self):
        """
            Wait for a keypress 
        """

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        keyPressed = False

        for key in self.keyTable:
            if keys[self.keyTable[key]]:
                Mem.getInstance().registers[self.vx] = key
                keyPressed = True

        if keyPressed == False:
            Mem.getInstance().freezePC()

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

    def _FX55(self):
        """
            Save v0-vx to i through (i+x)
        """
        
        for j in range(0, self.vx + 1):
            Mem.getInstance().mem[Mem.getInstance().i + j] = Mem.getInstance().registers[j]

    def _FX65(self):
        """
            Load v0-vx from i through (i+x)
        """

        for j in range(0, self.vx + 1):
            Mem.getInstance().registers[j] = Mem.getInstance().mem[Mem.getInstance().i + j]

    def _FX1E(self):
        """
            i += vx
        """

        Mem.getInstance().i += Mem.getInstance().registers[self.vx]

        if Mem.getInstance().i > 0xfff:
            Mem.getInstance().registers[15] = 1
            Mem.getInstance().i &= 0xfff
        else:
            Mem.getInstance().registers[15] = 0
        
    def __str__(self) -> str:
        allVarsFormated: str = ""

        Emu.log("CPU class instance:")
        for var in vars(self):
            if var == "lookupTable" or var == "fTable" or var == "hTable" or var == "keyTable": continue
            allVarsFormated += "  -" + var + ": " + str(self.__dict__[var]) + "\n"

        return allVarsFormated

class Emu:
    instance: object | None = None

    @staticmethod
    def getInstance() -> object:
        """
            Static function to allow to be used as a singleton.
        """

        if Emu.instance == None: Emu.instance = Emu()
        return Emu.instance

    def __init__(self):
        self.reset()

        self.mem = Mem.getInstance() # Init Mem class
        self.cpu = CPU.getInstance() # Init CPU class
        self.dm = DisplayManager().getInstance() # Init the display class

    @staticmethod
    def log(log: str) -> None:
        """
            Wrapper around the print function to control console logging.
        """

        if Emu.getInstance().logging == True:
            print(log)

    def reset(self):
        self.logging = False # Set to True to enable logging message into console
        self.gameData = False
        self.gameOn = False

    def setRom(self, rom):
        self.gameData = rom

    def play(self):
        if self.gameData == False:
            print("No game ROM has been provided")
            return

        self.mem.fillMemory(self.gameData)

        self.dm.invertColors()
        self.dm.openDisplay()

        self.timer = pygame.time.Clock()

        self.gameOn = True

        try: # Enable global error handling
            self.loop()
        except Exception: # If an error occur print: the error code, the Mem vars content and the CPU vars content
            self.log("\n" + traceback.format_exc())

            self.log(Mem.getInstance())
            self.log(CPU.getInstance())

    def loop(self):
        i = 0
        while self.gameOn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameOn = False

                    pygame.quit()
                    break

            # Get the current instruction to execute
            instruction = self.mem.getCurrentInstruction()

            # Tell the CPU to decode the instruction
            self.cpu.decode(instruction)
            
            # Execute the instruction
            self.cpu.exec()

            # Increment the pc if needed
            self.mem.updatePC()

            # Update the screen
            self.dm.update()

            if i == 9: # Timers decrement at 60hz, 540 / 9 = 60
                self.mem.decrementTimers()
                i = 0

            i += 1
            self.timer.tick(540)

def printHowToUse():
    print("Emu-CHIP8\n")

    print("How to use:")
    print("- no arg --> use the library to select your game")
    print("- 'game name' --> bypass the menu and jump directly to the game")
    print("- list --> list all available games")

    print("\n- help --> acces this menu")

def printListGames():
    games = getGames()

    print("All available games are listed below:")
    for game in games:
        print("-", game)

def main():
    emu = Emu.getInstance()

    if len(sys.argv) == 2:
        firstParam = sys.argv[1]

        if firstParam == "help":
            printHowToUse()
        elif firstParam == "list":
            printListGames()
        elif firstParam in getGames():
            gameRom = getGameFile(firstParam)

            emu.setRom(gameRom)
            emu.play()
        else:
            print("Game does not exist !")
    elif len(sys.argv) > 2:
        printHowToUse()
    else:
        gameName = Menu().openLibrary()

        if gameName == False:
            print("Bye")
        else:
            emu.setRom(getGameFile(gameName))
            emu.play()

main()