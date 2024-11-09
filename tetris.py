from copy import deepcopy
from random import choice
from random import randrange

import pygame

import music


class Tetris:
    @staticmethod
    def get_record():
        """
        Метод для получения текущего рекорда из файла.
        Возвращает строку, содержащую наибольшее количество очков.
        """
        with open('tetris/hscore_tetris') as fil:
            return fil.readline()

    @staticmethod
    def set_record(record, score):
        """
        Метод для установки нового рекорда, если текущий score больше сохраненного рекорда.
        Записывает новый рекорд в файл.
        """
        if int(record) < score:
            with open('tetris/hscore_tetris', 'w') as f:
                f.write(str(score))

    @staticmethod
    def get_next_color():
        """
        Генерирует случайный цвет для следующей фигуры.
        Возвращает кортеж с тремя значениями (R, G, B).
        """
        return randrange(30, 256), randrange(30, 256), randrange(30, 256)

    def __init__(self, menu_sc):
        """
        Конструктор, инициализирующий все необходимые параметры для игры.
        Создает окно игры, настраивает начальные параметры и фигуры.
        """
        self.menu_sc = menu_sc
        pygame.init()

        self.running = True  # Флаг, указывающий, работает ли игра
        self.W, self.H = 10, 20  # Размеры игрового поля
        self.TILE = 45  # Размер одного квадрата на поле
        self.GAME_RES = self.W * self.TILE, self.H * self.TILE  # Размер игрового экрана
        self.RES = 750, 940  # Общий размер окна
        self.FPS = 60  # Частота кадров в игре

        # Настройка игрового экрана
        self.screen = pygame.display.set_mode(self.RES)
        self.game_sc = pygame.Surface(self.GAME_RES)  # Поверхность для игры
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tetris")  # Название окна
        programicon = pygame.image.load('icons/tetris.png')  # Иконка программы
        pygame.display.set_icon(programicon)

        # Сетка для отображения игрового поля
        self.grid = [pygame.Rect(x * self.TILE, y * self.TILE, self.TILE, self.TILE)
                     for x in range(self.W) for y in range(self.H)]

        # Возможные формы фигур в Tetris
        figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                       [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                       [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                       [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, -1)],
                       [(0, 0), (0, -1), (0, 1), (1, -1)],
                       [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        # Перевод позиций в прямоугольники для фигуры
        self.figures = [[pygame.Rect(x + self.W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]

        # Прямоугольник для фигуры
        self.figure_rect = pygame.Rect(0, 0, self.TILE - 2, self.TILE - 2)

        # Игровое поле: двумерный массив для отслеживания занятых клеток
        self.field = [[0 for __ in range(self.W)] for _ in range(self.H)]

        # Настройки анимации (скорость падения фигур)
        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000

        # Фон для игры
        self.game_bg = pygame.image.load("tetris/img/bg.png").convert()

        # Шрифты для текста
        main_font = pygame.font.SysFont("Comic Sans MS", 65)
        self.font = pygame.font.SysFont("Comic Sans MS", 45)

        # Заголовки для игры (название и счет)
        self.title_tetris = main_font.render("TETRIS", True, pygame.Color("darkorange"))
        self.title_score = self.font.render("Score:", True, pygame.Color("green"))
        self.title_record = self.font.render("Hscore:", True, pygame.Color("purple"))

        # Инициализация текущей и следующей фигуры
        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_next_color(), self.get_next_color()

        # Начальные значения очков и линий
        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def collision_check(self, item):
        """
        Метод для проверки, не столкнулась ли фигура с границами поля или другими фигурами.
        Возвращает False, если есть столкновение, и True, если нет.
        """
        if self.figure[item].x < 0 or self.figure[item].x > self.W - 1 or \
                self.figure[item].y > self.H - 1 or self.field[self.figure[item].y][self.figure[item].x]:
            return False
        return True

    def cycle(self):
        """
        Основной игровой цикл. Отвечает за обработку событий, обновление состояния игры
        и отрисовку элементов на экране.
        """
        while self.running:
            # Получаем текущий рекорд
            record = self.get_record()
            dx, rotate = 0, False  # Перемещение и вращение фигуры

            # Отрисовываем игру
            self.draw(record)

            # Ожидаем событий, таких как нажатие клавиш
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Закрытие игры
                    self.running = False
                    self.screen = self.menu_sc
                    with open("game_end.txt", "w+") as fil:
                        fil.write("1")
                    break
                if event.type == pygame.KEYDOWN:
                    # Обработка нажатий клавиш
                    if event.key == pygame.K_LEFT:
                        dx = -1  # Двигаем фигуру влево
                    if event.key == pygame.K_RIGHT:
                        dx = 1  # Двигаем фигуру вправо
                    if event.key == pygame.K_DOWN:
                        self.anim_limit = 100  # Ускоряем падение фигуры
                    if event.key == pygame.K_UP:
                        rotate = True  # Вращаем фигуру
                    if event.key == pygame.K_ESCAPE:
                        # Выход из игры
                        self.running = False
                        self.screen = self.menu_sc
                        with open("game_end.txt", "w+") as fil:
                            fil.write("1")
                        break
                if event.type == music.STOPPED_PLAYING:
                    # Перезапуск музыки
                    music.play_music()
            if not self.running:
                break

            # Перемещение фигуры по оси X
            figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].x += dx
                if not self.collision_check(i):
                    self.figure = deepcopy(figure_old)
                    break

            # Обновление состояния игры (анимирование падения)
            self.anim_count += self.anim_speed
            if self.anim_count > self.anim_limit:
                self.anim_count = 0
                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i].y += 1
                    if not self.collision_check(i):
                        # Закрепляем фигуру на поле
                        for j in range(4):
                            self.field[figure_old[j].y][figure_old[j].x] = self.color
                        # Генерация новой фигуры
                        self.figure, self.color = self.next_figure, self.next_color
                        self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_next_color()
                        self.anim_limit = 2000
                        break

            # Поворот фигуры
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

            # Очистка заполненных линий
            line, lines = self.H - 1, 0
            for row in range(self.H - 1, -1, -1):
                count = 0
                for col in range(self.W):
                    if self.field[row][col]:
                        count += 1
                if count == self.W:
                    lines += 1
                    self.field.pop(row)
                    self.field.insert(0, [0 for _ in range(self.W)])
                else:
                    line -= 1

            # Обновление очков
            self.score += self.scores.get(lines, 0)
            self.lines += lines
            if lines:
                self.anim_limit -= 100

            # Установка рекорда, если необходимо
            self.set_record(record, self.score)

            # Обновление экрана
            pygame.display.update()
            self.clock.tick(self.FPS)

    def draw(self, record):
        """
        Отрисовка всех элементов игры: сетки, фигур, фона, очков и рекорда.
        """
        # Заполнение фона
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_sc, (20, 20))
        self.game_sc.blit(self.game_bg, (0, 0))

        # Отрисовка сетки
        [pygame.draw.rect(self.game_sc, (40, 40, 40), i_rect, 1) for i_rect in self.grid]

        # Отрисовка текущей фигуры
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * self.TILE
            self.figure_rect.y = self.figure[i].y * self.TILE
            pygame.draw.rect(self.game_sc, self.color, self.figure_rect)

        # Отрисовка закрепленных фигур
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * self.TILE, y * self.TILE
                    pygame.draw.rect(self.game_sc, col, self.figure_rect)

        # Отрисовка следующей фигуры
        for i in range(4):
            self.figure_rect.x = self.next_figure[i].x * self.TILE + 380
            self.figure_rect.y = self.next_figure[i].y * self.TILE + 185
            pygame.draw.rect(self.screen, self.next_color, self.figure_rect)

        # Отображение очков
        self.screen.blit(self.title_tetris, (485, -10))
        self.screen.blit(self.title_score, (535, 780))
        self.screen.blit(self.font.render(str(self.score), True, pygame.Color("white")), (550, 840))

        # Отображение рекорда
        self.screen.blit(self.title_record, (525, 650))
        self.screen.blit(self.font.render(record, True, pygame.Color("gold")), (550, 710))
