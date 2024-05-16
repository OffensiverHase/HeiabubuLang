import sys

from Context import Context
from Error import Error
from Token import Position


def fail(error: Error):
    print_err(''
              f'Encountered error in stage {error.stage}\n'
              f'{error}\n'
              f'Context: {error.context} ', sep='\n')
    print_err(f'\nsrc --> {error.context.file}\n')
    arrow_str(error.pos, error.context)


def arrow_str(pos: Position, context: Context):
    if pos.line > 0:
        line_before = f'{(pos.line + 1) - 1}\t|\t{context.file_text.splitlines()[pos.line - 1]}'
        print_err(line_before)
        print_err('\t|')

    line = f'{(pos.line + 1)}\t|\t{context.file_text.splitlines()[pos.line]}'
    arrow = '\t|\t '
    for i in range(pos.column - 1):
        arrow += ' '
    arrow += '^'
    print_err(line)
    print_err(arrow)

    if pos.line + 1 < len(context.file_text.splitlines()):
        line_after = f'{(pos.line + 1) + 1}\t|\t{context.file_text.splitlines()[pos.line + 1]}'
        print_err(f'{line_after}')
        print_err('\t|')
    print_err()


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
