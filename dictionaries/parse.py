import sys

with open(sys.argv[1], "r") as f:
    words = [line.split(' ')[0] for line in f.readlines()]

with open(sys.argv[2], "w") as f:
    f.write('\n'.join(words))
