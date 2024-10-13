from pygame.locals import *

from forinarow import *
from py2048 import DveTysyachiSorokVosyem
from tetris import Tetris
from tictactoe import *
import music


class Menu:
    def __init__(self):
        # Инициализация класса
        pygame.init()

        self.cl = pygame.time.Clock()
        self.font = pygame.font.SysFont("Comic Sans MS", 20)
        self.screen = pygame.display.set_mode((400, 500), 0, 32)

        self.size = 100, 100
        self.ims = [pygame.transform.scale(pygame.image.load("icons/2048.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/tetris.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/4inarow.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/tictactoe.png"), self.size)]
        self.imrects = [(50, 100, 100, 100),
                        (50, 300, 100, 100),
                        (250, 100, 100, 100),
                        (250, 300, 100, 100)]

        self.button_1 = pygame.Rect(self.imrects[0])
        self.button_2 = pygame.Rect(self.imrects[1])
        self.button_3 = pygame.Rect(self.imrects[2])
        self.button_4 = pygame.Rect(self.imrects[3])

        self.draw()
        self.playing = False

    def draw(self):
        # Прорисовывание меню
        pygame.display.set_caption("Main Menu")
        programicon = pygame.image.load('icons/menu.png')
        pygame.display.set_icon(programicon)
        self.screen = pygame.display.set_mode((400, 500), 0, 32)
        self.screen.fill(pygame.Color("lightblue"))
        for im, rect in zip(self.ims, self.imrects):
            self.screen.blit(im, rect)

        self.draw_text('GAMES:', self.font, (255, 255, 255), self.screen, 20, 20)

    @staticmethod
    def draw_text(text, font, color, surface, x, y):
        # Прорисовывание текста
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def main_menu(self):
        # Игровой цикл
        click = False
        while True:
            if not self.playing:
                self.draw()
            else:
                with open("game_end.txt", "r+") as fil:
                    if fil.read():
                        self.playing = False

            # Проверка коллизии кнопки и мыши
            mx, my = pygame.mouse.get_pos()
            if click:
                if self.button_1.collidepoint((mx, my)):
                    g = DveTysyachiSorokVosyem(self.screen)
                    g.play()
                    self.playing = True
                elif self.button_2.collidepoint((mx, my)):
                    g = Tetris(self.screen)
                    g.cycle()
                    self.playing = True
                elif self.button_3.collidepoint((mx, my)):
                    g = FourInARow(6, 7)
                    g.start()
                    self.playing = True
                elif self.button_4.collidepoint((mx, my)):
                    g = TicTacToe(250, 20)
                    g.selection_mode()
                    g.update()
                    g.start()
                    self.playing = True

            click = False
            # Считывание событий с клавиатуры и мыши
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()

            pygame.display.update()
            self.cl.tick(60)


if __name__ == '__main__':
    # Запуск музыки и меню
    music.play_music()
    m = Menu()
    m.main_menu()
