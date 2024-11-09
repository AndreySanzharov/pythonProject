from pygame.locals import *
from forinarow import *
from py2048 import DveTysyachiSorokVosyem
from tetris import Tetris
from tictactoe import *
import music

class Menu:
    def __init__(self):
        # Инициализация Pygame и параметров меню
        pygame.init()

        # Настройка часов для контроля FPS
        self.cl = pygame.time.Clock()
        # Шрифт для отображения текста
        self.font = pygame.font.SysFont("Comic Sans MS", 20)
        # Создание окна 400x500 пикселей
        self.screen = pygame.display.set_mode((400, 500), 0, 32)

        # Размер иконок игр
        self.size = 100, 100
        # Загрузка иконок для игр и изменение их размера
        self.ims = [pygame.transform.scale(pygame.image.load("icons/2048.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/tetris.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/4inarow.png"), self.size),
                    pygame.transform.scale(pygame.image.load("icons/tictactoe.png"), self.size)]
        # Позиции и размеры иконок на экране
        self.imrects = [(50, 100, 100, 100),
                        (50, 300, 100, 100),
                        (250, 100, 100, 100),
                        (250, 300, 100, 100)]

        # Определение областей кнопок для проверки кликов
        self.button_1 = pygame.Rect(self.imrects[0])
        self.button_2 = pygame.Rect(self.imrects[1])
        self.button_3 = pygame.Rect(self.imrects[2])
        self.button_4 = pygame.Rect(self.imrects[3])

        # Первоначальная отрисовка меню
        self.draw()
        # Флаг, указывающий, что игра запущена
        self.playing = False

    def draw(self):
        # Прорисовка основного меню
        pygame.display.set_caption("Main Menu")
        # Установка иконки окна
        programicon = pygame.image.load('icons/menu.png')
        pygame.display.set_icon(programicon)
        # Установка цвета фона экрана
        self.screen.fill(pygame.Color("lightblue"))
        # Отображение иконок игр на экране
        for im, rect in zip(self.ims, self.imrects):
            self.screen.blit(im, rect)

        # Вывод заголовка "GAMES:"
        self.draw_text('GAMES:', self.font, (255, 255, 255), self.screen, 20, 20)

    @staticmethod
    def draw_text(text, font, color, surface, x, y):
        # Вспомогательный метод для отображения текста на экране
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def main_menu(self):
        # Основной цикл меню
        click = False
        while True:
            # Если ни одна игра не запущена, отрисовать меню
            if not self.playing:
                self.draw()
            else:
                # Проверить файл, чтобы определить, завершилась ли игра
                with open("game_end.txt", "r+") as fil:
                    if fil.read():
                        self.playing = False

            # Получение координат мыши для проверки нажатий
            mx, my = pygame.mouse.get_pos()
            if click:
                # Проверка, нажата ли одна из кнопок с играми
                if self.button_1.collidepoint((mx, my)):
                    # Запуск игры 2048
                    g = DveTysyachiSorokVosyem(self.screen)
                    g.play()
                    self.playing = True
                elif self.button_2.collidepoint((mx, my)):
                    # Запуск игры Тетрис
                    g = Tetris(self.screen)
                    g.cycle()
                    self.playing = True
                elif self.button_3.collidepoint((mx, my)):
                    # Запуск игры 4 в ряд
                    g = FourInARow(6, 7)
                    g.start()
                    self.playing = True
                elif self.button_4.collidepoint((mx, my)):
                    # Запуск игры Крестики-нолики
                    g = TicTacToe(250, 20)
                    g.selection_mode()
                    g.update()
                    g.start()
                    self.playing = True

            # Сброс флага клика
            click = False
            # Обработка событий
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
                # Если музыка остановилась, перезапустить ее
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()

            # Обновление экрана
            pygame.display.update()
            # Ограничение частоты кадров (60 FPS)
            self.cl.tick(60)

if __name__ == '__main__':
    # Запуск музыки и меню
    music.play_music()
    m = Menu()
    m.main_menu()
