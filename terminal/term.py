import os
import terminal.colors as colors


class Term:
    def __init__(self):

        # commands
        self.__command_buffer: list[str] = []

        # current frame
        self.__front_screen_buffer: list[str] = []

        # previous frame
        self.__back_screen_buffer: list[str] = []

        # empty buffer
        self.__clean_screen_buffer: list[str] = []

        # (width, height)
        self.__window_size: tuple[int, int] = (0, 0)

        self.__colors: list[list[int]] = []

        self.__buffer_size: int = 0

    def setup(self, width: int, height: int, title: str = ""):

        assert width > 0 and height > 0

        # windows
        if os.name == "nt":
            os.system(" ")

        print(f"\033[8;{height};{width}t", end="")

        self.__window_size = (width, height)
        self.__buffer_size = width * height

        # set window title
        if len(title) != 0:
            print(f"\033]0;{title}\007", end="")

        # clear screen and move cursor home
        print("\033[2J\033[H", end="")

        self.__clean_screen_buffer = [" "] * self.__buffer_size
        self.__front_screen_buffer = self.__clean_screen_buffer[:]
        self.__back_screen_buffer = self.__clean_screen_buffer[:]
        self.__colors = [
            [colors.COLOR_FG_DEFAULT, colors.COLOR_BG_DEFAULT]
            for _ in range(self.__buffer_size)
        ]

    def __index_from(self, x: int, y: int) -> int:
        return (y * self.__window_size[0]) + x

    # returns (y, x)
    def __get_yx_from_index(self, i: int) -> tuple[int, int]:
        return divmod(i, self.__window_size[0])

    def __del__(self):
        print(f"\033[{colors.STYLE_RESET}m")

    # ------------------------------ Screen ------------------------------ #
    def set_title(self, title: str):
        """
        Sets the terminal title
        """
        self.__command_buffer.append(f"\033]0;{title}\007")

    def clear_buffers(self):
        """
        Clears the front screen buffer and the colors buffer
        """
        self.__colors = [
            [colors.COLOR_FG_DEFAULT, colors.COLOR_BG_DEFAULT]
            for _ in range(self.__buffer_size)
        ]
        self.__front_screen_buffer = self.__clean_screen_buffer[:]

    def set_screen_buffer(self, buff: list[str]):
        """
        Sets the front screen buffer to custom
        """
        self.__front_screen_buffer = buff

    def get_screen_buffer(self) -> list[str]:
        """
        Returns the front screen buffer
        """
        return self.__front_screen_buffer

    def get_window_size(self) -> tuple[int, int]:
        """
        Returns the window size from the setup
        """
        return self.__window_size

    def write_char_at(
        self,
        x: int,
        y: int,
        char: str,
        colors: list[int] = [colors.COLOR_FG_DEFAULT, colors.COLOR_BG_DEFAULT],
    ):
        """
        Writes the single character into front buffer
        """
        index = self.__index_from(x, y)
        if self.__colors[index][0] != colors[0] or self.__colors[index][1] != colors[1]:
            self.__front_screen_buffer[index] = f"\033[{colors[0]};{colors[1]}m{char}"
            self.__colors[index] = colors
        else:
            self.__front_screen_buffer[index] = char

    def write_str_at(
        self,
        x: int,
        y: int,
        string: str,
        colors: list[int] = [colors.COLOR_FG_DEFAULT, colors.COLOR_BG_DEFAULT],
    ):
        """
        Writes the entire string into front buffer
        """
        index = self.__index_from(x, y)

        if self.__colors[index][0] != colors[0] or self.__colors[index][0] != colors[1]:
            self.__front_screen_buffer[index] = f"\033[{colors[0]};{colors[1]}m{string[0]}"
            self.__colors[index] = colors
        else:
            self.__front_screen_buffer[index] = string[0]

        index += 1
        for char in string[1:]:
            self.__front_screen_buffer[index] = char
            # HACK: force to update
            self.__back_screen_buffer[index] = ""
            self.__colors[index] = colors
            index += 1
    
    def print_screen(self):
        """
        Only prints the front buffer
        """
        tmp_commands: list[str] = ["\0337", "\033[H"]
        prev_index : int = 0

        for i in range(self.__buffer_size):
            # different content
            if self.__back_screen_buffer[i] != self.__front_screen_buffer[i]:
                if i - 1 == prev_index:
                    tmp_commands.append(self.__front_screen_buffer[i])
                else:
                    y, x = self.__get_yx_from_index(i)
                    tmp_commands.append(
                        f"\033[{y + 1};{x + 1}f{self.__front_screen_buffer[i]}"
                    )
                prev_index = i

        self.__back_screen_buffer = self.__front_screen_buffer[:]

        tmp_commands.append("\0338")
        print("".join(tmp_commands), end="")

    # ------------------------------ Commands ------------------------------ #
    def erase_screen_from_cursor(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[J")

    def erase_screen_to_cursor(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[1J")

    def erase_screen(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[2J")

    def erase_line_from_cursor(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[K")

    def erase_line_to_cursor(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[1K")

    def erase_line(self):
        """
        Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[2K")

    def clear(self):
        """
        Adds clear command to the buffer. Doesn't effect the front buffer
        """
        self.__command_buffer.append("\033[2J\033[H")

    def execute_commands(self):
        """
        Executes all commands in the buffer
        """
        print("".join(self.__command_buffer), end="", flush=True)
        self.__command_buffer.clear()

    # ------------------------------ Commands: Cursor ------------------------------ #

    def cursor_move_home(self):
        self.__command_buffer.append(f"\033[H")

    def cursor_move(self, x: int, y: int):
        self.__command_buffer.append(f"\033[{y};{x}f")

    def cursor_move_up(self, i: int = 1):
        self.__command_buffer.append(f"\033[{i}A")

    def cursor_move_down(self, i: int = 1):
        self.__command_buffer.append(f"\033[{i}B")

    def cursor_move_forward(self, i: int = 1):
        self.__command_buffer.append(f"\033[{i}C")

    def cursor_move_backward(self, i: int = 1):
        self.__command_buffer.append(f"\033[{i}D")

    def cursor_save(self):
        self.__command_buffer.append("\0337")

    def cursor_restore(self):
        self.__command_buffer.append("\0338")
