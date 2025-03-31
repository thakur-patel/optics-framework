import curses
import curses.textpad
import ast
# Import updated ConfigHandler
from optics_framework.common.config_handler import ConfigHandler


class LoggerTUI:
    """
    A text-based UI for editing logger configuration.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        # Use the updated singleton instance of ConfigHandler
        self.config_handler = ConfigHandler.get_instance()
        self.options = list(self.config_handler.config.keys())
        self.current_index = 0
        self.init_curses()
        self.run()

    def init_curses(self):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def confirm_quit(self):
        height, width = self.stdscr.getmaxyx()
        win = curses.newwin(5, 50, height // 2 - 2, width // 2 - 25)
        win.box()
        win.addstr(1, 2, "Quit without saving? (y/n)", curses.color_pair(2))
        win.refresh()

        while True:
            key = win.getch()
            if key in [ord("y"), ord("Y")]:
                return True
            elif key in [ord("n"), ord("N")]:
                return False

    def run(self):
        while True:
            self.stdscr.clear()
            self.display_menu()
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                self.current_index = (
                    self.current_index - 1) % len(self.options)
            elif key == curses.KEY_DOWN:
                self.current_index = (
                    self.current_index + 1) % len(self.options)
            elif key == ord(" "):
                self.modify_value()
            elif key == ord("s"):
                try:
                    self.config_handler.save_config()
                except Exception as e:
                    self.show_error_message(f"Error saving config: {e}")
                exit(0)
            elif key == ord("q"):
                if self.confirm_quit():
                    exit(0)

    def display_menu(self):
        height, width = self.stdscr.getmaxyx()
        title = "Logger Configuration"
        self.stdscr.addstr(
            1,
            (width // 2 - len(title) // 2),
            title,
            curses.A_BOLD | curses.color_pair(2),
        )

        # Always fetch the latest config dynamically
        config = self.config_handler.config

        for idx, key in enumerate(self.options):
            prefix = "> " if idx == self.current_index else "  "
            value = str(config[key])  # Fetch latest value
            color = (
                curses.color_pair(
                    1) if idx == self.current_index else curses.A_NORMAL
            )
            self.stdscr.addstr(idx + 3, 2, f"{prefix}{key}: {value}", color)

        footer = "[SPACE] Edit  [S] Save  [Q] Quit"
        self.stdscr.addstr(
            height - 2, (width // 2 - len(footer) //
                         2), footer, curses.color_pair(3)
        )

    def modify_value(self):
        key = self.options[self.current_index]
        config = self.config_handler.config  # Fetch latest config

        if isinstance(config[key], bool):
            config[key] = not config[key]
        else:
            new_value = self.get_validated_input(config[key])
            if new_value is not None:
                config[key] = new_value

    def get_text_input(self, current_value):
        height, width = self.stdscr.getmaxyx()
        win = curses.newwin(5, 50, height // 2 - 2, width // 2 - 25)
        win.box()
        win.addstr(1, 2, "Enter new value:", curses.color_pair(2))
        win.addstr(2, 2, f"[Current: {current_value}]", curses.color_pair(1))
        win.refresh()

        curses.echo()
        input_value = ""
        cursor_x = 2

        while True:
            win.addstr(3, cursor_x, input_value)
            win.refresh()
            key = win.getch()

            if key in [10, 13]:  # Enter key
                break
            elif key in [127, curses.KEY_BACKSPACE]:
                if input_value:
                    input_value = input_value[:-1]
                    win.addstr(3, cursor_x, " " * 48)
            elif key == ord("q"):
                curses.noecho()
                if self.confirm_quit():
                    exit(0)
                else:
                    win.clear()
                    win.box()
                    win.addstr(1, 2, "Enter new value:", curses.color_pair(2))
                    win.addstr(
                        2, 2, f"[Current: {current_value}]", curses.color_pair(
                            1)
                    )
                    win.refresh()
            else:
                input_value += chr(key)

        curses.noecho()
        return input_value.strip() if input_value else current_value

    def get_validated_input(self, current_value):
        while True:
            new_value = self.get_text_input(current_value)
            try:
                # For list types, use ast.literal_eval to parse user input
                if isinstance(current_value, list):
                    parsed = ast.literal_eval(new_value)
                    if isinstance(parsed, list):
                        return parsed
                    else:
                        raise ValueError
                else:
                    # Attempt to cast new_value to the type of the current value
                    return type(current_value)(new_value)
            except Exception:
                self.show_error_message("Invalid input!")

    def show_error_message(self, message):
        height, width = self.stdscr.getmaxyx()
        win = curses.newwin(
            3, len(message) + 6, height // 2, width // 2 - (len(message) // 2)
        )
        win.box()
        win.addstr(1, 2, message, curses.color_pair(2))
        win.refresh()
        curses.napms(1500)


def main():
    curses.wrapper(LoggerTUI)


if __name__ == "__main__":
    main()
