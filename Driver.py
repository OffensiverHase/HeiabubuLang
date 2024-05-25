import builtins
import os
import platform
import subprocess
from argparse import Namespace, ArgumentParser
from ctypes import CFUNCTYPE, c_int

import llvmlite.binding as llvm
import llvmlite.ir
from termcolor import colored

from Context import Context
from Error import Error, RuntimeError
from IrBuilder import IrBuilder
from Lexer import Lexer
from Methods import fail
from Parser import Parser
from Semantic import Analyser

"""The compiler Driver gluing all components together"""


def start() -> int:
    """Collect the args and set the global variables to those values, then start the compilation"""
    args = parse_args()
    for arg in args.d:
        globals()[arg.upper() + '_DEBUG'] = True
    if args.run:
        globals()['RUN'] = True
    try:
        with open(args.file_path) as f:
            text = f.read()
    except FileNotFoundError:
        print(colored(f'File {args.file_path} not found!', 'red'))
        return 1
    if args.o:
        globals()['OUTPUT'] = args.o
    else:
        globals()['OUTPUT'] = args.file_path.replace('.hb', '.exe' if platform.system() == 'Windows' else '')
    global OPT
    OPT = args.no_opt
    return run(text, args.file_path)


def parse_args() -> Namespace:
    """Use argparse ArgumentParser to parse argv"""
    arg_parser = ArgumentParser(prog='Heiabubu', description='LLVM implementation of a Heiabubu compiler',
                                epilog='Exit Status:\n\tReturns 0 unless an error occurs')

    arg_parser.add_argument('file_path', help='Path to your entry point Heiabubu file. (e.g. main.hb)')
    arg_parser.add_argument('-d', type=str, action='append', choices=['tokens', 'ast', 'ir', 'asm'],
                            help='Dump for debug info', default=[])
    arg_parser.add_argument('-o', type=str, help='The emitted output file. (e.g. main.exe)')
    arg_parser.add_argument('-no_opt', action='store_false', help='Turn off all optimisations')
    arg_parser.add_argument('-run', action='store_true',
                            help='Run the given file via JIT compilation, dont create an executable')
    return arg_parser.parse_args()


"""Global flags mostly for emitting debug info"""
TOKENS_DEBUG = False  # emit OUTPUT.tokens
AST_DEBUG = False  # emit OUTPUT.json
IR_DEBUG = False  # emit OUTPUT.ll
ASM_DEBUG = False  # emit OUTPUT.s
RUN = False  # Run the code with JIT compilation, else create an executable
OPT = True  # Optimise the code with llvm -03 level
OUTPUT: str | None = None  # The name of the output files, specified with -o, default is file_path.exe on Windows, else file_path


def run(text: str, file: str) -> int:
    """
    Run the compiler in the following steps:
        1. Lexer(text)      -> token[]
        2. Parser(token[])  -> ast
        3. Analyser(ast)    -> None
        4. IrBuilder(ast)   -> ir_module
        5. LLVM(ir_module)  -> object_file
        6. gcc(object_file) -> executable
    """
    file = file.split(os.sep)[-1]
    file, _ = os.path.splitext(file)
    ctx = Context(None, f'load_{file}', file, text)
    lexer = Lexer(ctx)
    tokens = lexer.make_tokens()
    if isinstance(tokens, Error):
        fail(tokens)
        return 1
    if TOKENS_DEBUG:
        with open(OUTPUT + '.tokens', 'w') as f:
            f.write(f'{file}:\n' + ' ' + ' '.join(map(str, tokens)))
    parser = Parser(tokens, ctx)
    ast = parser.parse()
    if isinstance(ast, Error):
        fail(ast)
        return 1
    if AST_DEBUG:
        with open(OUTPUT + '.json', 'w') as f:
            f.write(ast.__str__())
    analyser = Analyser(ctx)
    try:
        analyser.check(ast)
    except Error as e:
        fail(e)
        return 1
    builder = IrBuilder(ctx)
    try:
        builder.build(ast)
    except Error as e:
        fail(e)
        return 1
    module = builder.module
    module.triple = llvm.get_default_triple()
    if IR_DEBUG:
        with open(OUTPUT + '.ll', 'w') as f:
            if OPT:
                module = opt(module)
                if module is None:
                    return 1
            f.write(module.__str__())
    if RUN:
        run_jit(module, file)
    else:
        cmp(module)
    return 0


def opt(module: llvmlite.ir.Module) -> llvm.ModuleRef | None:
    """Optimise the llvmlite module if OPT, return llvm module"""
    try:
        module_ref = llvm.parse_assembly(module.__str__())
    except builtins.RuntimeError as e:
        print(colored('Caught llvm runtime error:', 'red'))
        print(colored(str(e), 'red'))
        print(colored('please report this to github!', 'red'))
        return None
    if OPT:
        pmb = llvm.PassManagerBuilder()
        pmb.opt_level = 3
        pm = llvm.ModulePassManager()
        pmb.populate(pm)
        pm.run(module_ref)
    return module_ref


def cmp(module: llvmlite.ir.Module):
    """
    Compile the llvm module to an executable file in the following steps:
        1. LLVM(module)     -> temp.o
        2. gcc(temp.o)      -> executable
        3. remove temp.o
    """
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        llvm_module = opt(module)
        if llvm_module is None:
            return
        llvm_module.verify()
    except Exception as e:
        print(e)
        raise

    target = llvm.Target.from_default_triple().create_target_machine()

    try:
        with open(OUTPUT + '_temp.o', "xb") as f:
            obj = target.emit_object(llvm_module)
            f.write(obj)
        if ASM_DEBUG:
            with open(OUTPUT + '.s') as f:
                assembly = target.emit_assembly(llvm_module)
                f.write(assembly)

        subprocess.run(['gcc', OUTPUT + '_temp.o', '-o', OUTPUT], capture_output=True, text=True)
    except Exception as e:
        print(colored(str(e), 'red'))
    finally:
        os.remove(OUTPUT + '_temp.o')


def run_jit(module: llvmlite.ir.Module, file: str):
    """Run the llvm module via just in time compilation"""
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        llvm_module = opt(module)
        if llvm_module is None:
            return
        llvm_module.verify()
    except Exception as e:
        print(e)
        raise

    target = llvm.Target.from_default_triple().create_target_machine()
    engine = llvm.create_mcjit_compiler(llvm_module, target)
    engine.finalize_object()

    if ASM_DEBUG:
        with open(OUTPUT + '.s') as f:
            assembly = target.emit_assembly(llvm_module)
            f.write(assembly)

    entry = engine.get_function_address('main')
    if entry == 0:
        entry = engine.get_function_address(f'load_{file}')
    c_func = CFUNCTYPE(c_int)(entry)
    print('\n\nStarting...\n')
    result = c_func()
    print(f'\nReturned {result}')
