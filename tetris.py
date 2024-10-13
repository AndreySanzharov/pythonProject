from copy import deepcopy
from random import choice
from random import randrange

import pygame

import music

class Tetris:
    @staticmethod
    def get_record():
        # Взять рекорд из файла
        with open('tetris/hscore_tetris') as fil:
            return fil.readline()

    @staticmethod
    def set_record(record, score):
        # Положить рекорд в файл
        if int(record) < score:
            with open('tetris/hscore_tetris', 'w') as f:
                f.write(str(score))

    @staticmethod
    def get_next_color():
        # Цвет следующей фигуры
        return randrange(30, 256), randrange(30, 256), randrange(30, 256)

    def __init__(self, menu_sc):
        # Инициализация класса
        self.menu_sc = menu_sc
        pygame.init()

        self.running = True
        self.W, self.H = 10, 20
        self.TILE = 45
        self.GAME_RES = self.W * self.TILE, self.H * self.TILE
        self.RES = 750, 940
        self.FPS = 60

        self.screen = pygame.display.set_mode(self.RES)
        self.game_sc = pygame.Surface(self.GAME_RES)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tetris")
        programicon = pygame.image.load('icons/tetris.png')
        pygame.display.set_icon(programicon)

        self.grid = [pygame.Rect(x * self.TILE, y * self.TILE, self.TILE, self.TILE)
                     for x in range(self.W) for y in range(self.H)]

        figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                       [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                       [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                       [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[pygame.Rect(x + self.W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]

        self.figure_rect = pygame.Rect(0, 0, self.TILE - 2, self.TILE - 2)
        self.field = [[0 for __ in range(self.W)] for _ in range(self.H)]

        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000

        self.game_bg = pygame.image.load("tetris/img/bg.png").convert()

        main_font = pygame.font.SysFont("Comic Sans MS", 65)
        self.font = pygame.font.SysFont("Comic Sans MS", 45)

        self.title_tetris = main_font.render("TETRIS", True, pygame.Color("darkorange"))
        self.title_score = self.font.render("Score:", True, pygame.Color("green"))
        self.title_record = self.font.render("Hscore:", True, pygame.Color("purple"))

        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_next_color(), self.get_next_color()

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def collision_check(self, item):
        if self.figure[item].x < 0 or self.figure[item].x > self.W - 1 or \
                self.figure[item].y > self.H - 1 or self.field[self.figure[item].y][self.figure[item].x]:
            return False
        return True

    def cycle(self):
        # Игровой цикл
        while self.running:
            record = self.get_record()
            dx, rotate = 0, False

            self.draw(record)

            for i in range(self.lines):
                pygame.time.wait(200)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.screen = self.menu_sc
                    with open("game_end.txt", "w+") as fil:
                        fil.write("1")
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        dx = -1
                    if event.key == pygame.K_RIGHT:
                        dx = 1
                    if event.key == pygame.K_DOWN:
                        self.anim_limit = 100
                    if event.key == pygame.K_UP:
                        rotate = True
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.screen = self.menu_sc
                        with open("game_end.txt", "w+") as fil:
                            fil.write("1")
                        break
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()
            if not self.running:
                break

            figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].x += dx
                if not self.collision_check(i):
                    self.figure = deepcopy(figure_old)
                    break

            # ускорение фигуры
            self.anim_count += self.anim_speed
            if self.anim_count > self.anim_limit:
                self.anim_count = 0
                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i].y += 1
                    if not self.collision_check(i):
                        for j in range(4):
                            self.field[figure_old[j].y][figure_old[j].x] = self.color
                        self.figure, self.color = self.next_figure, self.next_color
                        self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_next_color()
                        self.anim_limit = 2000
                        break

            # поворот фигуры
            center = self.figure[0]
            figure_old = deepcopy(self.figure)
            if rotate:
                for i in range(4):
                    x = self.figure[i].y - center.y
                    y = self.figure[i].x - center.x
                    self.figure[i].x = center.x - x
                    self.figure[i].y = center.y + y
                    if not self.collision_check(i):
                        self.figure = deepcopy(figure_old)
                        break

            # проверить на наличие полных рядов
            line, lines = self.H - 1, 0
            for row in range(self.H - 1, -1, -1):
                count = 0
                for i in range(self.W):
                    if self.field[row][i]:
                        count += 1
                    self.field[line][i] = self.field[row][i]
                if count < self.W:
                    line -= 1
                else:
                    self.anim_speed += 3
                    lines += 1
            self.score += self.scores[lines]

            self.gameover(record)

            pygame.display.flip()
            self.clock.tick(self.FPS)

    def gameover(self, record):
        # конец игры
        for i in range(self.W):
            if self.field[0][i]:
                self.set_record(record, self.score)
                self.field = [[0 for __ in range(self.W)] for _ in range(self.H)]
                self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
                self.score = 0
                for i_rect in self.grid:
                    pygame.draw.rect(self.game_sc, self.get_next_color(), i_rect)
                    self.screen.blit(self.game_sc, (20, 20))
                    pygame.display.flip()
                    self.clock.tick(200)

    def draw(self, record):
        # Прорисовывание игры
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_sc, (20, 20))
        self.game_sc.blit(self.game_bg, (0, 0))
        # прорисовывание игрового поля
        [pygame.draw.rect(self.game_sc, (40, 40, 40), i_rect, 1) for i_rect in self.grid]
        # прорисовывание фигур
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * self.TILE
            self.figure_rect.y = self.figure[i].y * self.TILE
            pygame.draw.rect(self.game_sc, self.color, self.figure_rect)

        # прорисовывание поля
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * self.TILE, y * self.TILE
                    pygame.draw.rect(self.game_sc, col, self.figure_rect)

        # прорисовывание следующей фигуры
        for i in range(4):
            self.figure_rect.x = self.next_figure[i].x * self.TILE + 380
            self.figure_rect.y = self.next_figure[i].y * self.TILE + 185
            pygame.draw.rect(self.screen, self.next_color, self.figure_rect)

        # прорисовывание очков
        self.screen.blit(self.title_tetris, (485, -10))
        self.screen.blit(self.title_score, (535, 780))
        self.screen.blit(self.font.render(str(self.score), True, pygame.Color("white")), (550, 840))
        self.screen.blit(self.title_record, (525, 650))
        self.screen.blit(self.font.render(record, True, pygame.Color("gold")), (550, 710))
