# Typr

A curses application developed in Python for typing practice and assessing typing speed

Requires `windows-curses` on Windows.

# Usage

The program can be run using the `typr` command if `source path/to/.typr.sh` has been added to your shell's .rc file. Alternatively, the program can be run using `python main.py <flags/arguments>`.

# Arguments

A file can be specified as an argument when using the command. How this file is used depends on the flags passed.

# Flags

```
-d, --dictionary [TOP_WORDS] (default):
    Use a text file as a dictionary to select words at random. A parameter can be specified to override the top `n` words used from the dictionary.
-e, --extract:
    Use a text file as an extract to type from.
-z, --zen:
    Enables zen mode, preventing all stats from being displayed and providing a minimal experience. This overrides the `default_zen` value in the configuration file.
-v, --verbose:
    Disables zen mode, displaying stats. This overrides the `default_zen` value in the configuration file.
-t, --timer [TIMER] (default):
    Uses a timer if a dictionary is used. A time in seconds can be specified, or defaults to `60`.
-w, --words [WORDS]:
    Uses a word count if a dictionary is used. A word count can be specified, or defaults to `100`.
```

# Dictionaries

Dictionaries are split into individual words and added at random to create a series of words to practice. A few sample frequency lists have been provided to start from, and can be located in `/dictionaries`. Any additional word lists can be stored here.

- English: `english-50k.txt`
- French: `french-50k.txt`
- German: `german-50k.txt`
- Italian: `italian-50k.txt`
- Russian: `russian-50k.txt`
- Serbian: `serbian-50k.txt`
- Spanish: `spanish-50k.txt`

# Extracts

Extracts are imported directly to be practiced from. There is only one sample extract, which can be found in `/extracts`, but more can be added.

# Configuration

## Display

- `input_width` (default 80): internal width of the input box.
- `max_lines` (default 5): internal height of the input box.
- `vertical_margin` (default 2): vertical margin before the stats and input box when vertical_align is "top", or after when vertical_align is "bottom".
- `margin_left` (default 4): horizontal margin before the input box.
- `input_margin` (default 1): horizontal margin inside the input box.
- `stat_height` (default 1): rows reserved to display statistics.
- `vertical_align` (default "center"): align content vertically to "top", "center", or "bottom".
- `border` (default false): whether a border is drawn around the input box.
- `line_indicator` (default false): whether a line indicator is rendered.

## Defaults

- `default_dictionary` (default $PATH/dictionaries/english-50k.txt):
    dictionary used when none is specified.
- `default_extract` (default $PATH/extracts/sample.txt):
    extract used when none is specified. 
- `default_timer` (default 60):
    timer used when none is specified.
- `default_words` (default 100):
    word count used when none is specified.
- `default_top_words` (default 1000):
    top `n` words to use when none is specified.
- `default_zen` (default false):
    the default zen setting when non is specified.
