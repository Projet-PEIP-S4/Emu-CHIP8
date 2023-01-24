from utils.localDataManager import getGames, getGameFile

def main():
    print(getGames())

    fileData = getGameFile("MISSILE")

main()