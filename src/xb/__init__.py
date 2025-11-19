import sys

import xb.run

def main() -> None:
    args = sys.argv[1:]
    if len(args):
        xb.run.file(args[0])
    else:
        xb.run.repl()
