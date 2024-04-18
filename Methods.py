import sys

from Context import Context
from Error import Error
from Token import Position


def fail(error: Error):
    print_err(''
              f'Encountered error in stage {error.stage}\n'
              f'{error}\n'
              f'Context: {error.context} ', sep='\n')
    arrow_str(error.pos, error.context)


def arrow_str(pos: Position, context: Context):
    line = context.file_text.splitlines()[pos.line]
    arrow = ' '
    for i in range(pos.column - 1):
        arrow += ' '
    arrow += '^'
    print_err(f'{pos.line}\t{line}')
    print_err(f'\t{arrow}')


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
