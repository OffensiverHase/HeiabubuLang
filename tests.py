from llvmlite import ir
from Shell import run_jit


# <editor-fold desc="Setup">
ctx = ir.Context()
builder = ir.IRBuilder()
module = ir.Module('main', ctx)

fnty = ir.FunctionType(ir.IntType(32), [])
fun = ir.Function(module, fnty, 'main')

block = fun.append_basic_block('entry')
builder.position_at_start(block)

int_type = ir.IntType(32)
str_type = ir.IntType(8).as_pointer()
bool_type = ir.IntType(1)
float_type = ir.DoubleType()
# </editor-fold>

builder.add(int_type(1), int_type(1), name='nop')
builder.add(int_type(1), int_type(1), name='nop')
builder.ret(int_type(0))

# <editor-fold desc="Ending">
print(module)

run_jit(module)
# </editor-fold>
