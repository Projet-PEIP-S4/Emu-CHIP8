import pygame

from utils.localDataManager import getGames

class Menu:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 640))
        self.font = pygame.font.SysFont("arialblack", 40)

        self.clearScreen()

        self.games = getGames()
        self.selectedGame = 0

    def drawText(self, text):
        renderedText = self.font.render(text, True, (0,0,0))
        renderedTextRect = renderedText.get_rect(center = (1280 / 2, 640 / 2))

        self.screen.blit(renderedText, (renderedTextRect))

    def clearScreen(self):
        self.screen.fill((255, 255, 255))

    def openLibrary(self):
        return self.loop()

    def loop(self):
        while True:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            self.clearScreen()
            self.drawText(self.games[self.selectedGame])

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.selectedGame == len(self.games) - 1:
                            self.selectedGame = 0
                        else :
                            self.selectedGame += 1

                    if event.key == pygame.K_RETURN:
                        return self.games[self.selectedGame]
                
            pygame.display.flip()