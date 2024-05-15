from __future__ import annotations

import os.path

from llvmlite import ir
from llvmlite.ir import CompareInstr, GlobalVariable

from Context import Context
from Env import Environment
from Error import Error
from Lexer import Lexer
from Methods import print_err
from Node import *
from Parser import Parser
from Token import TT


def visit_unknown_node(node: Node):
    print_err(f'Found unknown node: {node.__class__.__name__}!')


class IrBuilder:
    def __init__(self, context: Context):
        self.context = context

        self.int_type = ir.IntType(32)
        self.float_type = ir.DoubleType()
        self.bool_type = ir.IntType(1)
        self.byte_type = ir.IntType(8)
        self.str_type = ir.PointerType(self.byte_type)
        self.null_type = ir.VoidType()

        self.counter = -1

        self.breaks: list[ir.Block] = []
        self.continues: list[ir.Block] = []

        self.global_imports = {}

        self.module = ir.Module(f'{self.context.file}_main')

        self.builder = ir.IRBuilder()
        self.allocator = Allocator()

        self.structs: dict[str, Struct] = {}

        self.pow = self.module.declare_intrinsic('llvm.pow', [self.float_type])

        self.env = Environment()

        self.init_builtins()

    def get_type(self, name: str) -> ir.Type:
        if name.startswith('list'):
            list_type = name.removeprefix('list:')
            list_type = self.get_type(list_type)
            return list_type.as_pointer()
        else:
            Type: ir.Type | None = None
            try:
                Type = self.__getattribute__(name + '_type')
            except AttributeError:
                if name in self.module.get_identified_types().keys():
                    Type = self.module.context.get_identified_type(name)
                else:
                    print_err(f'No type called {name}')
            return Type

    def increment_counter(self) -> int:
        self.counter += 1
        return self.counter

    def init_builtins(self):
        def init_bool() -> tuple[GlobalVariable, GlobalVariable]:
            true_var = ir.GlobalVariable(self.module, self.bool_type, 'true')
            true_var.initializer = self.bool_type(1)
            true_var.global_constant = True

            false_var = ir.GlobalVariable(self.module, self.bool_type, 'false')
            false_var.initializer = self.bool_type(0)
            false_var.global_constant = True

            return true_var, false_var

        def init_print() -> ir.Function:
            funty: ir.FunctionType = ir.FunctionType(self.int_type, [self.str_type], var_arg=True)
            return ir.Function(self.module, funty, 'printf')

        def __init_c_std_library() -> None:
            strlen_ty = ir.FunctionType(self.int_type, [ir.IntType(8).as_pointer()], var_arg=False)
            strlen_func = ir.Function(self.module, strlen_ty, name="strlen")

            malloc_ty = ir.FunctionType(ir.IntType(8).as_pointer(), [self.int_type], var_arg=False)
            malloc_func = ir.Function(self.module, malloc_ty, name="malloc")

            strcpy_ty = ir.FunctionType(ir.IntType(8).as_pointer(),
                                        [ir.IntType(8).as_pointer(), ir.IntType(8).as_pointer()], var_arg=False)
            strcpy_func = ir.Function(self.module, strcpy_ty, name="strcpy")

            self.env.define('len', strlen_func, self.int_type)

        self.env.define('printf', init_print(), self.int_type)

        true, false = init_bool()
        self.env.define('true', true, true.type)
        self.env.define('false', false, false.type)

        __init_c_std_library()

    def build(self, node: Node):
        fnty = ir.FunctionType(self.int_type, [])
        fun = ir.Function(self.module, fnty, f'load_{self.context.file}')
        block = fun.append_basic_block(f'load_{self.context.file}_entry')
        self.env.define(f'load_{self.context.file}', fun, self.int_type)

        with self.allocator.set_block(block):
            self.builder.position_at_end(block)

            self.visit(node)

            if not self.builder.block.is_terminated:
                self.builder.ret(self.int_type(0))

    def visit(self, node: Node) -> tuple[ir.Value, ir.Type] | None:
        method = getattr(self, 'visit' + node.__class__.__name__, visit_unknown_node)
        return method(node)

    def visitNumberNode(self, node: NumberNode) -> tuple[ir.Value, ir.Type]:
        Type = self.int_type if node.token.type == TT.INT else self.float_type
        return ir.Constant(Type, node.token.value), Type

    def visitStatementNode(self, node: StatementNode):
        for expr in node.expressions:
            self.visit(expr)

    def visitFunDefNode(self, node: FunDefNode):
        name: str = node.identifier.value
        body = node.body
        param_names: list[str] = [p.value for p in node.args]
        param_types: list[ir.Type] = []
        for t in node.arg_types:
            Type = self.get_type(t.value)
            if isinstance(Type, ir.BaseStructType):
                Type = Type.as_pointer()
            param_types.append(Type)
        return_type = self.get_type(node.return_type.value)
        if return_type.__class__ in [ir.IdentifiedStructType, ir.LiteralStructType]:
            return_type = return_type.as_pointer()

        fun_type = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, fun_type, name)
        block = func.append_basic_block(f'{name}_entry')

        with self.allocator.set_block(block):

            prev_builder = self.builder
            prev_env = self.env
            self.builder = ir.IRBuilder(block)
            self.env = Environment(parent=prev_env)

            params_ptr: list[ir.AllocaInstr] = []

            for i, typ in enumerate(param_types):
                ptr = self.builder.alloca(typ, name=param_names[i])
                params_ptr.append(ptr)

            for i, typ in enumerate(param_types):
                self.builder.store(func.args[i], params_ptr[i])

            for i, x in enumerate(zip(param_types, param_names)):
                typ = param_types[i]
                ptr = params_ptr[i]

                self.env.define(x[1], ptr, typ)

            self.env.define(name, func, return_type)

            self.visit(body)
            if return_type == self.null_type and not self.builder.block.is_terminated:
                self.builder.ret_void()

            self.env = prev_env
            self.env.define(name, func, return_type)
            self.builder = prev_builder

    def visitReturnNode(self, node: ReturnNode):
        value_node = node.value

        if not value_node:
            self.builder.ret_void()
            return

        value, Type = self.resolve(value_node)

        if self.is_str(Type):
            ptr_to_array = self.builder.gep(value,
                                            [self.int_type(0), self.int_type(0)] if Type.pointee.is_pointer else [
                                                self.int_type(0)], name='ret_temp')
            self.builder.ret(ptr_to_array)
        elif self.is_list(Type):
            ptr_to_array = self.builder.gep(value,
                                            [self.int_type(0), self.int_type(0)] if self.is_list(Type.pointee) else [
                                                self.int_type(0)], name='ret_temp')
            self.builder.ret(ptr_to_array)
        else:
            self.builder.ret(value)

    def visitListNode(self, node: ListNode) -> tuple[ir.Value, ir.Type]:
        values = node.content
        if len(values) == 0:
            lst = ir.Constant(ir.ArrayType(self.int_type, 0), [])
            return lst, lst.type

        _, list_type = self.resolve(values[0])
        resolved_values: list[ir.Value] = []
        for v in values:
            value, Type = self.visit(v)
            if Type != list_type:
                print_err(f'Expected {list_type}, got {Type}')
            resolved_values.append(value)

        list_ptr = self.allocator.alloca(ir.ArrayType(list_type, len(values)), name='list_ptr')
        self.builder._anchor += 1

        begin = self.builder.gep(list_ptr, [self.int_type(0), self.int_type(0)], name='array.0')
        self.builder.store(resolved_values[0], begin)

        resolved_values.pop(0)

        last_ptr = begin

        for i, resolved in enumerate(resolved_values):
            element_ptr = self.builder.gep(last_ptr, [self.int_type(1)], name=f'array.{i}')
            self.builder.store(resolved, element_ptr)
            last_ptr = element_ptr

        return list_ptr, list_ptr.type

    def visitVarAssignNode(self, node: VarAssignNode):
        name: str = node.name.value
        value_node = node.value
        value_type = self.get_type(node.type.value) if node.type else None

        value, Type = self.resolve(value_node)

        if value_type != Type and value_type is not None and (value_type != Type.pointee) if Type.is_pointer else True:
            print_err(f'Type Error: expected {value_type}, got {Type}')

        if self.env.lookup(name) is None:

            ptr = self.allocator.alloca(Type, name=name)
            self.builder._anchor += 1

            self.builder.store(value, ptr)
            self.env.define(name, ptr, Type)
        else:
            ptr, Type2 = self.env.lookup(name)
            if value_type != Type2 and value_type is not None:
                print_err(f'Type Error: expected {value_type}, got {Type2}')
            if Type != Type2:
                print_err(f'Type Error: expected {Type2}, got {Type}')
            self.builder.store(value, ptr)

    def visitVarAccessNode(self, node: VarAccessNode) -> tuple[ir.Value, ir.Type]:
        if node.name.value in ['true', 'false']:
            return ir.Constant(self.bool_type, 1 if node.name.value == 'true' else 0), self.bool_type
        # todo errors
        ptr, Type = self.env.lookup(node.name.value)
        return self.builder.load(ptr, name=node.name.value), Type

    def visitBinOpNode(self, node: BinOpNode) -> tuple[ir.Value, ir.Type]:
        operator = node.operator
        left_value, left_type = self.resolve(node.left)
        right_value, right_type = self.resolve(node.right)
        value = None
        Type = None
        if right_type == self.int_type and left_type == self.int_type:
            value, Type = self.int_bin_op(left_value, right_value, operator)

        elif right_type == self.float_type or left_type == self.float_type:
            if right_type == self.int_type or left_type == self.int_type:
                convert_left = right_type == self.float_type
                value, Type = self.float_bin_op(left_value, right_value, convert_left, operator)

        elif right_type == self.bool_type and left_type == self.bool_type:
            value, Type = self.bool_bin_op(left_value, right_value, operator)

        elif self.is_str(right_type) and self.is_str(left_type):
            value, Type = self.str_bin_op(left_value, right_value, operator)

        elif self.is_list(right_type) and self.is_list(left_type):
            value, Type = self.list_bin_op(left_value, right_value, operator)

        elif self.is_list(left_type) and right_type == self.int_type:
            value, Type = self.list_int_bin_op(left_value, right_value, operator,
                                               isinstance(left_type.pointee, ir.ArrayType))

        elif right_type == self.int_type and self.is_str(left_type):
            value, Type = self.str_int_bin_op(left_value, right_value, operator)
        else:
            print_err(f'Cannot find operation {operator} on {left_type} and {right_type}')

        return value, Type

    def visitUnaryOpNode(self, node: UnaryOpNode) -> tuple[ir.Value, ir.Type]:
        operator = node.operator
        node_value, node_Type = self.resolve(node.node)
        value = None
        Type = node_Type
        if operator.type == TT.PLUS:
            value = node_value
        elif operator.type == TT.MINUS:
            value = self.builder.neg(node_value)
        elif operator.type == TT.NOT:
            value = self.builder.not_(node_value)
        return value, Type

    def visitStringNode(self, node: StringNode) -> tuple[ir.Value, ir.Type]:
        string: str = node.value.value
        string = string.replace('\\n', '\n\0')

        fmt: str = f'{string}\0'
        c_fmt = ir.Constant(ir.ArrayType(self.byte_type, len(fmt)), bytearray(fmt.encode('utf8')))

        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name=f'__str_{self.increment_counter()}')
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt

        return global_fmt, global_fmt.type

    def visitIfNode(self, node: IfNode):
        condition = node.bool
        consequence = node.expr
        alternative = node.else_expr

        test, Type = self.resolve(condition)

        if alternative is None:
            with self.builder.if_then(test):
                self.visit(consequence)
        else:
            with self.builder.if_else(test) as (true, otherwise):
                with true:
                    self.visit(consequence)
                with otherwise:
                    self.visit(alternative)

    def visitWhileNode(self, node: WhileNode):
        condition = node.bool
        body = node.expr

        test, Type = self.resolve(condition)

        consequence = self.builder.append_basic_block(f'while_loop_entry_{self.increment_counter()}')
        otherwise = self.builder.append_basic_block(f'while_loop_otherwise_{self.counter}')

        self.breaks.append(otherwise)
        self.continues.append(consequence)

        self.builder.cbranch(test, consequence, otherwise)

        self.builder.position_at_start(consequence)
        self.visit(body)
        test, Type = self.resolve(condition)
        self.builder.cbranch(test, consequence, otherwise)
        self.builder.position_at_start(otherwise)

        self.breaks.pop()
        self.continues.pop()

    def visitBreakNode(self, node: BreakNode):
        if len(self.breaks) == 0:
            print_err(f'break outside of while or for!')
        self.builder.branch(self.breaks[-1])

    def visitContinueNode(self, node: ContinueNode):
        if len(self.continues) == 0:
            print_err(f'break outside of while of for!')
        self.builder.branch(self.continues[-1])

    def visitForNode(self, node: ForNode):
        var_name = node.identifier.value
        var_value, var_type = self.resolve(node.from_node)
        step_value, step_type = self.resolve(node.step)
        body: Node = node.expr
        to_value, to_type = self.resolve(node.to)

        if var_type != step_type != to_type:
            print_err('For loop variable, step and to types have to match!')

        loop_cond_block = self.builder.append_basic_block(f'loop_cond_{self.increment_counter()}')
        loop_body_block = self.builder.append_basic_block(f'loop_body_{self.counter}')
        loop_inc_block = self.builder.append_basic_block(f'loop_inc_block_{self.counter}')
        loop_exit_block = self.builder.append_basic_block(f'loop_exit_block_{self.counter}')

        ptr = self.allocator.alloca(var_type, name=var_name)
        self.builder._anchor += 1

        self.builder.store(var_value, ptr)
        self.builder.branch(loop_cond_block)
        prev_env = self.env
        self.env = Environment(None, prev_env, f'for_loop_{self.counter}')
        self.env.define(var_name, ptr, var_type)

        self.builder.position_at_end(loop_cond_block)
        loop_var_value = self.builder.load(ptr, name='loop_var')
        cond: CompareInstr | None = None
        if var_type == self.int_type or var_type == self.byte_type:
            cond = self.builder.icmp_signed('<', loop_var_value, to_value, name='loop_cond')
        elif var_type == self.float_type:
            cond = self.builder.fcmp_ordered('<', loop_var_value, to_value, name='loop_cond')
        else:
            print_err(f'Unknown types for for loop, got {var_type}, expected int, float, or byte')
        self.builder.cbranch(cond, loop_body_block, loop_exit_block)

        self.builder.position_at_end(loop_body_block)
        self.visit(body)
        self.builder.branch(loop_inc_block)

        self.builder.position_at_end(loop_inc_block)
        old_value = self.builder.load(ptr, name='old_loop_var')
        new_value = self.builder.add(old_value, step_value) if not var_type == self.float_type else self.builder.fadd(
            old_value, step_value, name='new_loop_var')
        self.builder.store(new_value, ptr)
        self.builder.branch(loop_cond_block)

        self.builder.position_at_end(loop_exit_block)

        self.env = prev_env

    def visitStructDefNode(self, node: StructDefNode):
        name: str = node.identifier.value
        funcs = node.functions
        idents = [ident.value for ident in node.values.keys()]
        types = [typ.value for typ in node.values.values()]
        self.structs[name] = Struct(name, idents)

        struct_type = self.module.context.get_identified_type(name)
        struct_type.set_body(*[self.get_type(typ) for typ in types])

        for fun in funcs:
            self.visit(fun)

    def visitStructAssignNode(self, node: StructAssignNode):
        struct, struct_type = self.resolve(node.obj)
        key: str = node.key.value
        value, value_type = self.resolve(node.value)
        struct_obj = self.structs[struct_type.pointee.name if struct_type.is_pointer else struct_type.name]
        index = struct_obj.field_indices[key]  # todo

        ptr = self.builder.gep(struct, [self.int_type(0), self.int_type(index)], name=f'{struct_obj.name}.{key}_ptr')
        self.builder.store(value, ptr)

    def visitStructReadNode(self, node: StructReadNode) -> tuple[ir.Value, ir.Type]:
        struct, struct_type = self.resolve(node.obj)
        key: str = node.key.value
        struct_obj = self.structs[struct_type.pointee.name if struct_type.is_pointer else struct_type.name]
        index = struct_obj.field_indices[key]  # todo

        if not struct_type.is_pointer:
            pass

        ptr = self.builder.gep(struct, [self.int_type(0), self.int_type(index)] if struct_type.is_pointer else [
            self.int_type(index)], name=f'{struct_obj.name}.{key}_ptr')
        value = self.builder.load(ptr, name=f'{struct_obj.name}.{key}')
        return value, value.type

    def visitImportNode(self, node: ImportNode):
        file_path = node.file_path.value
        if self.global_imports.get(file_path) is not None:
            print_err(f'Already imported {file_path} globally!')
            return

        with open(os.path.abspath(file_path), 'r') as f:
            file_code = f.read()

        ctx = Context(self.context, f'import_{file_path}', self.context.var_map, file_path, file_code)
        lexer = Lexer(ctx)
        tokens = lexer.make_tokens()
        parser = Parser(tokens, ctx)
        ast = parser.parse()
        if isinstance(ast, Error):
            print_err(f'Error while importing file {file_path}: {ast}')

        ir_builder = IrBuilder(ctx)
        ir_builder.visit(ast)

        self.global_imports[file_path] = ast

    def visitFunCallNode(self, node: FunCallNode) -> tuple[ir.Value, ir.Type]:
        name = node.identifier.value
        params = node.args

        if name in self.structs.keys():
            return self.init_struct(node)

        args: list[ir.Value] = []
        types: list[ir.Type] = []

        for i, p in enumerate(params):
            p_val, p_type = self.resolve(p)
            if isinstance(p_type, ir.BaseStructType):
                ptr = self.allocator.alloca(p_type, name=f'{node.identifier.value}.arg{i}')
                self.builder._anchor += 1

                self.builder.store(p_val, ptr)
                p_val = ptr
                p_type = ptr.type
            elif p_type.is_pointer and isinstance(p_type.pointee, ir.ArrayType):
                p_val = self.builder.bitcast(p_val, self.str_type, name='str_bitcast')
                p_type = self.str_type
            args.append(p_val)
            types.append(p_type)

        match name:
            case 'print':
                if len(types) <= 0:
                    print_err("printf cannot be called without a argument, use `printf('\n')`")
                ret = self.printf(params=args, return_type=types[0])
                ret_type = self.int_type
            case _:
                func, ret_type = self.env.lookup(name)
                ret = self.builder.call(func, args, name=f'{name}.ret')
        return ret, ret_type

    def init_struct(self, node: FunCallNode) -> tuple[ir.Value, ir.Type]:
        name = node.identifier.value
        params = node.args

        args: list[ir.Value] = []
        types: list[ir.Type] = []

        if len(params) > 0:
            for p in params:
                p_val, p_type = self.resolve(p)
                args.append(p_val)
                types.append(p_type)

        struct_type = self.module.context.get_identified_type(name)
        struct_obj = self.structs[name]

        struct_ptr = self.allocator.alloca(struct_type, name=name)
        self.builder._anchor += 1

        for i, arg in enumerate(args):
            ptr = self.builder.gep(struct_ptr, [self.int_type(0), self.int_type(i)],
                                   name=f'{name}.{list(struct_obj.field_indices)[i]}_ptr')
            if types[i].is_pointer and isinstance(types[i].pointee, ir.ArrayType):
                val = self.builder.bitcast(args[i], self.str_type, name='casted_str_val')
                self.builder.store(val, ptr)
            else:
                self.builder.store(arg, ptr)

        return struct_ptr, struct_ptr.type

    def visitPassNode(self, _: PassNode):
        self.builder.add(self.int_type(0), self.int_type(0), 'nop')

    def resolve(self, node: Node, value_type: str | None = None) -> tuple[ir.Value, ir.Type]:
        match node:
            case NumberNode():
                node: NumberNode = node
                value, Type = node.token.value, (
                    self.int_type if node.token.type == TT.INT else self.float_type) if value_type is None else value_type
                return ir.Constant(Type, value), Type
            case BinOpNode():
                node: BinOpNode = node
                return self.visitBinOpNode(node)
            case UnaryOpNode():
                node: UnaryOpNode = node
                return self.visitUnaryOpNode(node)
            case VarAccessNode():
                node: VarAccessNode = node
                return self.visitVarAccessNode(node)
            case FunCallNode():
                node: FunCallNode = node
                return self.visitFunCallNode(node)
            case StringNode():
                node: StringNode = node
                return self.visitStringNode(node)
            case ListNode():
                node: ListNode = node
                return self.visitListNode(node)
            case StructReadNode():
                node: StructReadNode = node
                return self.visitStructReadNode(node)
            case _:
                print_err(f'Tried to resolve unknown node: {node.__class__.__name__}: {node}')

    def int_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token) -> tuple[ir.Value, ir.Type]:
        Type = self.int_type
        value = None
        match operator.type:
            case TT.PLUS:
                value = self.builder.add(left_value, right_value, name='add')
            case TT.MINUS:
                value = self.builder.sub(left_value, right_value, name='sub')
            case TT.MUL:
                value = self.builder.mul(left_value, right_value, name='mul')
            case TT.DIV:
                value = self.builder.sdiv(left_value, right_value, name='div')
            case TT.MOD:
                value = self.builder.srem(left_value, right_value, name='mod')
            case TT.POW:
                pass  # todo value = self.builder.call(self.powi, [left_value, right_value], name='powi.ret')
            case TT.LESS:
                value = self.builder.icmp_signed('<', left_value, right_value, name='less')
                Type = self.bool_type
            case TT.LESSEQUAL:
                value = self.builder.icmp_signed('<=', left_value, right_value, name='lessequal')
                Type = self.bool_type
            case TT.GREATER:
                value = self.builder.icmp_signed('>', left_value, right_value, name='greater')
                Type = self.bool_type
            case TT.GREATEREQUAL:
                value = self.builder.icmp_signed('>=', left_value, right_value, name='greaterequal')
                Type = self.bool_type
            case TT.EQUALS:
                value = self.builder.icmp_signed('==', left_value, right_value, name='equal')
                Type = self.bool_type
            case TT.UNEQUALS:
                value = self.builder.icmp_signed('!=', left_value, right_value, name='unequal')
                Type = self.bool_type
            case TT.AND:
                value = self.builder.and_(left_value, right_value, name='and')
            case TT.XOR:
                value = self.builder.xor(left_value, right_value, name='xor')
            case _:
                print_err(f'unknown operation {operator} on int and int!')  # todo
        return value, Type

    def float_bin_op(self, left_value: ir.Value, right_value: ir.Value, convert_left: bool, operator: Token) -> tuple[
        ir.Value, ir.Type]:
        Type = self.float_type
        value = None
        if convert_left:
            left_value = self.builder.sitofp(left_value, self.float_type, 'cast_to_float')
        else:
            right_value = self.builder.sitofp(right_value, self.float_type, name='cast_to_float')

        match operator.type:
            case TT.PLUS:
                value = self.builder.fadd(left_value, right_value, name='plus')
            case TT.MINUS:
                value = self.builder.fsub(left_value, right_value, name='minus')
            case TT.MUL:
                value = self.builder.fmul(left_value, right_value, name='mul')
            case TT.DIV:
                value = self.builder.fdiv(left_value, right_value, name='div')
            case TT.MOD:
                value = self.builder.frem(left_value, right_value, name='mod')
            case TT.POW:
                value = self.builder.call(self.pow, [left_value, right_value], name='pow.ret')
            case TT.LESS:
                value = self.builder.fcmp_ordered('<', left_value, right_value, name='less')
                Type = self.bool_type
            case TT.LESSEQUAL:
                value = self.builder.fcmp_ordered('<=', left_value, right_value, name='lessequal')
                Type = self.bool_type
            case TT.GREATER:
                value = self.builder.fcmp_ordered('>', left_value, right_value, name='greater')
                Type = self.bool_type
            case TT.GREATEREQUAL:
                value = self.builder.fcmp_ordered('>=', left_value, right_value, name='greaterequal')
                Type = self.bool_type
            case TT.EQUALS:
                value = self.builder.fcmp_ordered('==', left_value, right_value, name='equal')
                Type = self.bool_type
            case TT.UNEQUALS:
                value = self.builder.fcmp_ordered('!=', left_value, right_value, name='unequal')
                Type = self.bool_type
            case _:
                print_err(f'unknown operation {operator} on float and float!')  # todo
        return value, Type

    def bool_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token) -> tuple[ir.Value, ir.Type]:
        Type = self.bool_type
        value = None
        match operator.type:
            case TT.AND:
                value = self.builder.and_(left_value, right_value, name='and')
            case TT.OR:
                value = self.builder.or_(left_value, right_value, name='or')
            case TT.XOR:
                value = self.builder.xor(left_value, right_value, name='xor')
            case TT.EQUALS:
                value = self.builder.icmp_unsigned(left_value, '==', right_value, name='equal')
            case TT.UNEQUALS:
                value = self.builder.icmp_unsigned(left_value, '!=', right_value, name='unequal')
            case _:
                print_err(f'unknown operation {operator} on bool and bool!')  # todo
        return value, Type

    def list_int_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token, bitcast: bool) -> tuple[
        ir.Value, ir.Type]:
        value, Type = None, None
        match operator.type:
            case TT.GET:
                if bitcast:
                    left_value = self.builder.bitcast(left_value, self.int_type.as_pointer(), 'list_to_ptr')
                ptr = self.builder.gep(left_value, [right_value], name='list_element_ptr')  # todo
                value = self.builder.load(ptr, name=f'list_element')
                Type = value.type
            case _:
                print_err(f'unḱnown operation {operator} on list and int')
        return value, Type

    def list_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token) -> tuple[ir.Value, ir.Type]:
        match operator.type:
            case TT.PLUS:
                list_ptr1 = self.builder.gep(left_value,
                                             [self.int_type(0)] if isinstance(left_value.type, ir.ArrayType) else [
                                                 self.int_type(0), self.int_type(0)], name="list_ptr1")
                list_ptr2 = self.builder.gep(right_value,
                                             [self.int_type(0)] if isinstance(left_value.type, ir.ArrayType) else [
                                                 self.int_type(0), self.int_type(0)], name="list_ptr2")
                len1 = self.builder.call()
                 # todo concat lists!

    def str_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token) -> tuple[ir.Value, ir.Type]:

        match operator.type:
            case TT.PLUS:
                str_ptr1 = self.builder.gep(left_value, [self.int_type(0)] if left_value.type == self.str_type else [
                    self.int_type(0), self.int_type(0)], name="str_ptr1")
                str_ptr2 = self.builder.gep(right_value, [self.int_type(0)] if left_value.type == self.str_type else [
                    self.int_type(0), self.int_type(0)], name="str_ptr2")

                len1 = self.builder.call(self.module.globals.get("strlen"), [str_ptr1], name="len1")

                len2 = self.builder.call(self.module.globals.get("strlen"), [str_ptr2], name="len2")

                # Allocate Memory
                total_length = self.builder.add(len1, len2)
                concat_ptr = self.builder.call(self.module.globals.get("malloc"), [total_length], name="concat_ptr")

                # Copy the first string (left_value) into the allocated memory
                self.builder.call(self.builder.function.module.globals.get("strcpy"), [concat_ptr, str_ptr1],
                                  name="copy_ptr1")

                # Calculate the offset for appending the second string (right_value)
                offset_ptr2 = self.builder.gep(concat_ptr, [len1], name="offset_ptr2")

                # Copy the second string (right_value) into the allocated memory at the offset position
                self.builder.call(self.builder.function.module.globals.get("strcpy"), [offset_ptr2, str_ptr2],
                                  name="copy_ptr1")

                value = concat_ptr

                Type = value.type

            case _:
                print_err(f'No such operation on string and string: {operator}')

        return value, Type

    def str_int_bin_op(self, left_value: ir.Value, right_value: ir.Value, operator: Token) -> tuple[ir.Value, ir.Type]:
        match operator.type:
            case TT.GET:
                char_ptr = self.builder.gep(left_value,
                                            [right_value] if left_value.type == self.str_type else [self.int_type(0),
                                                                                                    right_value],
                                            name="str_idx_ptr")
                i8_value = self.builder.load(char_ptr, name='char_i8_value')
                arr_ptr = self.allocator.alloca(ir.ArrayType(self.byte_type, 2), name='char_str_ptr')
                self.builder._anchor += 1
                c_ptr = self.builder.gep(arr_ptr, [self.int_type(0), self.int_type(0)], name='real_char_ptr')
                self.builder.store(i8_value, c_ptr)
                none_ptr = self.builder.gep(arr_ptr, [self.int_type(0), self.int_type(1)], name='none_ptr')
                self.builder.store(self.byte_type(0), none_ptr)
                value = arr_ptr
                Type = arr_ptr.type
            case _:
                print_err(f'No such operation on string and int: {operator}')
        return value, Type

    def printf(self, params: list[ir.Value], return_type: ir.Type) -> ir.CallInstr:
        func, _ = self.env.lookup('printf')
        c_str = self.allocator.alloca(return_type, name='c_str')
        self.builder._anchor += 1
        self.builder.store(params[0], c_str)

        rest_params = params[1:]

        if isinstance(params[0], ir.LoadInstr):
            c_fmt: ir.LoadInstr = params[0]
            g_var_ptr = c_fmt.operands[0]
            string_val = self.builder.load(g_var_ptr, name='c_str_val')
            fmt_arg = self.builder.bitcast(string_val, self.str_type, name='c_str_to_ptr')
            return self.builder.call(func, [fmt_arg, *rest_params], name='printf.ret')
        else:
            fmt_arg = self.builder.bitcast(self.module.get_global(f'__str_{self.counter}'), self.str_type,
                                           name='c_str_to_ptr')
            return self.builder.call(func, [fmt_arg, *rest_params], name='printf.ret')

    def is_str(self, typ: ir.Type) -> bool:
        if typ == self.str_type:
            return True
        if isinstance(typ, ir.ArrayType):
            if typ.element == self.byte_type:
                return True
            return False
        if typ.is_pointer:
            if typ.pointee == self.str_type:
                return True
            if isinstance(typ.pointee, ir.ArrayType):
                if typ.pointee.element == self.byte_type:
                    return True
                return False
        return False

    def is_list(self, typ: ir.Type) -> bool:
        if self.is_str(typ):
            return False
        if isinstance(typ, ir.ArrayType):
            return True
        if typ.is_pointer:
            return True  # fixme (can't be right, but how then?)
        return False


