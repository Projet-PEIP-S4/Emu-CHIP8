from utils.localDataManager import getGames, getGameFile

logging: bool = True
def log(log: str) -> None:
    if logging:
        print(log)

class Mem:
    instance: object | None = None

    @staticmethod
    def getInstance() -> object:
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
            binArray = list(str(bin(gameData[i]))[2:])
            self.mem[i * 8 : i * 8 + len(binArray)] = binArray

            i += 1

        self.mem = [int(x) for x in self.mem]

    def __str__(self):
        allVarsFormated: str = ""

        print("\nMem class instance:")
        for var in vars(self):
            allVarsFormated += "  -" + var + ": " + "???" + "\n"

        return allVarsFormated

def main():
    fileData = getGameFile("MISSILE")

    Mem.getInstance().fillMemory(fileData)

main()