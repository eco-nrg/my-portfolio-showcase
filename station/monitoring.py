import curses
from datetime import datetime
from kv.redis_kv import models
from py_scripts.schedule import Interval
from textwrap import TextWrapper


def print_dict(screen, data: dict, max_y, max_x):
    if len(data.keys()) == 0:
        return
    col_width = max(len(k) for k in data.keys()) + 2
    screen.erase()
    for k in sorted(data.keys()):
        screen.addstr(max_y, max_x, f"{k}:", curses.A_NORMAL)

        wrapper = TextWrapper(width=80)
        lines = wrapper.wrap(data.get(k, ''))
        for line in lines:
            screen.addstr(max_y, max_x + col_width, line, curses.A_NORMAL)
            max_y += 1
    screen.refresh()


def main(stdscr):
    # Clear screen
    curses.curs_set(0)
    stdscr.clear()
    stdscr.timeout(100)

    data = models.get_all()
    data_interval = Interval(1)

    ch = ''
    while ch != ord('q') and ch != ord('Q'):
        if data_interval.check():
            data = models.get_all()

        now = datetime.now().isoformat()
        stdscr.addstr(1, 1, now, curses.A_NORMAL)

        print_dict(stdscr, data, 3, 1)

        ch = stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
