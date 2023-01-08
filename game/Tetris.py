import random
import terminal
import sys
import os

from queue import SimpleQueue
from time import time
from terminal import colors
from pynput import keyboard


class GameTetris:
    WIDTH = 15
    HEIGHT = 30
    MAX_FALLING_SPEED = 0.05
    START_FALLING_SPEED = 0.4
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
        [
            [1, 1, 1, 1],
        ],
        [
            [1, 0, 0],
            [1, 1, 1],
        ],
        [
            [0, 0, 1],
            [1, 1, 1],
        ],
    ]

    NONE = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3
    ROTATE = 4
    EXIT = 5

    def __init__(self, term: terminal.Term):

        self._context = term
        self._context.setup(
            self.WIDTH * 2 + 2 + self.MARGIN + 2 + self.SIDEBAR_WIDTH,
            self.HEIGHT + 2,
            "Tetris",
        )

        self._context.cursor_hide()
        self._context.execute_commands()

        if os.name != "nt":
            import curses

            curses.initscr()
            curses.noecho()

    def _handle_keyboard_release(self, code):

        if code == keyboard.Key.left:
            self._keys.put(self.MOVE_LEFT)
        elif code == keyboard.Key.right:
            self._keys.put(self.MOVE_RIGHT)
        elif code == keyboard.Key.up:
            self._keys.put(self.ROTATE)
        elif code == keyboard.Key.down:
            self._keys.put(self.MOVE_DOWN)
        elif code == keyboard.Key.esc:
            self._keys.put(self.EXIT)
            self._running = False

    def _prepare_board(self):

        self._current_color: int = None
        self._current_piece = []

        self._falling_speed = self.START_FALLING_SPEED

        self._next_color = self._random_color()
        self._next_piece = random.choice(self.PIECES)

        self._current_piece_pos: list[int] = [0, 0]
        self._shadow_pos_y: int = 0

        self._current_piece_height: int = 0
        self._current_piece_width: int = 0

        self._grid: list[list[int]] = [
            [[0, None] for x in range(self.WIDTH)] for y in range(self.HEIGHT)
        ]
        self._running = False

        self._listener = keyboard.Listener(on_press=self._handle_keyboard_release)
        self._keys = SimpleQueue()

        # board border
        width = self.WIDTH * 2
        border_width = self.WIDTH - 4

        self._context.write_str_at(
            0,
            0,
            "┏" + "━" * border_width + "┫" + "Tetris" + "┣" + "━" * border_width + "┓",
        )
        for y in range(0, self.HEIGHT):
            self._context.write_str_at(0, y + 1, "┃" + " " * width + "┃")

        self._context.write_str_at(0, self.HEIGHT + 1, "┗" + "━" * width + "┛")
        self._context.print_screen()

        # next piece border
        offset = width + 2 + self.MARGIN
        line_width = self.SIDEBAR_WIDTH

        self._next_piece_offset = offset

        self._context.write_str_at(
            offset,
            0,
            "┏"
            + "━" * ((line_width - 6) // 2)
            + "┫"
            + "Next"
            + "┣"
            + "━" * ((line_width - 6) // 2)
            + "┓\n",
        )
        for y in range(0, 4):
            self._context.write_str_at(offset, y + 1, "┃" + " " * line_width + "┃\n")

        self._context.write_str_at(offset, 5, "┗" + "━" * line_width + "┛\n")

        scope_start_y = self.MARGIN // 2 + 5
        # score
        self._score: int = 0
        self._score_pos = [offset + 9, scope_start_y + 1]
        self._lines: int = 0
        self._level: int = 0

        self._context.write_str_at(
            offset, scope_start_y, "┏" + "━" * line_width + "┓\n"
        )
        self._context.write_str_at(
            offset, scope_start_y + 1, f"┃ Score: {self._score:07d} ┃\n"
        )
        self._context.write_str_at(
            offset, scope_start_y + 2, f"┃ Lines: {self._lines:07d} ┃\n"
        )
        self._context.write_str_at(
            offset, scope_start_y + 3, f"┃ Level: {self._level:07d} ┃\n"
        )
        self._context.write_str_at(
            offset, scope_start_y + 4, "┗" + "━" * line_width + "┛\n"
        )

        self._context.print_screen()

    def run(self):
        # print borders
        self._prepare_board()
        self._running = True

        # 1.st block
        self._spawn_block()
        self._create_next_piece()

        self._print_block(self._current_piece_pos)

        self._listener.start()

        start = time()
        delta = 0

        while self._running:
            delta = time() - start

            try:
                # throws EmptyException
                key = self._keys.get(False, 0.3)
                if key == self.EXIT:
                    break

                if key == self.ROTATE:
                    self._rotate()
                else:
                    self._move(key)
            except:
                pass

            can_cast_shadow = self._cast_shadow()

            if delta > self._falling_speed:
                start = time()
                delta = 0

                if not self._move(self.MOVE_DOWN):
                    self._place_block()
                    self._spawn_block()
                    self._create_next_piece()
                    self._shadow_pos_y = 0

                    if self._check_overlapping(
                        self._current_piece, self._current_piece_pos
                    ):
                        self._running = False
                        break

            self._print_block(self._current_piece_pos)
            if self._shadow_pos_y != self._current_piece_pos[1] and can_cast_shadow:
                self._clear_block([self._current_piece_pos[0], self._shadow_pos_y])

        self._listener.stop()
        self._context.clear_styles()

    def _cast_shadow(self) -> bool:

        used_indexes: set[int] = set()
        min_depth = self.HEIGHT - 1
        pos_x, pos_y = self._current_piece_pos

        for y in range(self._current_piece_height - 1, -1, -1):
            for x in range(self._current_piece_width):
                if x in used_indexes or self._current_piece[y][x] == 0:
                    continue

                used_indexes.add(x)
                tmp_y = pos_y

                while (
                    tmp_y < min_depth
                    and y + tmp_y < self.HEIGHT - 1
                    and self._grid[y + tmp_y + 1][x + pos_x][0] == 0
                ):
                    tmp_y += 1

                if min_depth > tmp_y:
                    min_depth = tmp_y

        if min_depth - self._current_piece_height >= self._current_piece_pos[1]:
            self._shadow_pos_y = min_depth
            self._print_block([pos_x, min_depth], "▓▓")
            return True
        else:
            return False

    def _create_next_piece(self):
        # clear previous
        height = len(self._next_piece)
        width = len(self._next_piece[0])

        offset_x = (self.SIDEBAR_WIDTH - 3) // 2 - width

        for y in range(height):
            for x in range(width):
                if self._next_piece[y][x] == 1:
                    self._context.write_str_at(
                        self._next_piece_offset + 3 + x * 2 + offset_x, y + 2, "  "
                    )

        self._next_piece = random.choice(self.PIECES)
        self._next_color = self._random_color()

        height = len(self._next_piece)
        width = len(self._next_piece[0])

        offset_x = (self.SIDEBAR_WIDTH - 3) // 2 - width
        for y in range(height):
            for x in range(width):
                if self._next_piece[y][x] == 1:
                    self._context.write_str_at(
                        self._next_piece_offset + 3 + x * 2 + offset_x,
                        y + 2,
                        "██",
                        [self._next_color, colors.COLOR_BG_DEFAULT],
                    )

        self._context.print_screen()

    def _place_block(self):
        pos_x = self._current_piece_pos[0]
        pos_y = self._current_piece_pos[1]

        remove_indexes = []
        for y in range(self._current_piece_height):
            for x in range(self._current_piece_width):
                if self._current_piece[y][x] != 0:
                    self._grid[y + pos_y][x + pos_x][0] = 1
                    self._grid[y + pos_y][x + pos_x][1] = self._current_color

            remove = True
            for x in range(self.WIDTH):
                if self._grid[y + pos_y][x][0] == 0:
                    remove = False
                    break

            if remove:
                remove_indexes.append(y + pos_y)

        if not remove_indexes:
            return

        removed_lines_count = len(remove_indexes)

        self._lines += removed_lines_count
        self._level = self._lines // 10
        self._falling_speed = max(
            self.START_FALLING_SPEED - self._level * 0.05, self.MAX_FALLING_SPEED
        )

        if removed_lines_count == 1:
            self._score += removed_lines_count * 40 * (self._level + 1)
        elif removed_lines_count == 2:
            self._score += removed_lines_count * 100 * (self._level + 1)
        elif removed_lines_count == 3:
            self._score += removed_lines_count * 300 * (self._level + 1)
        else:
            self._score += removed_lines_count * 1200 * (self._level + 1)

        x, y = self._score_pos
        self._context.write_str_at(x, y, f"{self._score:07d}")
        self._context.write_str_at(x, y + 1, f"{self._lines:07d}")
        self._context.write_str_at(x, y + 2, f"{self._level:07d}")

        for index in remove_indexes:
            self._grid.pop(index)
            self._grid.insert(0, [[0, None] for i in range(self.WIDTH)])

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self._grid[y][x][0] != 0:
                    self._write_cell(x, y, self._grid[y][x][1], "██")
                else:
                    self._clear_cell(x, y)

    def _spawn_block(self):
        self._current_piece = self._next_piece
        self._current_piece_pos = [self.WIDTH // 2, 0]
        self._current_color = self._next_color

        self._current_piece_width = len(self._current_piece[0])
        self._current_piece_height = len(self._current_piece)

    def _random_color(self):
        color = random.choice(colors.ALL_FG_COLORS)
        if color == colors.COLOR_FG_BLACK or color == colors.COLOR_FG_DEFAULT:
            return colors.COLOR_FG_BLACK_BRIGHT
        else:
            return color

    def _clear_cell(self, x: int, y: int):
        self._context.write_str_at(x * 2 + 1, y + 1, "  ")

    def _write_cell(self, x: int, y: int, color: int, char: str):
        self._context.write_str_at(
            x * 2 + 1, y + 1, char, [color, colors.COLOR_BG_DEFAULT]
        )

    def _print_block(self, pos: list[int], char: str = "██"):
        for y in range(len(self._current_piece)):
            for x in range(len(self._current_piece[y])):
                if self._current_piece[y][x] != 0:
                    self._write_cell(x + pos[0], y + pos[1], self._current_color, char)
        self._context.print_screen()

    def _clear_block(self, pos: list[int]):
        for y in range(len(self._current_piece)):
            for x in range(len(self._current_piece[y])):
                if self._current_piece[y][x] != 0:
                    self._clear_cell(x + pos[0], y + pos[1])

    def _rotate(self):
        # rotate list
        rotated = list(map(list, zip(*self._current_piece[::-1])))

        if self._can_move(rotated, self._current_piece_pos):
            self._clear_block(self._current_piece_pos)
            self._current_piece = rotated
            self._current_piece_height = len(self._current_piece)
            self._current_piece_width = len(self._current_piece[0])

    def _move(self, move: int) -> bool:
        new_pos = self._current_piece_pos[:]

        if move == self.MOVE_DOWN:
            new_pos[1] += 1
        elif move == self.MOVE_LEFT:
            new_pos[0] -= 1
        else:
            new_pos[0] += 1

        if self._can_move(self._current_piece, new_pos):
            self._clear_block(self._current_piece_pos)
            self._current_piece_pos = new_pos
            return True
        else:
            return False

    def _can_move(self, block: list[list[int]], pos: list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)

        if pos[0] < 0 or pos[0] + block_width > self.WIDTH:
            return False
        elif pos[1] < 0 or pos[1] + block_height > self.HEIGHT:
            return False
        else:
            return not self._check_overlapping(block, pos)

    def _check_overlapping(self, block: list[list[int]], pos: list[int]) -> bool:
        block_width = len(block[0])
        block_height = len(block)

        for y in range(block_height):
            for x in range(block_width):
                if block[y][x] == 1:
                    if self._grid[y + pos[1]][x + pos[0]][0] == 1:
                        return True
        return False
