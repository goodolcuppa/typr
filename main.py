import curses
from curses import wrapper
import time
import json
import os
from argparse import ArgumentParser
import random

PATH = os.path.dirname(os.path.realpath(__file__))

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("file", nargs='?')
    parser.add_argument("-e", "--extract", action="store_true")
    parser.add_argument("-d", "--dictionary", type=int, nargs='?', const=-1)
    parser.add_argument("-z", "--zen", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-t", "--timer", type=int, nargs='?')
    parser.add_argument("-w", "--words", type=int, nargs='?', const=-1)
    return parser.parse_args()

def load_text(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        return " ".join([line.strip() for line in lines])

def load_raw_text(args, config):
    if args.file:
        return load_text(args.file)
    else:
        if args.extract:
            return load_text(config["default_extract"].replace("$PATH", PATH))
        else:
            return load_text(config["default_dictionary"].replace("$PATH", PATH))

def load_config():
    with open(PATH + "/config.json") as f:
        return json.load(f)

def get_dictionary_lines(words, length, line_count):
    lines = []
    line = ""
    while len(lines) < line_count:
        if len(line) >= length:
            lines.append(line)
            line = ""
        word = random.choice(words)
        if len(line) + len(word) <= length:
            line += word + ' '
        else:
            lines.append(line)
            line = ""
    return lines

def get_word_count_lines(words, length, word_count):
    lines = []
    line = ""
    current_count = 0
    while current_count < word_count:
        if len(line) >= length:
            lines.append(line)
            line = ""
        word = random.choice(words)
        if len(line) + len(word) <= length:
            line += word + ' '
            current_count += 1
        else:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)
    return lines

    
def get_extract_lines(text, length):
    lines = []
    line = ""
    word_index = 0
    while word_index < len(text):
        if len(line) >= length:
            lines.append(line)
            line = ""
        word = text[word_index]
        if len(line) + len(word) <= length:
            line += word + ' '
            word_index += 1
        else:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)
    return lines


def is_escape(key):
    try:
        if ord(key) == 27:
            return True
    except:
        pass
    return False

def is_backspace(key):
    if key in ("KEY_BACKSPACE", "\b", "\x7f"):
        return True
    return False

def display_results(results):
    for key, value in results.items():
        print(f"{key}: " + "{0:.2f}".format(value))

