from queue import SimpleQueue
import random
from time import time
from terminal import colors
import terminal
from pynput import keyboard

class GameTetris:
    WIDTH = 10
    HEIGHT = 24
    PIECES = [
        # T
        [
            [0,1,0],
            [1,1,1],
        ],
        [
            [1,1,0],
            [0,1,1],
        ],
        [
            [0,1,1],
            [1,1,0],
        ],
        [
            [1,1],
            [1,1],
        ],
        [
            [1,1,1,1]
        ],
        [
            [1,0,0],
            [1,1,1]
        ],
        [
            [0,0,1],
            [1,1,1]
        ],
    ]

    NONE = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3
    ROTATE = 4
    EXIT = 5

    def __init__(self, term : terminal.Term):
        self.__context = term
        self.__context.setup(self.WIDTH * 2 + 18, self.HEIGHT + 2, "Tetris")
        
        self.__context.cursor_hide()
        self.__context.execute_commands()
        
        self.__current_piece = []
        self.__current_piece_pos = [0,0]
        self.__grid =  [[0 for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        self.__running = False
        self.__current_color =  self.__random_color()

        # board border
        width = self.WIDTH * 2
        border_width = self.WIDTH - 4

        self.__context.write_str_at(0,0, '┏' + '━' * border_width + '┫' + "Tetris" + '┣' + '━' * border_width + '┓')
        for y in range(0, self.HEIGHT):
            self.__context.write_str_at(0, y + 1, '┃' + ' ' * width + '┃')

        self.__context.write_str_at(0,self.HEIGHT + 1, '┗' + '━' * width + '┛')

        # next piece border
        offset = width + 4
        self.__context.write_str_at(offset, 0, '┏━━┫' + "Next" + '┣━━┓')
        for y in range(0, 5):
            self.__context.write_str_at(offset, y + 1, '┃' + ' ' * (5 * 2) + '┃')

        self.__context.write_str_at(offset, 6, '┗' + '━' * (5 * 2) + '┛')
        
        self.__listener = keyboard.Listener(on_release=self.__handle_keyboard_release)
        self.__keys = SimpleQueue()

    def __handle_keyboard_release(self, code):
        if code == keyboard.Key.left:
            self.__keys.put(self.MOVE_LEFT)
        elif code == keyboard.Key.right:
            self.__keys.put(self.MOVE_RIGHT)
        elif code == keyboard.Key.up:
            self.__keys.put(self.ROTATE)
        elif code == keyboard.Key.down:
            self.__keys.put(self.MOVE_DOWN)
        elif code == keyboard.Key.esc:
            self.__keys.put(self.EXIT)
            self.__running = False

    def run(self):
        self.__context.print_screen()
        self.__current_piece_pos[0] = self.WIDTH // 2
        self.__current_piece = random.choice(self.PIECES)
        self.__running = True
        self.__listener.start()

        start = time()
        delta = 0
        while self.__running:
            delta = time() - start
            
            try:
                key = self.__keys.get(False, 0.2)
                if key == self.EXIT:
                    break
                elif key == self.ROTATE:
                    self.__rotate()
                else:
                    self.__move(key)

            except:
                pass

            if delta > 0.2:
                start = time()
                delta = 0
                
                self.__clear_block()

                if not self.__move(self.MOVE_DOWN):
                    self.__current_piece = random.choice(self.PIECES)
                    self.__current_piece_pos = [self.WIDTH // 2, 0] 
                    self.__current_color =  self.__random_color()

            self.__print_block()

        self.__listener.stop()

    def __random_color(self):
        return random.choice(colors.ALL_FG_COLORS)

    def __clear_cell(self, x : int, y : int):
        self.__context.write_str_at(x * 2 + 1, y + 1, '  ')

    def __write_cell(self, x : int, y : int):
        self.__context.write_str_at(x * 2 + 1, y + 1, '██', [self.__current_color, colors.COLOR_BG_DEFAULT])

    def __print_block(self):
        for y in range(len(self.__current_piece)):
            for x in range(len(self.__current_piece[y])):
                if self.__current_piece[y][x] != 0:
                    self.__write_cell(x + self.__current_piece_pos[0], y + self.__current_piece_pos[1])
        self.__context.print_screen()

    def __clear_block(self):
        for y in range(len(self.__current_piece)):
            for x in range(len(self.__current_piece[y])):
                if self.__current_piece[y][x] != 0:
                    self.__clear_cell(x + self.__current_piece_pos[0], y + self.__current_piece_pos[1])
        self.__context.print_screen()

    def __rotate(self):
        rotated = list(map(list, zip(*self.__current_piece[::-1])))

        if self.__can_move(rotated, self.__current_piece_pos):
            self.__current_piece = rotated
    
    def __move(self, move : int) -> bool:
        new_pos = self.__current_piece_pos

        if move == self.MOVE_DOWN:
            new_pos[1] += 1
        elif move == self.MOVE_LEFT:
            new_pos[0] -= 1
        else:
            new_pos[0] += 1

        if self.__can_move(self.__current_piece, new_pos):
            self.__current_piece_pos = new_pos
            return True
        else:
            return False
    
    def __can_move(self, block : list[list[int]], pos : list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)
        
        if pos[0] <= 0 or pos[0] + block_width >= self.WIDTH - 1:
            return False
        elif pos[1] < 0 or pos[1] + block_height >= self.HEIGHT:
            return False
        else:
            return not self.__check_overlapping(block, pos)
    
    def __check_overlapping(self, block : list[list[int]], pos : list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)

        for y in range(block_height):
            for x in range(block_width):
                if block[y][x] == 1:
                    if self.__grid[y + pos[1]][x + pos[0]] == 1:
                        return True
        return False