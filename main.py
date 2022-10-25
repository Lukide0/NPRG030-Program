from time import time
import terminal

input()
term = terminal.Term()
term.setup(50, 5)
term.set_title("AHOJ")
term.print_screen()

start = time()

for _ in range(100_000):
    term.execute_commands()
    term.set_writting_style(terminal.COLOR_FG_RED)
    term.write_str_at(20, 0, f"{_}")

    term.print_screen()

print("\n", time() - start)