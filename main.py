import games

from terminal.colors import *
from terminal.term import Term


if __name__ == "__main__":
    term = Term()
    game = games.GameTetris(term)
    game.run()
    input()