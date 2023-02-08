import traceback

from utils.localDataManager import getGames, getGameFile
from utils.utils import Utils

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

        self.registers = [0] * 16 # Genral purpose registers
        self.pc = self.dataOffset # Programm counter
        self.sp = 0 # Stack pointer
        self.i = 0 # Draw offset registrer

        self.st = 0 # Sound timer register
        self.dt = 0 # Delay timer register

    def fillMemory(self, gameData: str) -> None:
        

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
            0x1: self._1NNN,
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

    def _1NNN(self):
        """
            Jump to NNN
        """

        Mem.getInstance().pc = (self.vx << 8) + (self.vy << 4) + self.n

    def __str__(self) -> str:
        allVarsFormated: str = ""

        log("CPU class instance:")
        for var in vars(self):
            allVarsFormated += "  -" + var + ": " + str(self.__dict__[var]) + "\n"

        return allVarsFormated

def loop():
    global gameOn

    mem = Mem.getInstance()
    cpu = CPU.getInstance()

    while gameOn: 
        # Get the current instruction to execute
        instruction = (mem.mem[mem.pc] << 8) + mem.mem[mem.pc + 1]
        log(hex(instruction))

        # Tell the CPU to decode the instruction
        cpu.decode(instruction)
        
        # Execute the instruction
        cpu.exec()

def main():
    fileData = getGameFile("MISSILE")
    
    Mem.getInstance().fillMemory(fileData)
    CPU.getInstance()

    loop()

try: # Enable global error handling
    main()
except Exception: # If an error occur print the error code, the Mem singleton vars content and the CPU vars content
    print("\n" + traceback.format_exc())

    log(Mem.getInstance())
    log(CPU.getInstance())