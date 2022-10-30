import queue
import random
from time import sleep
import terminal.colors as color
import terminal
import pynput.keyboard as keyboard


class Game2048:
    SIZE = 15

    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    EXIT = 4

    def __init__(self):
        self.__context = terminal.Term()
        self.__context.setup((self.SIZE - 1) * 7 + 8, (self.SIZE * 4) + 1, "2048")

        self.__window_size = self.__context.get_window_size()

        self.__grid = [[0 for x in range(self.SIZE)] for y in range(self.SIZE)]

        # create grid
        self.__context.write_str_at(0, 0, "┌──────" + "┬──────" * (self.SIZE - 1) + "┐")

        row_str = "│      " * self.SIZE + "│"
        row_join_str = "├──────" + "┼──────" * (self.SIZE - 1) + "┤"

        for row in range(1, self.__window_size[1] - 1):
            if row % 4 == 0:
                self.__context.write_str_at(0, row, row_join_str)
            else:
                self.__context.write_str_at(0, row, row_str)

        self.__context.write_str_at(
            0, self.__window_size[1] - 1, "└──────" + "┴──────" * (self.SIZE - 1) + "┘"
        )

        self.__listener = keyboard.Listener(on_release=self.__handle_keyboard_release)
        self.__keys = queue.SimpleQueue()

        self.__running = False

    def run(self):
        self.__running = True
        self.__listener.start()
        """
        BUG: spatne vykresleni po pridani dalsiho. Useknuta leva cast bloku
        """

        while self.__running:
            if not self.__spawn_cell():
                self.__running = False
            self.__render()
            sleep(0.2)
            self.__merge(random.choice([self.LEFT, self.RIGHT, self.DOWN, self.UP]))
            # self.__tick()

        self.__listener.stop()
        self.__context.clear_styles()

    def __handle_keyboard_release(self, code):
        if code == keyboard.Key.left:
            self.__keys.put(self.LEFT)
        elif code == keyboard.Key.right:
            self.__keys.put(self.RIGHT)
        elif code == keyboard.Key.up:
            self.__keys.put(self.UP)
        elif code == keyboard.Key.down:
            self.__keys.put(self.DOWN)
        elif code == keyboard.Key.esc:
            self.__keys.put(self.EXIT)
            self.__running = False

    def __render(self):
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                self.__write_cell(x, y, self.__grid[y][x])
        self.__context.print_screen()

    def __tick(self):

        key = self.__keys.get()
        if key == self.EXIT:
            return

        self.__merge(key)

    def __merge(self, move: int):
        if move == self.DOWN:
            for x in range(self.SIZE):
                for y in range(self.SIZE - 1, -1, -1):

                    if self.__grid[y][x] == 0:
                        continue

                    # move down
                    move_y = y
                    while move_y < self.SIZE - 1 and self.__grid[move_y + 1][x] == 0:
                        move_y += 1

                    val = self.__grid[y][x]

                    self.__grid[y][x] = 0
                    self.__grid[move_y][x] = val

                    # merge cells
                    tmp_y = y - 1
                    while tmp_y >= 0:
                        if self.__grid[tmp_y][x] == 0:
                            tmp_y -= 1
                            continue
                        elif self.__grid[tmp_y][x] == val:
                            self.__grid[move_y][x] += 1
                            self.__grid[tmp_y][x] = 0
                        break
                    # skip empty cells
                    y = tmp_y

        elif move == self.UP:
            for x in range(self.SIZE):
                for y in range(self.SIZE):
                    if self.__grid[y][x] == 0:
                        continue

                    # move up
                    move_y = y
                    while move_y > 0 and self.__grid[move_y - 1][x] == 0:
                        move_y -= 1

                    val = self.__grid[y][x]

                    self.__grid[y][x] = 0
                    self.__grid[move_y][x] = val

                    # merge cells
                    tmp_y = y + 1
                    while tmp_y <= self.SIZE - 1:
                        if self.__grid[tmp_y][x] == 0:
                            tmp_y += 1
                            continue
                        elif self.__grid[tmp_y][x] == val:
                            self.__grid[move_y][x] += 1
                            self.__grid[tmp_y][x] = 0
                        break
                    # skip empty cells
                    y = tmp_y

        elif move == self.RIGHT:
            for y in range(self.SIZE):
                for x in range(self.SIZE - 1, -1, -1):

                    if self.__grid[y][x] == 0:
                        continue

                    # move right
                    move_x = x
                    while move_x < self.SIZE - 1 and self.__grid[y][move_x + 1] == 0:
                        move_x += 1

                    val = self.__grid[y][x]

                    self.__grid[y][x] = 0
                    self.__grid[y][move_x] = val

                    # merge cells
                    tmp_x = x - 1
                    while tmp_x >= 0:
                        if self.__grid[y][tmp_x] == 0:
                            tmp_x -= 1
                            continue
                        elif self.__grid[y][tmp_x] == val:
                            self.__grid[y][move_x] += 1
                            self.__grid[y][tmp_x] = 0
                        break
                    # skip empty cells
                    x = tmp_x

        else:
            for y in range(self.SIZE):
                for x in range(self.SIZE):
                    if self.__grid[y][x] == 0:
                        continue

                    # move left
                    move_x = x
                    while move_x > 0 and self.__grid[y][move_x - 1] == 0:
                        move_x -= 1

                    val = self.__grid[y][x]

                    self.__grid[y][x] = 0
                    self.__grid[y][move_x] = val

                    # merge cells
                    tmp_x = x + 1
                    while tmp_x <= self.SIZE - 1:
                        if self.__grid[y][tmp_x] == 0:
                            tmp_x += 1
                            continue
                        elif self.__grid[y][tmp_x] == val:
                            self.__grid[y][move_x] += 1
                            self.__grid[y][tmp_x] = 0
                        break
                    # skip empty cells
                    x = tmp_x

    def __spawn_cell(self) -> bool:
        tmp = []
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                if self.__grid[y][x] == 0:
                    tmp.append((x, y))
        if not tmp:
            return False

        x, y = random.choice(tmp)
        self.__grid[y][x] = 1

        return True

    def __write_cell(self, x: int, y: int, num: int):
        if num == 0:
            self.__context.write_str_at(1 + 7 * x, 1 + 4 * y, " " * 6)
            self.__context.write_str_at(1 + 7 * x, 2 + 4 * y, " " * 6)
            self.__context.write_str_at(1 + 7 * x, 3 + 4 * y, " " * 6)
            return

        bg = color.COLOR_BG_RED

        if num == 1:
            bg = color.COLOR_BG_RED
        elif num == 2:
            bg = color.COLOR_BG_RED_BRIGHT
        elif num == 3:
            bg = color.COLOR_BG_YELLOW
        elif num == 4:
            bg = color.COLOR_BG_YELLOW_BRIGHT
        elif num == 5:
            bg = color.COLOR_BG_GREEN
        elif num == 6:
            bg = color.COLOR_BG_GREEN_BRIGHT
        elif num == 7:
            bg = color.COLOR_BG_BLUE
        elif num == 8:
            bg = color.COLOR_BG_BLUE_BRIGHT
        elif num == 9:
            bg = color.COLOR_BG_MAGENTA
        elif num == 10:
            bg = color.COLOR_BG_MAGENTA_BRIGHT
        else:
            bg = color.COLOR_BG_BLACK_BRIGHT

        colors = [color.COLOR_FG_WHITE, bg]
        num = 2**num

        self.__context.write_str_at(1 + 7 * x, 1 + 4 * y, " " * 6, colors)
        self.__context.write_str_at(1 + 7 * x, 2 + 4 * y, " " * 6, colors)
        self.__context.write_str_at(1 + 7 * x, 3 + 4 * y, " " * 6, colors)

        self.__context.write_str_at(2 + 7 * x, 2 + 4 * y, f"{num}", colors)
