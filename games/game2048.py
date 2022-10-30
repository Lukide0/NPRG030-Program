import queue
import random
from time import time
import terminal.colors as color
import terminal
import pynput.keyboard as keyboard

class Game2048:
    SIZE = 10

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
        self.__context.write_str_at(0, 0, "┌──────" + "┬──────"*(self.SIZE - 1) + "┐")

        row_str = "│      " * self.SIZE + "│"
        row_join_str = "├──────" + "┼──────"*(self.SIZE - 1) + "┤"

        for row in range(1, self.__window_size[1] - 1):
            if row % 4 == 0:
                self.__context.write_str_at(0, row, row_join_str)
            else:
                self.__context.write_str_at(0, row, row_str)

        self.__context.write_str_at(0, self.__window_size[1] - 1, "└──────" + "┴──────"*(self.SIZE - 1) + "┘")

        self.__listener = keyboard.Listener(on_release=self.__handle_keyboard_release)
        self.__keys = queue.SimpleQueue()

        self.__running = False

    def run(self):
        self.__running = True
        start = time()
        for i in range(1_000):
            for y in range(self.SIZE):
                for x in range(self.SIZE):
                    self.__write_cell(x,y, i % 11 + 1)
            self.__context.print_screen()

        print(time() - start)
        return
        self.__listener.start()
        
        """
        BUG: spatne vykresleni po pridani dalsiho. Useknuta leva cast bloku
        """

        while self.__running:

            if not self.__spawn_cell():
                self.__running = False
            self.__render()
            self.__tick()

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

        while self.__move(key):
            pass


    def __merge(self, move : int):
        """RIGHT -> FROM RIGHT TO LEFT"""

        if move == self.DOWN:
            for y in range(self.SIZE - 1):
                for x in range(self.SIZE):

                    if self.__grid[y][x] != 0:

                        if self.__grid[y][x] == self.__grid[y + 1][x]:

                            self.__grid[y + 1][x] += 1
                            self.__grid[y][x] = 0
                            
        elif move == self.UP:
            for y in range(self.SIZE - 1, 0, -1):
                for x in range(self.SIZE):

                    if self.__grid[y][x] != 0:

                        if self.__grid[y][x] == self.__grid[y - 1][x]:

                            self.__grid[y - 1][x] += 1
                            self.__grid[y][x] = 0
    
        elif move == self.RIGHT:
            for y in range(self.SIZE):
                for x in range(self.SIZE - 1):
    
                    if self.__grid[y][x] != 0:
        
                        if self.__grid[y][x] == self.__grid[y][x + 1]:
    
                            self.__grid[y][x + 1] += 1
                            self.__grid[y][x] = 0
        
        else:
            for y in range(self.SIZE):
                for x in range(self.SIZE - 1, 0, -1):

                    if self.__grid[y][x] != 0:
        
                        if self.__grid[y][x] == self.__grid[y][x - 1]:

                            self.__grid[y][x - 1] += 1
                            self.__grid[y][x] = 0
    def __move(self, move) -> bool:
        moved = False
        if move == self.DOWN:
            for y in range(self.SIZE - 1):
                for x in range(self.SIZE):
                    if self.__grid[y][x] != 0 and self.__grid[y + 1][x] == 0:
                        self.__grid[y + 1][x] = self.__grid[y][x]
                        self.__grid[y][x] = 0
                        moved = True
                            
        elif move == self.UP:
            for y in range(self.SIZE - 1, 0, -1):
                for x in range(self.SIZE):

                    if self.__grid[y][x] != 0 and self.__grid[y - 1][x] == 0:
                        self.__grid[y - 1][x] = self.__grid[y][x]
                        self.__grid[y][x] = 0
                        moved = True
    
        elif move == self.RIGHT:
            for y in range(self.SIZE):
                for x in range(self.SIZE - 1):
    
                    if self.__grid[y][x] != 0 and self.__grid[y][x + 1] == 0:
                        self.__grid[y][x + 1] = self.__grid[y][x]
                        self.__grid[y][x] = 0
                        moved = True
        
        else:
            for y in range(self.SIZE):
                for x in range(self.SIZE - 1, 0, -1):

                    if self.__grid[y][x] != 0 and self.__grid[y][x - 1] == 0:
                        self.__grid[y][x - 1] = self.__grid[y][x]
                        self.__grid[y][x] = 0
                        moved = True
        return moved
    def __spawn_cell(self) -> bool:
        tmp = []
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                if self.__grid[y][x] == 0:
                    tmp.append((x,y))
        if not tmp:
            return False

        x,y = random.choice(tmp)
        self.__grid[y][x] = 1

        return True

    def __write_cell(self, x : int, y : int, num : int):
        if num == 0:
            self.__context.write_str_at(1 + 7*x, 1+4*y, "#" * 6)
            self.__context.write_str_at(1 + 7*x, 2+4*y, "#" * 6)    
            self.__context.write_str_at(1 + 7*x, 3+4*y, "#" * 6)
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

        self.__context.write_str_at(1 + 7*x, 1+4*y, " " * 6, colors)
        self.__context.write_str_at(1 + 7*x, 2+4*y, " " * 6, colors)    
        self.__context.write_str_at(1 + 7*x, 3+4*y, " " * 6, colors)
        
        self.__context.write_str_at(2 + 7*x, 2+4*y, f"{num}", colors)

