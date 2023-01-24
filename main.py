from utils.localDataManager import getGames, getGameFile

logging = True
def log(log: str) -> None:
    if logging:
        print(log)

class Mem:
    instance = None

    @staticmethod
    def getInstance():
        if Mem.instance == None: Mem.instance = Mem()
        return Mem.instance

    def __init__(self):
        log("New memory instance")
        self.test = "bnojour"

def main():
    print(getGames())

    Mem.getInstance()
    fileData = getGameFile("MISSILE")

main()