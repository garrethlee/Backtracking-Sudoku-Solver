import pygame
import time
import random

pygame.init()
pygame.font.init()
WIDTH, HEIGHT = 800, 600
SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sudoku Solver')
clock = pygame.time.Clock()


### COLORS ###
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (213, 213, 213)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

### FONTS ###
font = pygame.font.SysFont('SegoeUISemiBold', 30)

running = True
board_drawn = False
is_unsolvable = False
is_success = False

def format_time(s):
    return f'{s//60}:{s%60:02d}'


class Checkbox():
    def __init__(self, x, y, w, h, color):
        """Initialize a checkbox"""
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.rect = pygame.Rect(x, y, w, h)
        self.hovered = False
        self.active = False

    def hover(self):
        mousepos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mousepos):
            self.hovered = True
        else:
            self.hovered = False

    def draw(self):
        """Draws the checkbox and handles hover animation"""
        pygame.draw.rect(SURFACE, BLACK, self.rect, 7)
        if self.hovered:
            pygame.draw.rect(SURFACE, GRAY, self.rect, 7)
        if self.active:
            pygame.draw.rect(SURFACE, BLACK, self.rect)

    def update(self, event):
        self.hover()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousepos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mousepos):
                self.active = not self.active


class Message():
    def __init__(self, message, x, y, color):
        self.message = message
        self.color = color
        self.x = x
        self.y = y

    def draw(self):
        msg = font.render(self.message, False, self.color)
        SURFACE.blit(msg, (self.x, self.y))


