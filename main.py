import curses
from curses import wrapper
import time
import json
import os
from argparse import ArgumentParser
import random

path = os.path.dirname(os.path.realpath(__file__))

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("file", nargs='?')
    parser.add_argument("-e", "--extract", action="store_true")
    parser.add_argument("-d", "--dictionary", action="store_true")
    parser.add_argument("-z", "--zen", action="store_true")
    parser.add_argument("-t", "--timer", type=int, nargs='?')
    parser.add_argument("-w", "--words", type=int, nargs='?', const=-1)
    return parser.parse_args()

def load_text(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        return " ".join([line.strip() for line in lines])

def load_config():
    with open(path + "/config.json") as f:
        return json.load(f)

def main(stdscr, args):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    CORRECT = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    INCORRECT = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    INCORRECT_SPACE = curses.color_pair(3)

    config = load_config()

    if args.zen:
        config["stat_height"] = 0

    if args.file:
        raw_text = load_text(args.file)
    else:
        if args.extract:
            raw_text = load_text(config["default_extract"].replace("$PATH", path))
        else:
            raw_text = load_text(config["default_dictionary"].replace("$PATH", path))
    
    # get or generate target_text
    target_text = ""
    if args.extract:
        target_text = raw_text
    else:
        words = raw_text.split()
        if args.words:
            if args.words == -1:
                args.words = config["default_words"]
            target_text = ' '.join([random.choice(words) for n in range(args.words)])
        else:
            if not args.timer:
                args.timer = config["default_timer"]
            while len(target_text) // (config["input_width"] - 2) < config["max_lines"]:
                target_text += random.choice(words) + ' '
    current_text = []

    words_completed = 0
    accuracy = 1
    raw_wpm = 0
    adj_wpm = 0
    progress = 0
    start_time = time.time()

    input_top = config["margin_top"] + config["stat_height"]

    input_pad = curses.newpad(
        (len(target_text) // (config["input_width"] - 2)) + 1,
        config["input_width"] - 2
    )

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
        # hide cursor
        curses.curs_set(0)

        # display input text
        input_pad.clear()
        input_pad.refresh(
            0, 
            0, 
            input_top + 1 + max(0, input_offset - input_scroll), 
            config["margin_left"] + 2,
            input_top + config["max_lines"], 
            config["margin_left"] + config["input_width"]
        )
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
        time_elapsed = max(time.time() - start_time, 1)
        raw_wpm = (len(current_text) / (time_elapsed / 60)) / 5
        adj_wpm = raw_wpm * accuracy
        progress = len(current_text) / len(target_text) if len(target_text) > 0 else 0

        if not args.zen:
            acc_text = f"ACC: {round(accuracy*100)}%"
            stdscr.addstr(
                config["margin_top"], config["margin_left"],
                "{:<20}".format(acc_text)
            )

            adj_wpm_text = f"WPM (ADJ): {round(adj_wpm)}"
            stdscr.addstr(
                config["margin_top"], config["margin_left"] + 20,
                "{:<20}".format(adj_wpm_text)
            )

            raw_wpm_text = f"WPM (RAW): {round(raw_wpm)}"
            stdscr.addstr(
                config["margin_top"], config["margin_left"] + 40,
                "{:<20}".format(raw_wpm_text)
            )

            if not args.extract and args.timer:
                time_text = f"TIME: {round(args.timer - time_elapsed)}"
                stdscr.addstr(
                    config["margin_top"], config["margin_left"] + 60,
                    "{:<20}".format(time_text)
                )
            else:
                progress_text = f"PRG: {round(progress*100)}%"
                stdscr.addstr(
                    config["margin_top"], config["margin_left"] + 60,
                    "{:<20}".format(progress_text)
                )

        # refresh screen
        stdscr.refresh()

        input_pad.refresh(
            max(0, input_scroll - input_offset), 
            0, 
            input_top + 1 + max(0, input_offset - input_scroll), 
            config["margin_left"] + 2,
            input_top + config["max_lines"], 
            config["margin_left"] + config["input_width"]
        )

        # return results on completion
        if len(current_text) >= len(target_text) or (args.timer and time_elapsed > args.timer):
            return {
                "accuracy": accuracy,
                "raw_wpm": raw_wpm,
                "adj_wpm": adj_wpm,
                "time_elapsed": time_elapsed
            }

        # show cursor
        curses.curs_set(1)

        # handle key input
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
    results = wrapper(main, parse_args())
    if results:
        for key, value in results.items():
            print(f"{key}: " + "{0:.2f}".format(value))
