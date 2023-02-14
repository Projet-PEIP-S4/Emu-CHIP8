import traceback

import pygame

class DisplayManager:
    """
        Display manager control everything related to the display
    """

    instance: object | None = None

    @staticmethod
    def getInstance() -> object:
        """
            Static function to allow to be used as a singleton.
        """

        if DisplayManager.instance == None: DisplayManager.instance = DisplayManager()
        return DisplayManager.instance
    
    def __init__(self):
        self.reset()

        pygame.init()

        self.openDisplay()
        self.clear()
        self.update()

    def reset(self):
        self.height = 640
        self.width = 1280

        self.pixelHeight = 20
        self.pixelWidth = 20

        self.invert = False

        self.white = (255, 255, 255) if not self.invert else (0, 0, 0)
        self.black = (0, 0, 0) if not self.invert else (255, 255, 255)

    def openDisplay(self):
        self.display = pygame.display.set_mode((self.width, self.height))

    def clear(self):
        self.display.fill(self.white)

    def getPixel(self, x, y):
        pixel_color = self.display.get_at((x, y))

        if pixel_color[:3] == self.white: return 0
        else: return 1

    def drawPixel(self, gameX, gameY, colorMode):
        print(gameX)

        screenX = gameX * self.pixelWidth
        screenY = gameY * self.pixelHeight

        if screenX >= self.width: # Need to be tested
            screenX = screenX % self.width

        if screenY >= self.height: # Need to be tested
            screenY = screenY % self.height

        actPixel = self.getPixel(screenX, screenY)
        newColor = self.black if actPixel ^ int(colorMode) else self.white # XOR

        pygame.draw.rect(self.display, newColor, (screenX, screenY, self.pixelWidth, self.pixelHeight))

        if actPixel == 1 and newColor == self.white:
            return 1
        else: return 0

    def update(self):
        pygame.display.flip()