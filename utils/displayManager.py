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

        self.openDisplay()

    def reset(self):
        self.height = 640
        self.width = 1280

        self.pixelHeight = 20
        self.pixelWidth = 20

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

    def openDisplay(self):
        self.display = pygame.display.set_mode((self.width, self.height))

    def clear(self):
        self.display.fill(self.white)

    def drawPixel(self, x, y, colorMode):
        x = x * self.pixelWidth
        y = y * self.pixelHeight

        pygame.draw.rect(self.display, (self.black if (int(colorMode) == 1) else self.white), (x, y, self.pixelWidth, self.pixelHeight))

    def update(self):
        pygame.display.flip()