def main(stdscr, args):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    CORRECT = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    INCORRECT = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    INCORRECT_SPACE = curses.color_pair(3)

    # config
    config = load_config()
    text_width = config["input_width"] - 2
    if args.zen:
        config["stat_height"] = 0

    # args
    if not args.zen:
        if args.verbose:
            args.zen = False
        else:
            args.zen = config["default_zen"]

    # load text
    raw_text = load_raw_text(args, config)
    top_words = config["default_top_words"]
    if args.dictionary and args.dictionary > 0:
        top_words = args.dictionary
    raw_words = raw_text.split(' ')[:top_words]
        
    # generate lines
    lines = []
    line_index = 0
    if args.extract:
        lines = get_extract_lines(raw_words, text_width)
    else:
        if args.words:
            if args.words == -1:
                args.words = config["default_words"]
            lines = get_word_count_lines(raw_words, text_width, args.words)
        else:
            args.timer = config["default_timer"]
            lines = get_dictionary_lines(raw_words, text_width, config["max_lines"])

    # remove trailing space
    if not args.timer:
        lines[-1] = lines[-1][:-1]
    current_text = [[]]

    # stats
    accuracy = 1
    raw_wpm = 0
    adj_wpm = 0
    progress = 0
    start_time = time.time()
    stat_width = text_width // 4
    stat_left = config["margin_left"] + config["input_margin"] + 1

    # input state
    if config["vertical_align"] == "center":
        input_top = curses.LINES // 2 - config["max_lines"] // 2
        stat_top = input_top - config["stat_height"]
    elif config["vertical_align"] == "bottom":
        input_top = curses.LINES - config["vertical_margin"] - config["max_lines"] - 2
        stat_top = input_top - config["stat_height"]
    # if "top" or invalid input
    else:
        input_top = config["vertical_margin"] + config["stat_height"]
        stat_top = config["vertical_margin"]
    input_offset = 2

    # main loop 
    while True:
        # hide cursor
        curses.curs_set(0)
        stdscr.clear()

        middle_line = config["max_lines"] // 2
        indicated_line = input_top + 1 + min(line_index, middle_line)

        start_line = 0 if line_index < middle_line else line_index - middle_line
        end_line = start_line + config["max_lines"]
        for y, line in enumerate(lines[start_line:end_line]):
            stdscr.addstr(input_top + 1 + y, config["margin_left"] + 2, line, curses.A_DIM)
            if (start_line + y) < len(current_text):
                for x, c in enumerate(current_text[start_line + y]):
                    if c == line[x]:
                        color = CORRECT
                    elif line[x] == ' ':
                        color = INCORRECT_SPACE
                    else:
                        color = INCORRECT
                    stdscr.addstr(input_top + 1 + y, config["margin_left"] + 2 + x, line[x], color)

        # calculate correct characters
        correct_chars = 0
        for y, line in enumerate(lines):
            if y < len(current_text):
                for x, c in enumerate(current_text[y]):
                    if c == line[x]:
                        correct_chars += 1

        # display line indicator
        if config["line_indicator"]:
            stdscr.addstr(indicated_line, config["margin_left"] + 1, '>')
            stdscr.addstr(indicated_line, config["margin_left"] + config["input_width"], '<')

        # display border
        if config["border"]:
            stdscr.addstr(
                input_top, config["margin_left"],
                '╭' + ('─'*config["input_width"]) + '╮'
            )
            for i in range(config["max_lines"]):
                stdscr.addstr(input_top + 1 + i, config["margin_left"], '│')
                stdscr.addstr(
                    input_top + 1 + i, config["margin_left"] + config["input_width"] + 1, '│'
                )
            stdscr.addstr(
                input_top + config["max_lines"] + 1, config["margin_left"],
                '╰' + ('─'*config["input_width"]) + '╯'
            )

        # display stats
        text_length = sum(len(line) for line in lines)
        current_length = sum(len(line) for line in current_text)
        accuracy = correct_chars / current_length if current_length > 0 else 1
        time_elapsed = max(time.time() - start_time, 1)
        raw_wpm = (current_length / (time_elapsed / 60)) / 5
        adj_wpm = raw_wpm * accuracy
        progress = current_length / text_length if text_length > 0 else 0

        if not args.zen:
            acc_text = f"ACC: {round(accuracy*100)}%"
            stdscr.addstr(
                stat_top, stat_left,
                acc_text.ljust(stat_width)
            )

            adj_wpm_text = f"WPM (ADJ): {round(adj_wpm)}"
            stdscr.addstr(
                stat_top, stat_left + stat_width,
                adj_wpm_text.ljust(stat_width)
            )

            raw_wpm_text = f"WPM (RAW): {round(raw_wpm)}"
            stdscr.addstr(
                stat_top, stat_left + (2*stat_width),
                raw_wpm_text.ljust(stat_width)
            )

            if not args.extract and args.timer:
                time_text = f"TIME: {round(args.timer - time_elapsed)}"
                stdscr.addstr(
                    stat_top, stat_left + (3*stat_width),
                    time_text.ljust(stat_width)
                )
            else:
                progress_text = f"PRG: {round(progress*100)}%"
                stdscr.addstr(
                    stat_top, stat_left + (3*stat_width),
                    progress_text.ljust(stat_width)
                )

        # refresh screen
        stdscr.refresh()

        # return results on completion
        if current_length >= text_length or (args.timer and time_elapsed > args.timer):
            return {
                "accuracy": accuracy,
                "raw_wpm": raw_wpm,
                "adj_wpm": adj_wpm,
                "time_elapsed": time_elapsed
            }
        
        # show cursor
        curses.curs_set(1)

        stdscr.move(
            indicated_line,
            config["margin_left"] + 2 + len(current_text[line_index])
        )

        # handle key input
        try:
            key = stdscr.getkey()
        except:
            continue
        
        if is_escape(key):
            break

        if is_backspace(key):
            if len(current_text[line_index]) > 0:
                current_text[line_index].pop()
            elif line_index > 0:
                current_text.pop()
                line_index -= 1
                current_text[line_index].pop()
        # if space is available on the current line
        elif len(current_text[line_index]) < len(lines[line_index]) - 1:
            current_text[line_index].append(key)
        # if no space is available on the current line
        else:
            current_text[line_index].append(key)
            current_text.append([])
            line_index += 1
            if args.timer:
                lines += get_dictionary_lines(raw_words, text_width, 1)
    
    return

if __name__ == "__main__":
    args = parse_args()
    results = wrapper(main, args)
    if results:
        display_results(results)    
