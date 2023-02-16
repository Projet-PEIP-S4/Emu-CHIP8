import pygame
from utils.localDataManager import getGames


def draw_text(screen,text, font, x, y):
  screen.fill((255,255,255))
  TEXT_COL = (0,0,0)
  img = font.render(text, True, TEXT_COL)
  screen.blit(img, (x, y))
  



def menu():
  pygame.init()
  screen = pygame.display.set_mode((1280,640))
  color = (255, 255, 255)
  screen.fill(color)

  run_menu = True
  games = getGames()
  current_game = games[0]
  font = pygame.font.SysFont("arialblack", 40)


  while run_menu: 
      events = pygame.event.get()
      keys = pygame.key.get_pressed()

      draw_text(screen,current_game,font,50,50)

      for event in events:
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            if games.index(current_game)+1 >= len(games):
              current_game = games[0]
            else :
              current_game = games[games.index(current_game)+1]

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            run_menu = False
            return current_game
          
      pygame.display.flip()
  

pygame.quit()