class Button():
    def __init__(self, text, x, y, w, h, color):
        """Initialize a button"""
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        """Draws the button with text centered"""
        pygame.draw.rect(SURFACE, self.color, self.rect, 3)
        txt = font.render(self.text, False, self.color)
        txt_rect = txt.get_rect(center=self.rect.center)
        SURFACE.blit(txt, (txt_rect))

    def update(self, event):
        """Handles button presses"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousepos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mousepos):
                return True
            return None


class Cell():
    def __init__(self, surface, color, rect, width, value):
        """Initialize the cell"""
        self.surface = surface
        self.color = color
        self.rect = rect
        self.width = width
        self.value = f'{value}'
        self.cursor = pygame.Rect(
            self.rect.x + self.rect.width // 2.2, self.rect.y + self.rect.height // 4, 2, 30)

    def draw(self):
        """Draw each cell"""
        pygame.draw.rect(self.surface, self.color, self.rect, self.width)


class Board():
    def __init__(self):
        """Initialize 9x9 sudoku board"""
        self.w = 9
        self.h = 9
        self.hovered = None
        self.selected = False
        self.board = []
        self.solving = False
        self.show_steps = False
        self.grid = [[0 for i in range(9)] for j in range(9)]
        self.cur_time = 0
        self.start = pygame.time.get_ticks()

    def draw(self):
        """Draws the current state of the board"""
        self.board = []
        for i in range(1, 10):
            row = []
            for j in range(1, 10):
                #updates timer
                s = int((pygame.time.get_ticks() - self.start) / 1000)
                if s > self.cur_time and self.solving:
                    clock_surface = pygame.Surface((100, 50))
                    clock_surface.fill(WHITE)
                    seconds_txt = font.render(format_time(s), False, BLACK)
                    clock_surface.blit(seconds_txt, (0,0))
                    SURFACE.blit(clock_surface, (WIDTH * 0.7, HEIGHT * 0.1))
                    self.cur_time = s
                # create cell
                rect = pygame.Rect(50*j, 50*i, 50, 50)
                cell = Cell(SURFACE, BLACK, rect, 3,
                            '' if self.grid[i-1][j-1] == 0 else self.grid[i-1][j-1])
                cell.draw()
                # updates number inside cell
                if cell.value == '':
                    emptied_cell = pygame.Surface((35, 35))
                    emptied_cell.fill(WHITE)
                    SURFACE.blit(emptied_cell, (50*j+5, 50*i+5))
                else:
                    surface_text = font.render(cell.value, False, BLACK)
                    SURFACE.blit(surface_text, (cell.rect.x + cell.rect.width //
                                                3, cell.rect.y + cell.rect.height // 8))
                # draw horizontal lines
                if (i-1) % 3 == 0 and i != 1:
                    start_pos = (50*j, 50*i)
                    end_pos = (50*(j+1), 50*i)
                    pygame.draw.line(SURFACE, BLACK, start_pos, end_pos, 10)
                # draw vertical lines
                if (j-1) % 3 == 0 and j != 1:
                    start_pos = (50*j, 50*i)
                    end_pos = (50*j, 50*(i+1))
                    pygame.draw.line(SURFACE, BLACK, start_pos, end_pos, 10)
                row.append(cell)
                if self.solving and self.show_steps:
                    pygame.display.flip()
            self.board.append(row)
        clock.tick(30)

    def hover(self):
        """Grey border around cell when hovered"""
        x, y = pygame.mouse.get_pos()
        if 50 <= x < 500 and 50 <= y < 500:
            self.hovered = (y, x)
            cell = self.board[y//50-1][x//50-1]
            cell.color = GRAY
            cell.draw()
        else:
            self.hovered = None

    def select(self):
        """Selects a cell inside the board to edit"""
        x, y = pygame.mouse.get_pos()
        if 50 <= x <= 500 and 50 <= y <= 500:
            self.selected = (y//50-1, x//50-1)
        else:
            self.selected = None

    def update(self, event):
        """Updates selected cell of the board"""
        self.hover()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.select()
        if self.selected and event.type == pygame.KEYDOWN:
            y, x = self.selected
            cell = self.board[y][x]
            # handles arrow key inputs to change cells
            if event.key == pygame.K_UP:
                if y >= 1:  
                    self.selected = (y-1, x)
            if event.key == pygame.K_DOWN:
                if y <= 7:
                    self.selected = (y+1, x)
            if event.key == pygame.K_LEFT:
                self.selected = (y, x-1)
            if event.key == pygame.K_RIGHT:
                self.selected = (y, x+1)
            # handles number inputs
            if event.key == pygame.K_1:
                cell.value = '1'
                self.grid[y][x] = 1
            if event.key == pygame.K_2:
                cell.value = '2'
                self.grid[y][x] = 2
            if event.key == pygame.K_3:
                cell.value = '3'
                self.grid[y][x] = 3
            if event.key == pygame.K_4:
                cell.value = '4'
                self.grid[y][x] = 4
            if event.key == pygame.K_5:
                cell.value = '5'
                self.grid[y][x] = 5
            if event.key == pygame.K_6:
                cell.value = '6'
                self.grid[y][x] = 6
            if event.key == pygame.K_7:
                cell.value = '7'
                self.grid[y][x] = 7
            if event.key == pygame.K_8:
                cell.value = '8'
                self.grid[y][x] = 8
            if event.key == pygame.K_9:
                cell.value = '9'
                self.grid[y][x] = 9
            if event.key == pygame.K_BACKSPACE:
                cell.value = ''
                self.grid[y][x] = 0

    def blink(self):
        """Handles cursor blinking when a cell
        is selected"""
        if self.selected:
            y, x = self.selected
            cell = self.board[y][x]
            if cell.value == '':
                if pygame.time.get_ticks() % 1000 > 500:
                    pygame.draw.rect(SURFACE, BLACK, cell.cursor, 2)
                else:
                    pygame.draw.rect(SURFACE, WHITE, cell.cursor, 2)


class Sudoku():
    """Creates board using python 
    lists and contains backtracking
    logic to solve the puzzle"""

    def __init__(self, board):
        """Initializes empty board
        (if not given any values)
        or partially filled board"""
        self.grid = [[0 for i in range(9)] for j in range(9)]
        self.board = board

    def check(self):
        """Checks preliminary settings of board """
        for i in range(9):
            # checks duplicates per row
            row = self.grid[i]
            if sum(row) != sum(set(row)):
                return False

            # checks duplicates per col
            col = [self.grid[j][i] for j in range(9)]
            if sum(col) != sum(set(col)):
                return False

            # checks duplicates per quadrant
            if i % 3 == 0:
                for k in range(9):
                    if k % 3 == 0:
                        qx = k // 3 * 3
                        qy = i // 3 * 3
                        seen = []
                        for a in range(qx, qx+3):
                            for b in range(qy, qy+3):
                                if self.grid[a][b] in seen and self.grid[a][b] != 0:
                                    return False
                                else:
                                    seen.append(self.grid[a][b])
        return True

    def possible(self, i, j, grid, n):
        """Checks if value can be placed
        in current cell based on
        grid condition"""
        # check in row
        if n in grid[i]:
            return False
        # check in column
        if n in (grid[k][j] for k in range(9)):
            return False
        # check in quadrant
        qx = (j//3)*3
        qy = (i//3)*3
        for i in range(qy, qy+3):
            for j in range(qx, qx+3):
                if grid[i][j] == n:
                    return False
        return True

    def solve(self):
        """Backtracking algorithm
        implemented recursively"""
        if self.check():
            self.board.solving = True
            for i in range(9):
                for j in range(9):
                    if self.grid[i][j] == 0:
                        for k in range(1, 10):
                            if self.possible(i, j, self.grid, k):
                                self.grid[i][j] = k
                                self.board.grid[i][j] = k
                                self.board.draw()
                                if self.solve():
                                    self.board.solving = False
                                    return True
                                self.grid[i][j] = 0
                                self.board.grid[i][j] = 0
                                self.board.draw()
                        self.board.solving = False
                        return False
            self.board.solving = False
            return True

    def randomize(self):
        """Randomize board to solve"""
        for i in range(9):
            for j in range(9):
                has_num = random.randint(1, 10)
                if has_num < 3:
                    while True:
                        n = random.randint(1, 9)
                        if self.possible(i, j, self.grid, n):
                            self.grid[i][j] = n
                            break


### BUTTONS ###
solve_btn = Button('Solve', WIDTH * 0.7, HEIGHT * 0.3, 100, 50, BLACK)
reset_btn = Button('Reset', WIDTH * 0.7, HEIGHT * 0.45, 100, 50, BLACK)
randomize_btn = Button('Random', WIDTH * 0.7, HEIGHT * 0.2, 150, 50, BLACK)
show_steps = Checkbox(WIDTH * 0.7, HEIGHT * 0.6, 30, 30, BLACK)


board = Board()

### MESSAGES ###
unsolvable = Message('Unsolvable!', WIDTH * 0.7, HEIGHT * 0.7, RED)
show = Message('Show Steps', show_steps.x + 40, show_steps.rect.y - 10, BLACK)
success = Message("Success", WIDTH * 0.7, HEIGHT * 0.7, GREEN)
seconds = Message(format_time(board.cur_time), WIDTH * 0.7, HEIGHT * 0.1, BLACK)


show = [solve_btn, reset_btn, randomize_btn, show_steps, show, seconds]

while running:
    board.blink()
    for event in pygame.event.get():
        
        SURFACE.fill(WHITE)
        board.draw()
        board.update(event)

        for item in show:
            item.draw()

        if is_unsolvable:
            unsolvable.draw()
        if is_success:
            success.draw()

        solve_is_clicked = solve_btn.update(event)
        reset_is_clicked = reset_btn.update(event)
        randomize_is_clicked = randomize_btn.update(event)
        show_steps.update(event)

        if solve_is_clicked:
            is_unsolvable = False
            is_success = False
            pygame.display.update()
            # solve the sudoku puzzle, return error message if board is incompatible
            board.start = pygame.time.get_ticks()
            board.cur_time = 0
            sudoku = Sudoku(board)
            sudoku.grid = board.grid

            if show_steps.active:
                sudoku.board.show_steps = True

            pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
            pygame.display.set_caption(
                "Loading... Please refrain from clicking anything")
            if sudoku.solve():
                is_success = True
            else:
                is_unsolvable = True
            pygame.display.set_caption('Sudoku Solver')
            pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
            seconds.message = format_time(board.cur_time)

        if randomize_is_clicked:
            board.start = pygame.time.get_ticks()
            sudoku = Sudoku(board)
            sudoku.randomize()
            board.grid = sudoku.grid
            is_unsolvable = False
            is_success = False

        if reset_is_clicked:
            # resets the whole board
            board = Board()
            is_unsolvable = False
            is_success = False
            seconds.message = format_time(0)

        if event.type == pygame.QUIT:
            running = False
            break

    pygame.display.update()
