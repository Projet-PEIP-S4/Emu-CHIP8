import os

def getGames():
    """
        Return the name of all files in the 'games' folder.
    """

    os.chdir("games") # Change path
    dirFileNamesList = os.listdir() # Read all files names in current path

    return dirFileNamesList

def getGameFile(fileName):
    """
        Read game file content.
        
        - fileName: string, name of the file
    """

    file = open(fileName, "rb")
    fileContent = file.read()
    file.close()

    return fileContent