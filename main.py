import curses
from curses import wrapper
import time
import json

def load_text():
    with open('texts/sample.txt', 'r') as f:
        lines = f.readlines()
        return " ".join([line.strip() for line in lines])

def main(stdscr):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    CORRECT = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    INCORRECT = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    INCORRECT_SPACE = curses.color_pair(3)

    with open("config.json") as f:
        config = json.load(f)

    target_text = load_text()
    current_text = []

    words = len(target_text.split(' '))
    words_completed = 0
    accuracy = 1
    raw_wpm = 0
    adj_wpm = 0
    start_time = time.time()

    input_top = config["margin_top"] + config["stat_height"]

    input_pad = curses.newpad(100, config["input_width"] - 2)

    input_scroll = 0
    input_offset = 2

    stdscr.clear()

    stdscr.addstr(
        input_top, config["margin_left"],
        '╭' + ('─'*config["input_width"]) + '╮'
    )
    for i in range(config["max_lines"]):
        if i == config["max_lines"] // 2:
            stdscr.addstr(input_top + 1 + i, config["margin_left"], '│>')
            stdscr.addstr(
                input_top + 1 + i, config["margin_left"] + config["input_width"], '<│'
            )
        else:
            stdscr.addstr(input_top + 1 + i, config["margin_left"], '│')
            stdscr.addstr(
                input_top + 1 + i, config["margin_left"] + config["input_width"] + 1, '│'
            )
    stdscr.addstr(
        input_top + config["max_lines"] + 1, config["margin_left"],
        '╰' + ('─'*config["input_width"]) + '╯'
    )

    text_width = config["input_width"] - 2
    while True:
        input_pad.clear()
        input_pad.addstr(target_text, curses.A_DIM)
        input_scroll = len(current_text) // text_width

        correct_chars = 0
        for i, c in enumerate(current_text):
            correct_char = target_text[i]
            if c == correct_char:
                color = CORRECT
                correct_chars += 1
            else:
                color = INCORRECT
            if correct_char == ' ' and c != correct_char:
                color = INCORRECT_SPACE
            input_pad.addstr(i // text_width, i % text_width, correct_char, color)
        
        # display stats
        accuracy = correct_chars / len(current_text) if correct_chars > 0 else 1
        acc_text = f"ACC: {int(accuracy*100)}%"
        stdscr.addstr(
            config["margin_top"], config["margin_left"],
            "{:<20}".format(acc_text)
        )

        time_elapsed = max(time.time() - start_time, 1)
        time_text = f"TIME: {round(time_elapsed)}"
        stdscr.addstr(
            config["margin_top"], config["margin_left"] + 60,
            "{:<20}".format(time_text)
        )

        raw_wpm = (len(current_text) / (time_elapsed / 60)) / 5
        raw_wpm_text = f"WPM (RAW): {round(raw_wpm)}"
        stdscr.addstr(
            config["margin_top"], config["margin_left"] + 20,
            "{:<20}".format(raw_wpm_text)
        )

        adj_wpm = raw_wpm * accuracy
        adj_wpm_text = f"WPM (ADJ): {round(adj_wpm)}"
        stdscr.addstr(
            config["margin_top"], config["margin_left"] + 40,
            "{:<20}".format(adj_wpm_text)
        )

        stdscr.refresh()

        input_pad.refresh(
            max(0, input_scroll - input_offset), 
            0, 
            input_top + 1 + max(0, input_offset - input_scroll), 
            config["margin_left"] + 2,
            input_top + config["max_lines"], 
            config["margin_left"] + config["input_width"]
        )

        if len(current_text) >= len(target_text):
            return {
                "accuracy": accuracy,
                "raw_wpm": raw_wpm,
                "adj_wpm": adj_wpm,
                "time_elapsed": time_elapsed
            }

        try:
            key = stdscr.getkey()
        except:
            continue
        
        try:
            if ord(key) == 27:
                break
        except:
            pass

        if key in ("KEY_BACKSPACE", "\b", "\x7f"):
            if len(current_text) > 0:
                current_text.pop()
        elif len(current_text) < len(target_text):
            current_text.append(key)
    
    return

if __name__ == "__main__":    
    results = wrapper(main)
    if results:
        for key, value in results.items():
            print(f"{key}: " + "{0:.2f}".format(value))
    else:
        print("program cancelled. no data.")


