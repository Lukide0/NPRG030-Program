import random
import terminal

from queue import SimpleQueue
from time import time
from terminal import colors
from pynput import keyboard


class GameTetris:
    WIDTH = 15
    HEIGHT = 30
    MAX_FALLING_SPEED = 0.05
    START_FALLING_SPEED = 0.4
    MAX_PIECE_LEN = 4
    SIDEBAR_WIDTH = 16
    MARGIN = 2

    PIECES = [
        [
            [0, 1, 0],
            [1, 1, 1],
        ],
        [
            [1, 1, 0],
            [0, 1, 1],
        ],
        [
            [0, 1, 1],
            [1, 1, 0],
        ],
        [
            [1, 1],
            [1, 1],
        ],
        [[1, 1, 1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
    ]

    NONE = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3
    ROTATE = 4
    EXIT = 5

    def __init__(self, term: terminal.Term):

        self.__context = term
        self.__context.setup(
            self.WIDTH * 2 + 2 + self.MARGIN + 2 + self.SIDEBAR_WIDTH,
            self.HEIGHT + 2,
            "Tetris",
        )

        self.__context.cursor_hide()
        self.__context.execute_commands()

        self.__current_color: int = None
        self.__current_piece = []

        self.__falling_speed = self.START_FALLING_SPEED

        self.__next_color = self.__random_color()
        self.__next_piece = random.choice(self.PIECES)

        self.__current_piece_pos: list[int] = [0, 0]

        self.__grid: list[list[int]] = [
            [[0, None] for x in range(self.WIDTH)] for y in range(self.HEIGHT)
        ]
        self.__running = False


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

    def __prepare(self):
        self.__listener = keyboard.Listener(on_press=self.__handle_keyboard_release)
        self.__keys = SimpleQueue()

        # board border
        width = self.WIDTH * 2
        border_width = self.WIDTH - 4

        self.__context.write_str_at(
            0,
            0,
            "┏" + "━" * border_width + "┫" + "Tetris" + "┣" + "━" * border_width + "┓",
        )
        for y in range(0, self.HEIGHT):
            self.__context.write_str_at(0, y + 1, "┃" + " " * width + "┃")

        self.__context.write_str_at(0, self.HEIGHT + 1, "┗" + "━" * width + "┛")

        # next piece border
        offset = width + 2 + self.MARGIN
        line_width = self.SIDEBAR_WIDTH

        self.__next_piece_offset = offset

        self.__context.write_str_at(
            offset,
            0,
            "┏"
            + "━" * ((line_width - 6) // 2)
            + "┫"
            + "Next"
            + "┣"
            + "━" * ((line_width - 6) // 2)
            + "┓",
        )
        for y in range(0, 4):
            self.__context.write_str_at(offset, y + 1, "┃" + " " * line_width + "┃")

        self.__context.write_str_at(offset, 5, "┗" + "━" * line_width + "┛")

        scope_start_y = self.MARGIN // 2 + 5
        # score 
        self.__score : int = 0
        self.__score_pos = [offset + 9, scope_start_y + 1]
        self.__lines : int = 0
        self.__level : int = 0

        self.__context.write_str_at(offset, scope_start_y, "┏" + "━" * line_width + "┓")
        self.__context.write_str_at(offset, scope_start_y + 1, f"┃ Score: {self.__score:07d} ┃")
        self.__context.write_str_at(offset, scope_start_y + 2, f"┃ Lines: {self.__lines:07d} ┃")
        self.__context.write_str_at(offset, scope_start_y + 3, f"┃ Level: {self.__level:07d} ┃")
        self.__context.write_str_at(offset, scope_start_y + 4, "┗" + "━" * line_width + "┛")

    def run(self):
        # print borders
        self.__prepare()
        self.__context.print_screen()
        self.__running = True

        # 1.st block
        self.__spawn_block()
        self.__create_next_piece()

        self.__print_block()

        self.__listener.start()

        start = time()
        delta = 0

        while self.__running:
            delta = time() - start

            try:
                # throws EmptyException
                key = self.__keys.get(False, 0.3)
                if key == self.EXIT:
                    break

                if key == self.ROTATE:
                    self.__rotate()
                else:
                    self.__move(key)
            except:
                pass

            if delta > self.__falling_speed:
                start = time()
                delta = 0

                if not self.__move(self.MOVE_DOWN):
                    self.__place_block()
                    self.__spawn_block()
                    self.__create_next_piece()
                    if self.__check_overlapping(
                        self.__current_piece, self.__current_piece_pos
                    ):
                        self.__running = False
                        break

            self.__print_block()

        self.__listener.stop()
        self.__context.clear_styles()

    def __create_next_piece(self):
        # clear previous
        height = len(self.__next_piece)
        width = len(self.__next_piece[0])

        offset_x = (self.SIDEBAR_WIDTH - 3) // 2 - width

        for y in range(height):
            for x in range(width):
                if self.__next_piece[y][x] == 1:
                    self.__context.write_str_at(
                        self.__next_piece_offset + 3 + x * 2 + offset_x, y + 2, "  "
                    )

        self.__next_piece = random.choice(self.PIECES)
        self.__next_color = self.__random_color()

        height = len(self.__next_piece)
        width = len(self.__next_piece[0])

        offset_x = (self.SIDEBAR_WIDTH - 3) // 2 - width
        for y in range(height):
            for x in range(width):
                if self.__next_piece[y][x] == 1:
                    self.__context.write_str_at(
                        self.__next_piece_offset + 3 + x * 2 + offset_x,
                        y + 2,
                        "██",
                        [self.__next_color, colors.COLOR_BG_DEFAULT],
                    )

        self.__context.print_screen()

    def __place_block(self):
        pos_x = self.__current_piece_pos[0]
        pos_y = self.__current_piece_pos[1]
        block_width = len(self.__current_piece[0])
        block_height = len(self.__current_piece)

        remove_indexes = []
        for y in range(block_height):
            for x in range(block_width):
                if self.__current_piece[y][x] != 0:
                    self.__grid[y + pos_y][x + pos_x][0] = 1
                    self.__grid[y + pos_y][x + pos_x][1] = self.__current_color

            remove = True
            for x in range(self.WIDTH):
                if self.__grid[y + pos_y][x][0] == 0:
                    remove = False
                    break

            if remove:
                remove_indexes.append(y + pos_y)

        if not remove_indexes:
            return

        removed_lines_count = len(remove_indexes)
        
        self.__lines += removed_lines_count
        self.__level = self.__lines // 10
        self.__falling_speed = max(self.START_FALLING_SPEED - self.__level * 0.05, self.MAX_FALLING_SPEED)

        if removed_lines_count == 1:
            self.__score += removed_lines_count * 40 * (self.__level + 1)
        elif removed_lines_count == 2:
            self.__score += removed_lines_count * 100 * (self.__level + 1)
        elif removed_lines_count == 3:
            self.__score += removed_lines_count * 300 * (self.__level + 1)
        else:
            self.__score += removed_lines_count * 1200 * (self.__level + 1)

        x, y = self.__score_pos
        self.__context.write_str_at(x, y, f"{self.__score:07d}")
        self.__context.write_str_at(x, y + 1, f"{self.__lines:07d}")
        self.__context.write_str_at(x, y + 2, f"{self.__level:07d}")

        for index in remove_indexes:
            self.__grid.pop(index)
            self.__grid.insert(0, [[0, None] for i in range(self.WIDTH)])

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.__grid[y][x][0] != 0:
                    self.__write_cell(x, y, self.__grid[y][x][1])
                else:
                    self.__clear_cell(x, y)

    def __spawn_block(self):
        self.__current_piece = self.__next_piece
        self.__current_piece_pos = [self.WIDTH // 2, 0]
        self.__current_color = self.__next_color

    def __random_color(self):
        color = random.choice(colors.ALL_FG_COLORS)
        if color == colors.COLOR_FG_BLACK or color == colors.COLOR_FG_DEFAULT:
            return colors.COLOR_FG_BLACK_BRIGHT
        else:
            return color

    def __clear_cell(self, x: int, y: int):
        self.__context.write_str_at(x * 2 + 1, y + 1, "  ")

    def __write_cell(self, x: int, y: int, color: int):
        self.__context.write_str_at(
            x * 2 + 1, y + 1, "██", [color, colors.COLOR_BG_DEFAULT]
        )

    def __print_block(self):
        for y in range(len(self.__current_piece)):
            for x in range(len(self.__current_piece[y])):
                if self.__current_piece[y][x] != 0:
                    self.__write_cell(
                        x + self.__current_piece_pos[0],
                        y + self.__current_piece_pos[1],
                        self.__current_color,
                    )
        self.__context.print_screen()

    def __clear_block(self):
        for y in range(len(self.__current_piece)):
            for x in range(len(self.__current_piece[y])):
                if self.__current_piece[y][x] != 0:
                    self.__clear_cell(
                        x + self.__current_piece_pos[0], y + self.__current_piece_pos[1]
                    )

    def __rotate(self):
        # rotate list
        rotated = list(map(list, zip(*self.__current_piece[::-1])))

        if self.__can_move(rotated, self.__current_piece_pos):
            self.__clear_block()
            self.__current_piece = rotated

    def __move(self, move: int) -> bool:
        new_pos = self.__current_piece_pos[:]

        if move == self.MOVE_DOWN:
            new_pos[1] += 1
        elif move == self.MOVE_LEFT:
            new_pos[0] -= 1
        else:
            new_pos[0] += 1

        if self.__can_move(self.__current_piece, new_pos):
            self.__clear_block()
            self.__current_piece_pos = new_pos
            return True
        else:
            return False

    def __can_move(self, block: list[list[int]], pos: list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)

        if pos[0] < 0 or pos[0] + block_width > self.WIDTH:
            return False
        elif pos[1] < 0 or pos[1] + block_height > self.HEIGHT:
            return False
        else:
            return not self.__check_overlapping(block, pos)

    def __check_overlapping(self, block: list[list[int]], pos: list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)

        for y in range(block_height):
            for x in range(block_width):
                if block[y][x] == 1:
                    if self.__grid[y + pos[1]][x + pos[0]][0] == 1:
                        return True
        return False