class Struct:
    def __init__(self, name: str, fields: list[str]):
        self.name = name
        self.field_indices = dict((field, idx) for idx, field in enumerate(fields))


class Allocator:
    def __init__(self):
        self.alloca_builder = ir.IRBuilder()
        self.node = AllocNode()
        self.block: ir.Block | None = None
        self.instr: ir.Instruction | None = None

    def set_block(self, block: ir.Block) -> Allocator:
        self.node = AllocNode(self.node, block)
        self.block = block
        self.instr = None
        return self

    def alloca(self, typ: ir.Type, name: str) -> ir.AllocaInstr:
        assert self.block is not None, 'First call set_block'
        if self.instr is None:
            self.alloca_builder.position_at_start(self.block)
        else:
            self.alloca_builder.position_after(self.instr)

        ret = self.alloca_builder.alloca(typ, name=name)
        self.instr = ret
        self.node.instr = ret

        return ret

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.node = self.node.last_node
        if not self.node:
            self.block = None
            self.instr = None
        else:
            self.block = self.node.block
            self.instr = self.node.instr


class AllocNode:
    def __init__(self, last_node: AllocNode | None = None, block: ir.Block | None = None,
                 instr: ir.Instruction | None = None):
        self.last_node = last_node
        self.block = block
        self.instr = instr
