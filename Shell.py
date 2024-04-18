import os
from ctypes import CFUNCTYPE, c_int

import llvmlite.binding as llvm
import llvmlite.ir
from llvmlite.binding import PassManagerBuilder, ModulePassManager

from Context import Context, VarMap
from Error import Error
from IrBuilder import IrBuilder
from Lexer import Lexer
from Methods import fail
from Parser import Parser


def start(args: list[str]):
    if len(args) <= 1:
        print('Welcome to TenessPy REPL. -help for help, -stop to stop')
        while True:
            in_str = input(' >>> ')
            if in_str == '-help':
                print_help()
                continue
            elif in_str == '-stop':
                break
            else:
                run(in_str)
    else:
        with open(args[1], "r") as f:
            run(f.read())


LEXER_DEBUG = False
PARSER_DEBUG = False
BUILDER_DEBUG = True
ASSEMBLY_DEBUG = False
RUN = True


def run(text: str):
    ctx = Context(None, '<main>', VarMap(), '<stdin>', text)
    lexer = Lexer(ctx)
    tokens = lexer.make_tokens()
    if LEXER_DEBUG:
        print('\nEvaluated to the following Tokens:')
        print('\t' + tokens.__str__())
    parser = Parser(tokens, ctx)
    ast = parser.parse()
    if isinstance(ast, Error):
        fail(ast)
    if PARSER_DEBUG:
        print('\nEvaluated to the following AST:')
        print('\t' + ast.__str__())
    builder = IrBuilder()
    builder.build(ast)
    module = builder.module
    module.triple = llvm.get_default_triple()
    if BUILDER_DEBUG:
        print('\nEvaluated to the following IR:')
        print('\t' + module.__str__())
    if RUN:
        run_jit(module)
    else:
        cmp(module)


def cmp(module: llvmlite.ir.Module):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        llvm_module = llvm.parse_assembly(module.__str__())
        llvm_module.verify()
    except Exception as e:
        print(e)
        raise

    target = llvm.Target.from_default_triple().create_target_machine()
    if not os.path.exists("out/"):
        os.makedirs('out/')
    if not os.path.exists("out/main.o"):
        open('out/main.o', 'x')
    with open('out/main.o', "wb") as f:
        assembly = target.emit_assembly(llvm_module)
        obj = target.emit_object(llvm_module)
        f.write(obj)
        if ASSEMBLY_DEBUG:
            print('Evaluated to the following assembly:')
            print(assembly)


def run_jit(module: llvmlite.ir.Module):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        llvm_module = llvm.parse_assembly(module.__str__())
        llvm_module.verify()
    except Exception as e:
        print(e)
        raise

    target = llvm.Target.from_default_triple().create_target_machine()
    engine = llvm.create_mcjit_compiler(llvm_module, target)
    engine.finalize_object()

    entry = engine.get_function_address('main')
    if entry == 0:
        print('No main function found!')
        return
    c_func = CFUNCTYPE(c_int)(entry)
    print('Starting...\n')
    result = c_func()
    print(f'\nReturned {result}')


def print_help():
    print(''
          '\tThe current Compiler implementation of TenessScript.\n\n'

          '\tCompiles the give tss file.\n\n'

          '\tOptions:\n'
          '\t\t-help:     show this help \n\n'

          '\tExit Status:\n'
          '\t\tReturns success unless a error occurs')
