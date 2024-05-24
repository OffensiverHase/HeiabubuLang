from __future__ import annotations

from typing import NoReturn

from Error import *
from Node import *


class Analyser:
    def __init__(self, ctx: Context):
        self.context = ctx
        self.env = Env()
        self.funcs: dict[str, Fun] = {}
        self.structs: dict[str, Struct] = {}
        self.current_fun: Fun = Fun(f'load_{ctx.file}', 0, [], 'null')

    def check(self, node: Node) -> str | None:
        method = getattr(self, 'check' + node.__class__.__name__, self.check_unknown_node)
        return method(node)

    def checkNumberNode(self, node: NumberNode) -> str:
        return 'int' if node.token.type == TT.INT else 'float' if node.token.type == TT.FLOAT else self.err(
            UnknownNodeError, f'Number node has to have either int or float Token, got {node.token.type}', node.pos)

    def checkBinOpNode(self, node: BinOpNode) -> str:
        left_type = self.check(node.left)
        right_type = self.check(node.right)
        if left_type is None or right_type is None:
            self.err(TypeError, 'Expected expression, got statement',
                     node.left.pos if left_type is None else node.right.pos)
        match node.operator.type:
            case TT.PLUS:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float'), ('str', 'str')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
                elif left_type.startswith('list:') and right_type.startswith('list:') and left_type == right_type:
                    return left_type
            case TT.MINUS:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
            case TT.MUL:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
            case TT.DIV:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
            case TT.MOD:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
            case TT.POW:
                if (left_type, right_type) in [('int', 'int'), ('float', 'float')]:
                    return left_type
                elif (left_type, right_type) in [('int', 'float'), ('float', 'int')]:
                    return 'float'
            case TT.EQUALS:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.UNEQUALS:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.LESS:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.LESSEQUAL:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.GREATER:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.GREATEREQUAL:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot compare two different types with =', node.operator.pos)
                return 'bool'
            case TT.AND:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot operate two different types with &', node.operator.pos)
                return left_type
            case TT.OR:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot operate two different types with |', node.operator.pos)
                return left_type
            case TT.XOR:
                if left_type != right_type:
                    self.err(TypeError, f'Cannot operate two different types with ~', node.operator.pos)
                return left_type
            case TT.GET:
                if not left_type.startswith('list:') and not left_type == 'str':
                    self.err(TypeError, 'Cannot index non list or str', node.left.pos)
                if not right_type == 'int':
                    self.err(TypeError, 'Cannot index with non int value', node.right.pos)

        self.err(TypeError, f'cannot find operator {node.operator} on {left_type} and {right_type}', node.operator.pos)

    def checkUnaryOpNode(self, node: UnaryOpNode) -> str:
        typ = self.check(node.value)
        if typ == 'int':
            return typ
        elif typ == 'float':
            if node.operator.type == TT.NOT:
                self.err(TypeError, 'Can only use not on int or bool value', node.operator.pos)
        elif typ == 'bool':
            if node.operator.type != TT.NOT:
                self.err(TypeError, f'Cannot operate with {node.operator} on bool', node.operator.pos)

    def checkVarAccessNode(self, node: VarAccessNode) -> str:
        res = self.env.get(node.name.value)
        if res:
            return res
        self.err(NoSuchVarError, f'Variable {node.name.value} is not defined in the current scope', node.pos)

    def checkVarAssignNode(self, node: VarAssignNode) -> None:
        value_type = self.check(node.value)
        if node.type is not None and node.type.value != value_type:
            self.err(TypeError, f'Expected {node.type}, got {value_type}', node.value.pos)
        self.env.define(node.name.value, value_type)

    def checkIfNode(self, node: IfNode) -> None:
        bool_value = self.check(node.bool)
        if bool_value != 'bool':
            self.err(TypeError, f'Expected bool, got {bool_value}', node.bool.pos)

        self.env = Env(self.env)
        self.check(node.expr)
        self.check(node.else_expr)
        self.env = self.env.parent

    def checkWhileNode(self, node: WhileNode) -> None:
        bool_value = self.check(node.bool)
        if bool_value != 'bool':
            self.err(TypeError, f'Expected bool, got {bool_value}', node.bool.pos)

        self.env = Env(self.env)
        self.check(node.expr)
        self.env = self.env.parent

    def checkForNode(self, node: ForNode) -> None:
        from_type = self.check(node.from_node)
        to_type = self.check(node.to)
        step_type = self.check(node.step) if node.step else 'int'
        if from_type != to_type != step_type != 'int':
            self.err(TypeError, f'Expected int, got {from_type}, {to_type} and {step_type}', node.from_node.pos)

        self.env = Env(self.env)
        self.env.define(node.identifier.value, 'int')
        self.check(node.expr)
        self.env = self.env.parent

    def checkFunCallNode(self, node: FunCallNode) -> str:
        if node.identifier.value not in self.funcs:
            self.err(NoSuchVarError, f'Function {node.identifier.value} is not defined in the current scope', node.pos)
        fun_helper = self.funcs[node.identifier.value]
        if fun_helper.argc != len(node.args):
            self.err(TypeError,
                     f'Function {fun_helper.name} expected {fun_helper.argc} arguments, got {len(node.args)}', node.pos)
        for i, arg in enumerate(node.args):
            arg_type = self.check(arg)
            if arg_type != fun_helper.arg_types[i]:
                self.err(TypeError,
                         f'Function {fun_helper.name} expected {fun_helper.arg_types[i]} for the {i}th element, found {arg_type}',
                         arg.pos)
        return fun_helper.ret_type

    def checkFunDefNode(self, node: FunDefNode) -> None:
        self.env = Env(self.env)
        self.context = Context(self.context, node.identifier.value, self.context.file, self.context.file_text)

        for i, arg in enumerate(node.args):
            self.env.define(arg.value, node.arg_types[i].value)
        self.check(node.body)
        fun_helper = Fun(node.identifier.value, len(node.arg_types), [arg_type.value for arg_type in node.arg_types],
                         node.return_type.value)
        self.current_fun = fun_helper
        self.funcs[node.identifier.value] = fun_helper

        self.context = self.context.parent
        self.env = self.env.parent

    def checkStringNode(self, node: StringNode) -> str:
        return 'str'

    def checkListNode(self, node: ListNode) -> str:
        if len(node.content) == 0:
            return 'list:int'
        list_type = self.check(node.content[0])
        for n in node.content:
            node_type = self.check(n)
            if node_type != list_type:
                self.err(TypeError, f'Expected {list_type}, got {node_type}', n.pos)
        return f'list:{list_type}'

    def checkStatementsNode(self, node: StatementsNode) -> None:
        for statement in node.expressions:
            self.check(statement)

    def checkListAssignNode(self, node: ListAssignNode) -> None:
        list_type = self.check(node.list)
        if not list_type.startswith('list:'):
            self.err(TypeError, 'Cannot index non list!', node.list.pos)
        list_type = list_type.removeprefix('list:')
        value_type = self.check(node.value)
        if value_type != list_type:
            self.err(TypeError, f'Expected {list_type}, got {value_type}', node.value.pos)
        index_type = self.check(node.index)
        if index_type != 'int':
            self.err(TypeError, f'Cannot index list with non integer, got {index_type}', node.index.pos)

    def checkStructDefNode(self, node: StructDefNode) -> None:
        fields: dict[str, str] = {}
        for name, typ in node.values:
            fields[name.value] = typ.value
        struct_helper = Struct(node.identifier.value, fields)
        self.structs[struct_helper.name] = struct_helper
        for fun in node.functions:
            self.check(fun)

    def checkStructAssignNode(self, node: StructAssignNode) -> None:
        obj_type = self.check(node.obj)
        struct_helper = self.structs[obj_type]
        if node.key.value not in struct_helper.fields:
            self.err(NoSuchVarError, f'Class {obj_type} does not have an attribute called {node.key.value}', node.key.pos)
        field_type = struct_helper.fields[node.key.value]
        value_type = self.check(node.value)
        if value_type != field_type:
            self.err(TypeError, f'Expected {field_type} for attribute {node.key.value}, got {value_type}', node.key.pos)

    def checkStructReadNode(self, node: StructReadNode) -> str:
        obj_type = self.check(node.obj)
        struct_helper = self.structs[obj_type]
        if node.key.value not in struct_helper.fields:
            self.err(NoSuchVarError, f'Class {obj_type} does not have an attribute called {node.key.value}',
                     node.key.pos)
        return struct_helper.fields[node.key.value]

    def checkImportNode(self, node: ImportNode) -> None:
        self.check(node.file_path.value)

    def checkPassNode(self, node: PassNode) -> None:
        pass

    def checkReturnNode(self, node: ReturnNode) -> None:
        ret_type = self.check(node.value) if node.value else 'null'
        if self.current_fun and ret_type != self.current_fun.ret_type:
            self.err(TypeError, f'Expected {self.current_fun.ret_type} as return type, got {ret_type}', node.pos)

    def checkBreakNode(self, node: BreakNode) -> None:
        pass  # Do the checks in IrBuilder

    def checkContinueNode(self, node: ContinueNode) -> None:
        pass  # Do the checks in IrBuilder

    def check_unknown_node(self, node):
        self.err(UnknownNodeError, f'Tried to resolve unknown node: {node.__class__.__name__}!\nnode json:\n{node}\n',
                 node.pos)

    def err(self, err_class: Error.__class__, message: str, pos: Position) -> NoReturn:
        err = err_class(message, pos, self.context, 'semantic-analysis')
        assert isinstance(err, Error), 'Error has to be a instance of self defined Error to be excepted'
        raise err


class Env:
    def __init__(self, parent: Env | None = None):
        self.parent = parent
        self.records: dict[str, str] = {'true': 'bool', 'false': 'bool'} if not self.parent else {}

    def define(self, key: str, value: str):
        self.records[key] = value

    def get(self, key: str) -> str | None:
        if key in self.records:
            return self.records[key]
        elif self.parent:
            return self.parent.get(key)
        else:
            return None


class Fun:
    def __init__(self, name: str, argc: int, argt: list[str], ret_type: str):
        self.name = name
        self.argc = argc
        self.arg_types = argt
        self.ret_type = ret_type


class Struct:
    def __init__(self, name: str, fields: dict[str, str]):
        self.name = name
        self.fields = fields
