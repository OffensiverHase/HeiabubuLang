import sys

from Context import Context
from Error import Error
from Token import Position

from termcolor import colored


def fail(error: Error):
    print(colored(str(error), 'red'))
    print(''
          f'Context:\n'
          f'\tstage --> {error.stage}\n'
          f'{error.context}'
          )
    arrow_str(error.pos, error.context)


def arrow_str(pos: Position, context: Context):
    if pos.line > 0:
        line_before = f'{(pos.line + 1) - 1}\t|\t{context.file_text.splitlines()[pos.line - 1]}'
        print(line_before)
        print('\t|')

    line = f'{(pos.line + 1)}\t|\t{context.file_text.splitlines()[pos.line]}'
    arrow_line = '\t|\t'
    arrow = ' '
    for i in range(pos.column - 1):
        arrow += ' '
    for i in range(pos.len):
        arrow += '^'
    print(line)
    print(arrow_line, end='')
    print(colored(arrow, 'red'))

    if pos.line + 1 < len(context.file_text.splitlines()):
        line_after = f'{(pos.line + 1) + 1}\t|\t{context.file_text.splitlines()[pos.line + 1]}'
        print(f'{line_after}')
    print()
