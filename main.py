import game

from terminal.colors import *
from terminal.Term import Term


if __name__ == "__main__":
    term = Term()
    tetris = game.GameTetris(term)
    tetris.run()
