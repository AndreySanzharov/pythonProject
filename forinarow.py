import math
import random
import sys
import numpy as np
import pygame
import music

# Инициализация Pygame
pygame.init()

# Определяем цвета для игрового интерфейса
BLUE = pygame.Color('blue')
BLACK = pygame.Color('black')
RED = pygame.Color('red')
YELLOW = pygame.Color('yellow')

# Константы для игроков и типа ячейки
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

# Длина окна для победного условия
WINDOW_LENGTH = 4

# Размер клетки
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)


class FourInARow:
    def __init__(self, row_count, col_count):
        # Инициализация игры с заданным количеством рядов и колонок.
        self.row_count = row_count
        self.col_count = col_count
        self.width = col_count * SQUARESIZE
        self.height = (row_count + 1) * SQUARESIZE  # Дополнительный ряд для отображения хода
        self.size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.size)  # Создаем экран
        self.board = self.create_board()  # Создаем игровую доску
        self.draw_board(self.board)  # Отрисовываем доску
        pygame.display.set_caption("FourInARow")  # Устанавливаем заголовок окна
        programicon = pygame.image.load('icons/4inarow.png')  # Загружаем иконку
        pygame.display.set_icon(programicon)

    def create_board(self):
        # Создаем пустую доску (матрица заполнена нулями, означающими пустые клетки)
        board = np.zeros((self.row_count, self.col_count))
        return board

    @staticmethod
    def drop_piece(board, row, col, piece):
        # Выполняем ход, устанавливая кусочек на указанную строку и столбец
        board[row][col] = piece

    def is_valid_location(self, board, col):
        # Проверка, можно ли сделать ход в данном столбце (пустая ли верхняя клетка)
        return board[self.row_count - 1][col] == 0

    def get_next_open_row(self, board, col):
        # Поиск первой доступной строки в выбранном столбце
        for r in range(self.row_count):
            if board[r][col] == 0:
                return r

    def winning_move(self, board, piece):
        # Проверка победного условия для горизонталей, вертикалей и диагоналей
        # Проверка горизонтальных победных комбинаций
        for c in range(self.col_count - 3):
            for r in range(self.row_count):
                if all([board[r][c + i] == piece for i in range(4)]):
                    return True

        # Проверка вертикальных победных комбинаций
        for c in range(self.col_count):
            for r in range(self.row_count - 3):
                if all([board[r + i][c] == piece for i in range(4)]):
                    return True

        # Проверка диагональных победных комбинаций (слева направо)
        for c in range(self.col_count - 3):
            for r in range(self.row_count - 3):
                if all([board[r + i][c + i] == piece for i in range(4)]):
                    return True

        # Проверка диагональных победных комбинаций (справа налево)
        for c in range(self.col_count - 3):
            for r in range(3, self.row_count):
                if all([board[r - i][c + i] == piece for i in range(4)]):
                    return True

    @staticmethod
    def evaluate_window(window, piece):
        # Оценка очков для конкретного окна (подматрицы)
        score = 0
        opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

        # Добавляем очки за комбинации (4 подряд, 3 подряд, 2 подряд)
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2

        # Уменьшаем очки за комбинацию из 3 подряд для противника
        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, board, piece):
        # Оцениваем всю доску для выбора оптимального хода
        score = 0

        # Оценка центральной колонки для дополнительного приоритета
        center_array = [int(i) for i in list(board[:, self.col_count // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Оценка по горизонтали
        for r in range(self.row_count):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(self.col_count - 3):
                window = row_array[c:c + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Оценка по вертикали
        for c in range(self.col_count):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(self.row_count - 3):
                window = col_array[r:r + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Оценка по диагоналям (слева направо)
        for r in range(self.row_count - 3):
            for c in range(self.col_count - 3):
                window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Оценка по диагоналям (справа налево)
        for r in range(self.row_count - 3):
            for c in range(self.col_count - 3):
                window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board):
        # Проверка, завершена ли игра (победа или ничья)
        return self.winning_move(board, PLAYER_PIECE) or \
            self.winning_move(board, AI_PIECE) or len(self.get_valid_locations(board)) == 0

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        # Алгоритм Минимакс для выбора оптимального хода
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, AI_PIECE):
                    return None, 100000000000000
                elif self.winning_move(board, PLAYER_PIECE):
                    return None, -10000000000000
                else:
                    return None, 0
            else:
                return None, self.score_position(board, AI_PIECE)
        if maximizing_player:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, AI_PIECE)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def get_valid_locations(self, board):
        # Возвращаем список доступных колонок для хода
        valid_locations = []
        for col in range(self.col_count):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

    def pick_best_move(self, board, piece):
        # Определяем наилучший ход, проверяя все доступные ходы
        valid_locations = self.get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(board, col)
            temp_board = board.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    def draw_board(self, board):
        # Отрисовка игрового поля с клетками
        for c in range(self.col_count):
            for r in range(self.row_count):
                pygame.draw.rect(self.screen, BLUE,
                                 (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(self.screen, BLACK, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

        for c in range(self.col_count):
            for r in range(self.row_count):
                color = RED if board[r][c] == PLAYER_PIECE else YELLOW if board[r][c] == AI_PIECE else BLACK
                pygame.draw.circle(self.screen, color, (
                int(c * SQUARESIZE + SQUARESIZE / 2), self.height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        pygame.display.update()


    def start(self):  # основной цикл
        pygame.display.update()
        game_over = False
        running = True
        myfont = pygame.font.SysFont("monospace", 75)

        turn = random.randint(PLAYER, AI)

        while not game_over and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:  # отрисовываем шарик, который собираемся бросать
                    pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, SQUARESIZE))
                    posx = event.pos[0]
                    if turn == PLAYER:
                        pygame.draw.circle(self.screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:  # игрок делает ход
                    pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, SQUARESIZE))
                    if turn == PLAYER:
                        posx = event.pos[0]
                        col = int(math.floor(posx / SQUARESIZE))

                        if self.is_valid_location(self.board, col):
                            row = self.get_next_open_row(self.board, col)
                            self.drop_piece(self.board, row, col, PLAYER_PIECE)

                            if self.winning_move(self.board, PLAYER_PIECE):
                                label = myfont.render("Красный победил!", True, RED)
                                self.screen.blit(label, (40, 10))
                                game_over = True

                            turn += 1
                            turn = turn % 2

                            self.draw_board(self.board)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        with open("game_end.txt", "w+") as fil:
                            fil.write("1")
                        break
                if event.type == music.STOPPED_PLAYING:
                    music.play_music()
            if running:
                if turn == AI and not game_over:  # компьютер делает ход
                    col, minimax_score = self.minimax(self.board, 5, -math.inf, math.inf, True)

                    if self.is_valid_location(self.board, col):
                        row = self.get_next_open_row(self.board, col)
                        self.drop_piece(self.board, row, col, AI_PIECE)

                        if self.winning_move(self.board, AI_PIECE):
                            label = myfont.render("Желтый победил!", True, YELLOW)
                            self.screen.blit(label, (40, 10))
                            game_over = True

                        self.draw_board(self.board)

                        turn += 1
                        turn = turn % 2

                if game_over:
                    pygame.time.wait(3000)
