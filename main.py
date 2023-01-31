from utils.localDataManager import getGames, getGameFile
from utils.utils import Utils

logging: bool = True

def log(log: str) -> None:
    if logging:
        print(log)

class Mem:
    instance: object | None = None

    @staticmethod
    def getInstanceMem() -> object:
        if Mem.instance == None: Mem.instance = Mem()
        return Mem.instance

    def __init__(self):
        log("New memory instance")
        
        self.reset()

    def reset(self) -> None:
        self.mem = [0] * 4096

        self.registers = [0] * 16 # Genral purpose registers
        self.pc = 0 # Programm counter
        self.st = 0 # Sound timer register
        self.dt = 0 # Delay timer register
        self.i = 0 # Draw offset registrer

    def fillMemory(self, gameData: str) -> None:
        i = 0
        while i < len(gameData):
            binArray = list(str(bin(gameData[i])))
            self.mem[i * 8 + 8 - len(binArray) : i * 8 + 8 ] = binArray

            i += 1

        self.mem = [int(x) for x in self.mem]

    def __str__(self):
        allVarsFormated: str = ""

        print("\nMem class instance:")
        for var in vars(self):
            allVarsFormated += "  -" + var + ": " + "???" + "\n"

        return allVarsFormated

class CPU:
    instance: object | None = None
    #print(CPU) à configurer 
    @staticmethod
    def getInstanceCPU() -> object:
        if CPU.instance == None: CPU.instance = CPU()
        return CPU.instance

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.code = 0
        self.vx = 0
        self.vy = 0
        self.n = 0
    
    def __str__(self) -> str:
        return f"code : {self.code}, vx : {self.vx}, vy : {self.vy}, n : {self.n}"

    def decode(self,instruction : int ):
        self.code = (instruction & 0xf000) >> 12
        self.vx = (instruction & 0x0f00) >> 8
        self.vy = (instruction & 0x00f0) >> 4
        self.n = (instruction & 0x000f) 
        
def loop():
    gameOn = True
    while gameOn: 
        #récupère l'instruction à effectuer
        pc = Mem.getInstanceMem().pc
        instructionArray = Mem.getInstanceMem().mem[pc : pc + 16]
        instruction =  Utils.convertBinArrayToHexStr(instructionArray[0:8])[2:] + Utils.convertBinArrayToHexStr(instructionArray[8:16])[2:]
        print(instruction)
        #execution la commande
        CPU.getInstanceCPU().decode(int(instruction))
        gameOn = False
        print(CPU.getInstanceCPU())
        
        #incrémente le pc


def main():
    fileData = getGameFile("MISSILE")
    Mem.getInstanceMem().fillMemory(fileData)
    loop()

main()