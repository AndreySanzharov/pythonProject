import numpy as np
import random
import pygame
from pygame.locals import *

ColorPalette = {
    0: (204, 192, 179),
    2: (238, 228, 219),
    4: (240, 226, 202),
    8: (242, 177, 121),
    16: (236, 141, 85),
    32: (250, 123, 92),
    64: (234, 90, 56),
    128: (237, 207, 114),
    256: (242, 208, 75),
    512: (237, 200, 80),
    1024: (227, 186, 19),
    2048: (236, 196, 2),
    4096: (96, 217, 146),
    8192: (56, 90, 135),
    16384: (160, 130, 146),
    32768: (120, 140, 155),
    65536: (112, 124, 200),
    131072: (70, 110, 255)
}


class DveTysyachiSorokVosyem:
    def __init__(self, menu_sc):
        # Инициализация класса
        self.menu_sc = menu_sc
        self.num = 4
        if self.num < 2:
            self.num = 2
        self.grid = np.zeros((self.num, self.num), dtype=int)

        self.sz = self.num * 100
        self.SPACING = 10
        self.running = True
        self.fl = True

        pygame.init()
        pygame.display.set_caption("2048")
        programicon = pygame.image.load('icons/2048.png')
        pygame.display.set_icon(programicon)

        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)

        self.screen = pygame.display.set_mode((self.sz, self.sz))

    @staticmethod
    def get_next_num(this):
        # Берет число
        this_n = this[this != 0]
        this_n_sum = []
        skip = False
        for j in range(len(this_n)):
            if not skip:
                if j != len(this_n) - 1 and this_n[j] == this_n[j + 1]:
                    new_n = this_n[j] * 2
                    skip = True
                else:
                    new_n = this_n[j]

                this_n_sum.append(new_n)
            else:
                skip = False
        return np.array(this_n_sum)

    def __str__(self):
        return str(self.grid)

    def gen_num(self, k=1):
        # Берет число
        if k < 1:
            k = 1
        elif k > self.num * self.num:
            k = self.num
        free_poss = list(zip(*np.where(self.grid == 0)))
        for pos in random.sample(free_poss, k):
            self.grid[pos] = 0
            if random.random() < 0.1:
                self.grid[pos] = 4
            else:
                self.grid[pos] = 2

    def make_move(self, move):
        # Делает ход
        for i in range(self.num):
            if move in 'lr':
                this = self.grid[i, :]
            else:
                this = self.grid[:, i]

            flipped = False
            if move in 'rd':
                flipped = True
                this = this[::-1]

            this_n = self.get_next_num(this)

            new_this = np.zeros_like(this)
            new_this[:len(this_n)] = this_n

            if flipped:
                new_this = new_this[::-1]

            if move in 'lr':
                self.grid[i, :] = new_this
            else:
                self.grid[:, i] = new_this

    def draw(self):
        # Прорисовывание игры
        self.screen.fill((189, 172, 161))

        for i in range(self.num):
            for j in range(self.num):
                n = self.grid[i][j]
                rect_x = j * self.sz // self.num + self.SPACING
                rect_y = i * self.sz // self.num + self.SPACING
                rect_w = self.sz // self.num - 2 * self.SPACING
                rect_h = self.sz // self.num - 2 * self.SPACING

                pygame.draw.rect(self.screen,
                                 ColorPalette[n],
                                 pygame.Rect(rect_x, rect_y, rect_w, rect_h),
                                 border_radius=5)
                if n:
                    text_surface = self.myfont.render(str(n), True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(rect_x + rect_w / 2,
                                                              rect_y + rect_h / 2))
                    self.screen.blit(text_surface, text_rect)

    def is_game_over(self):
        # Проверка на наличие ходов
        grid_bu = self.grid.copy()
        for move in 'lrud':
            self.make_move(move)
            if not all((self.grid == grid_bu).flatten()):
                self.grid = grid_bu
                return False
        return True

    def wait_for_key(self):
        # Считывание событий с клавиатуры
        while True:
            if self.is_game_over():
                self.fl = False
                print('GAME OVER!')
                break
            for event in pygame.event.get():
                if event.type == QUIT:
                    return 'q'
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        return 'u'
                    elif event.key == K_RIGHT:
                        return 'r'
                    elif event.key == K_LEFT:
                        return 'l'
                    elif event.key == K_DOWN:
                        return 'd'
                    elif event.key == K_q or event.key == K_ESCAPE:
                        return 'q'

    def play(self):
        # Игровой цикл
        self.gen_num(2)

        while True:
            self.draw()
            pygame.display.flip()
            cmd = self.wait_for_key()
            if not self.fl:
                break
            if cmd == 'q':
                self.screen = self.menu_sc
                break

            old_grid = self.grid.copy()
            self.make_move(cmd)

            if not all((self.grid == old_grid).flatten()):
                self.gen_num()

        with open("game_end.txt", "w") as fil:
            fil.write("1")
