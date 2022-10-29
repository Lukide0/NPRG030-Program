import random
from time import time
import terminal.colors as color
import terminal

class Game2048:
    SIZE = 4

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

    def run(self):
        self.__context.print_screen()
        while self.__spawn_cell():
            self.__context.print_screen()
            input()
            self.__context.cursor_move_up()
            self.__context.execute_commands()

        
    def __spawn_cell(self) -> bool:
        tmp = []
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                if self.__grid[y][x] == 0:
                    tmp.append((x,y))
        if not tmp:
            return False

        x,y = random.choice(tmp)

        self.__write_cell(x,y, 1)
        self.__grid[y][x] = 1

        return True

    def __write_cell(self, x : int, y : int, num : int):
        bg = color.COLOR_BG_RED
        
        if num == 1:
            bg = color.COLOR_BG_RED
        elif num == 2:
            bg = color.COLOR_BG_RED_BRIGHT
        elif num == 3:
            bg = color.COLOR_BG_YELLOW
        elif num == 4:
            bg = color.COLOR_BG_CYAN
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

