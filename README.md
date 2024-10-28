# Typr

A curses application developed in Python for typing practice and assessing typing speed

Requires `windows-curses` on Windows.

# Installation

The program can be run using the `typr` command if `source path/to/.typr.sh` has been added to your shell's .rc file. Alternatively, the program can be run using `python main.py <mode ("dict"/"text")> <file (or "default")> <zen_mode true or false>`.

# Flags

```
-d, --dict (default):
    Use a text file as a dictionary to select words at random. A specific file in /dictionaries can be specified as an argument, or it can be left blank to use the default.
-t, --text:
    Use a text file as an extract to type from. A specified file in /texts can be specified as an argument, or it can be left blank to use the default.
-z, --zen:
    Enables zen mode, preventing all stats from being displayed and providing a minimal experience.
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

# Texts

Texts are imported directly to be practiced from. There is only one sample text, which can be found in `/texts`, but more can be added.

