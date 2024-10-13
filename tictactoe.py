import os
import random
import sys
import time

import pygame

import music

pygame.init()
EMPTY = -1
PLAYER1 = 0
PLAYER2 = 1


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def terminate():
    pygame.quit()
    sys.exit()


class TicTacToe:
    class Digit(pygame.sprite.Sprite): # цифра для отображения счета
        def __init__(self, coords, color, size, *groups):
            super().__init__(*groups)
            x, y = coords
            self.color = color
            self.size = size
            self.image = pygame.transform.scale(load_image(self.color + "_0.png"), self.size)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            pygame.display.set_caption("TicTacToe")
            programicon = pygame.image.load('icons/tictactoe.png')
            pygame.display.set_icon(programicon)

        def change(self, digit): # узменяем цифру
            self.image = pygame.transform.scale(load_image(self.color + "_" + digit + ".png"), self.size)

    def __init__(self, cell_size, margin):
        self.player_1 = 0
        self.player_2 = 0
        self.vs_computer = None
        self.margin = margin
        self.cell_size = cell_size
        self.width = cell_size * 3 + margin * 2
        self.height = self.width + self.width // 4
        size = self.width, self.height
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Крестики-нолики")
        self.cells = [[-1 for _ in range(3)] for _ in range(3)]
        self.move = 0
        self.scores = { # словарь для подсчета очков для алгоритма минимакс
            1: 100,
            0: -100,
            'draw': 0
        }
        self.all_sprites = pygame.sprite.Group()
        self.x_image = pygame.transform.scale(load_image("krestik.png"), (self.cell_size, self.cell_size))

        self.o_image = pygame.transform.scale(load_image("nolik.png"), (self.cell_size, self.cell_size))

        self.difficulty = None

        self.score_group_1 = pygame.sprite.Group() # группы спрайтов для счета
        self.score_group_2 = pygame.sprite.Group()

        score_size = self.width // 8, self.height // 7
        
        # сами спрайты для счета
        self.score1_2 = self.Digit((self.width // 8 - score_size[0] // 2, 5 * self.height // 6), 'b', score_size,
                                   self.score_group_1)
        self.score1_1 = self.Digit((self.width // 8 + score_size[0] // 2, 5 * self.height // 6), 'b', score_size,
                                   self.score_group_1)

        self.score2_1 = self.Digit(
            (self.width - self.width // 8 + score_size[0] // 2 - score_size[0], 5 * self.height // 6), 'r', score_size,
            self.score_group_2)
        self.score2_2 = self.Digit(
            (self.width - self.width // 8 - score_size[0] // 2 - score_size[0], 5 * self.height // 6), 'r', score_size,
            self.score_group_2)
        
    def signal(self, result): # показать результат игры и обнулить поле
        self.move = 0
        self.all_sprites.empty()
        self.cells = [[-1 for _ in range(3)] for _ in range(3)]
        self.all_sprites.update()
        self.screen.fill((0, 0, 0))

        if result == -1:
            fon_name = "draw.png"
        elif result == 0:
            fon_name = "o_win.png"
            self.player_1 += 1
            self.score1_1.change(str(self.player_1).rjust(2, '0')[1])
            self.score1_2.change(str(self.player_1).rjust(2, '0')[0])
            self.score_group_1.update(self.screen)
        else:
            fon_name = "x_win.png"
            self.player_2 += 1
            self.score2_1.change(str(self.player_2).rjust(2, '0')[1])
            self.score2_2.change(str(self.player_2).rjust(2, '0')[0])
            self.score_group_2.update(self.screen)

        fon = pygame.transform.scale(load_image(fon_name), (self.width, self.height))

        self.screen.blit(fon, (0, 0))
        pygame.display.flip()
        time.sleep(3)
        self.screen.fill((0, 0, 0))
        self.update()

    def selection_mode(self, selecting_player_numbers=True): # выбор режима и сложности

        button_size = self.width // 4, 7 * self.width // 4 // 20

        def on_button_1(pos):
            x = pos[0]
            y = pos[1]
            if self.width // 2 - self.width // 8 < x < self.width // 2 + button_size[0] \
                    and self.height // 2 - 100 < y < self.height // 2 - 100 + button_size[1]:
                return True
            return False

        def on_button_2(pos):
            x = pos[0]
            y = pos[1]
            if self.width // 2 - self.width // 8 < x < self.height // 2 + button_size[0] \
                    and self.height // 2 < y < self.height // 2 + button_size[1]:
                return True
            return False

        class PlayerButton(pygame.sprite.Sprite): # кнопка
            def __init__(self, coords, image, image_fon, *groups):
                super().__init__(*groups)
                x, y = coords
                self.image = pygame.transform.scale(load_image(image), button_size)
                self.image_normal = pygame.transform.scale(load_image(image), button_size)
                self.image_fon = pygame.transform.scale(load_image(image_fon), button_size)
                self.turn = True
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y

            def update(self): # подсветка при наведении курсора
                if self.turn:
                    self.image = self.image_fon
                    self.turn = False
                else:
                    self.image = self.image_normal
                    self.turn = True

        coords_1 = self.width // 2 - self.width // 8, self.height // 2 - 100
        coords_2 = self.width // 2 - self.width // 8, self.height // 2

        sprites_1 = pygame.sprite.Group()
        if selecting_player_numbers: # если выбор количества игроков, то картинки с нужной надписью
            button1_name = "1pl.png"
            button1_fon_name = "1pl_fon.png"
            button2_name = "2pl.png"
            button2_fon_name = "2pl_fon.png"
            fon_name = "selection_mode.png"
        else:
            button1_name = "hard.png"
            button1_fon_name = "hard_fon.png"
            button2_name = "easy.png"
            button2_fon_name = "easy_fon.png"
            fon_name = "difficulty_selection.png"

        fon = pygame.transform.scale(load_image(fon_name), (self.width, self.height))

        PlayerButton(coords_1, button1_name, button1_fon_name, sprites_1)
        sprites_2 = pygame.sprite.Group()
        PlayerButton(coords_2, button2_name, button2_fon_name, sprites_2)
        sprites_1_fon = True
        sprites_2_fon = True
        sprites_1.draw(self.screen)
        sprites_2.draw(self.screen)

        while True:
            if on_button_1(pygame.mouse.get_pos()) and sprites_1_fon:
                sprites_1_fon = False
                sprites_1.update()
            elif not on_button_1(pygame.mouse.get_pos()) and not sprites_1_fon:
                sprites_1_fon = True
                sprites_1.update()
            if on_button_2(pygame.mouse.get_pos()) and sprites_2_fon:
                sprites_2.update()
                sprites_2_fon = False
            elif not on_button_2(pygame.mouse.get_pos()) and not sprites_2_fon:
                sprites_2_fon = True
                sprites_2.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if on_button_1(event.pos):
                        if selecting_player_numbers:
                            self.vs_computer = True
                            self.selection_mode(False)
                            return
                        self.difficulty = 1
                        self.screen.fill((0, 0, 0))
                        return
                    elif on_button_2(event.pos):
                        if selecting_player_numbers:
                            self.vs_computer = False
                            self.screen.fill((0, 0, 0))
                            return
                        self.difficulty = 0
                        self.screen.fill((0, 0, 0))
                        return
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()

            self.screen.fill((0, 0, 0))
            self.screen.blit(fon, (0, 0))
            sprites_1.draw(self.screen)
            sprites_2.draw(self.screen)

            pygame.display.flip()

    def update(self): # обновляем экран, когда сделали ход или очистили поле
        self.screen.fill((0, 0, 0))
        self.all_sprites.draw(self.screen)
        self.score_group_1.draw(self.screen)
        self.score_group_2.draw(self.screen)
        color = pygame.Color('white')
        pygame.draw.rect(self.screen, color, (self.cell_size, 0, self.margin, self.height - self.width // 4))
        pygame.draw.rect(self.screen, color,
                         (2 * self.cell_size + self.margin, 0, self.margin, self.height - self.width // 4))
        pygame.draw.rect(self.screen, color, (0, self.cell_size, self.width, self.margin))
        pygame.draw.rect(self.screen, color, (0, 2 * self.cell_size + self.margin, self.width, self.margin))

        self.all_sprites.draw(self.screen)

        pygame.display.flip()

    def get_random_cell(self): # выбор хода для легкого режима
        while True:
            x, y = random.randint(0, 2), random.randint(0, 2)
            if self.cells[y][x] == -1:
                return x, y

    def make_move(self, mouse_pos, is_user_turn): # делаем ход
        krestik = pygame.sprite.Sprite()
        krestik.image = self.x_image
        krestik.rect = krestik.image.get_rect()

        nolik = pygame.sprite.Sprite()
        nolik.image = self.o_image
        nolik.rect = nolik.image.get_rect()

        cell_x = (mouse_pos[0] - self.margin) // (self.cell_size + self.margin)
        cell_y = (mouse_pos[1] - self.margin) // (self.cell_size + self.margin)
        x = cell_x * self.cell_size + cell_x * self.margin
        y = cell_y * self.cell_size + cell_y * self.margin
        if self.cells[cell_y][cell_x] == -1:
            if is_user_turn:
                self.cells[cell_y][cell_x] = self.move % 2
                if self.move % 2 == PLAYER2:
                    krestik = pygame.sprite.Sprite()
                    krestik.image = self.x_image
                    krestik.rect = krestik.image.get_rect()
                    krestik.rect.x = x
                    krestik.rect.y = y
                    self.all_sprites.add(krestik)
                else:
                    nolik = pygame.sprite.Sprite()
                    nolik.image = self.o_image
                    nolik.rect = nolik.image.get_rect()
                    nolik.rect.x = x
                    nolik.rect.y = y
                    self.all_sprites.add(nolik)

                self.move += 1
                if self.move != 9 and self.vs_computer: # делаем ход компьютера
                    self.make_move(mouse_pos, False)
        
        if self.is_win(0, self.cells):
            self.signal(0)
            return

        elif self.is_win(1, self.cells):
            self.signal(1)
            return
        elif self.move == 9:
            self.signal(-1)
            return
        
        if not is_user_turn:
            if self.difficulty:
                x, y = self.get_computer_position()
            else:
                x, y = self.get_random_cell()
            self.cells[y][x] = PLAYER2

            x = x * self.cell_size + x * self.margin
            y = y * self.cell_size + y * self.margin
            krestik.rect.x = x
            krestik.rect.y = y
            self.all_sprites.add(krestik)
            self.move += 1

        self.all_sprites.update()
        self.update()
        pygame.display.flip()

    def minimax(self, board, is_ai_turn): # рекурсивный алгоритм для поиска лучшего решения
        if self.is_win(PLAYER1, board):
            return self.scores[PLAYER1]
        if self.is_win(PLAYER2, board):
            return self.scores[PLAYER2]
        if self.is_draw(board):
            return self.scores['draw']

        if is_ai_turn:
            # выбираем ход который нам выгодней
            best_score = - sys.maxsize
            for y in range(3):
                for x in range(3):
                    if board[y][x] == EMPTY:
                        board[y][x] = PLAYER2
                        score = self.minimax(board, False)
                        board[y][x] = EMPTY
                        best_score = max(best_score, score)
        else:
            # пользователь выбирает ход который нам не выгоден
            best_score = sys.maxsize
            for y in range(3):
                for x in range(3):
                    if board[y][x] == -1:
                        board[y][x] = PLAYER1
                        score = self.minimax(board, True)
                        board[y][x] = EMPTY
                        best_score = min(best_score, score)
        return best_score

    def get_computer_position(self): # рассматриваем все возможные ходы и считаем наилучший
        move = None
        best_score = -sys.maxsize
        board = [self.cells[y].copy() for y in range(3)]
        for y in range(3):
            for x in range(3):
                if board[y][x] == EMPTY:
                    board[y][x] = PLAYER2
                    score = self.minimax(board, False)
                    board[y][x] = EMPTY
                    if score > best_score:
                        best_score = score
                        move = x, y
        return move

    @staticmethod
    def is_win(char, field): # проверка на победу
        opponent_char = int(not bool(char))
        # проверяем строки
        for y in range(3):
            if opponent_char not in field[y] and EMPTY not in field[y]:
                return True

        # проверяем колонки
        for x in range(3):
            col = [field[0][x], field[1][x], field[2][x]]
            if opponent_char not in col and EMPTY not in col:
                return True

        # проверяем диагонали
        diagonal = [field[0][0], field[1][1], field[2][2]]
        if opponent_char not in diagonal and EMPTY not in diagonal:
            return True
        diagonal = [field[0][2], field[1][1], field[2][0]]
        if opponent_char not in diagonal and EMPTY not in diagonal:
            return True

        return False

    @staticmethod
    def is_draw(board): # проверка на заполнение поля
        count = 0
        for y in range(3):
            count += 1 if EMPTY in board[y] else 0
        return count == 0

    def start(self): # основной цикл
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.make_move(event.pos, True)
                    self.screen.fill((0, 0, 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        with open("game_end.txt", "w+") as fil:
                            fil.write("1")
                        break
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()
