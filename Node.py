import json
from typing import List

from Token import Token, TT, Position


class Node:
    def __repr__(self):
        return json.dumps(self.json(), indent=2)

    @property
    def pos(self) -> Position:
        pass

    def json(self) -> dict:
        pass


class NumberNode(Node):
    def __init__(self, number: Token):
        self.token = number

    @property
    def pos(self) -> Position:
        return self.token.pos

    def json(self) -> dict:
        return {'type': 'number', 'number': self.token.__str__()}


class BinOpNode(Node):
    def __init__(self, left: Node, operator: Token, right: Node):
        self.left = left
        self.operator = operator
        self.right = right

    @property
    def pos(self) -> Position:
        return self.left.pos

    def json(self) -> dict:
        return {'type': 'bin_op', 'left': self.left.json(), 'operator': self.operator.__str__(),
                'right': self.right.json()}


class UnaryOpNode(Node):
    def __init__(self, operator: Token, node: Node):
        self.operator = operator
        self.node = node

    @property
    def pos(self) -> Position:
        return self.operator.pos

    def json(self) -> dict:
        return {'type': 'unary_op', 'operator': self.operator.__str__(), 'right': self.node.json()}


class VarAccessNode(Node):
    def __init__(self, name: Token):
        self.name = name

    @property
    def pos(self) -> Position:
        return self.name.pos

    def json(self) -> dict:
        return {'type': 'var_access', 'identifier': self.name.__str__()}


class VarAssignNode(Node):
    def __init__(self, name: Token, type_token: Token | None, value: Node):
        self.name = name
        self.type = type_token
        self.value = value

    @property
    def pos(self) -> Position:
        return self.name.pos

    def json(self) -> dict:
        return {'type': 'var_assign', 'identifier': self.name.__str__(),
                'type_annotation': self.type.__str__() if self.type else 'none', 'value': self.value.json()}


class IfNode(Node):
    def __init__(self, bool_node: Node, expr: Node, else_expr: Node | None):
        self.bool = bool_node
        self.expr = expr
        self.else_expr = else_expr

    @property
    def pos(self) -> Position:
        return self.bool.pos

    def json(self) -> dict:
        return {'type': 'if', 'if': self.bool.json(), 'then': self.expr.json(),
                'else': self.else_expr.json() if self.else_expr else 'none'}


class WhileNode(Node):
    def __init__(self, bool_node: Node, expr: Node):
        self.bool = bool_node
        self.expr = expr

    @property
    def pos(self) -> Position:
        return self.bool.pos

    def json(self) -> dict:
        return {'type': 'while', 'while': self.bool.json(), 'then': self.expr.json()}


class ForNode(Node):
    def __init__(self, identifier: Token, from_node: Node, to: Node, step: Node | None, expr: Node):
        self.identifier = identifier
        self.from_node = from_node
        self.to = to
        self.step = step if step else NumberNode(Token(TT.INT, 1, identifier.pos))
        self.expr = expr

    @property
    def pos(self) -> Position:
        return self.identifier.pos

    def json(self) -> dict:
        return {'type': 'for', 'var_name': self.identifier.__str__(), 'from': self.from_node.json(),
                'to': self.to.json(), 'step': self.step.json() if self.step.__str__() else 'none',
                'then': self.expr.json()}


class FunCallNode(Node):
    def __init__(self, identifier: Token, args: List[Node]):
        self.identifier = identifier
        self.args = args

    @property
    def pos(self) -> Position:
        return self.identifier.pos

    def json(self) -> dict:
        args = [a.json() for a in self.args]
        return {'type': 'fun_call', 'identifier': self.identifier.__str__(), 'args': args}


class FunDefNode(Node):
    def __init__(self, identifier: Token, args: List[Token], arg_types: List[Token], body: Node, return_type: Token):
        self.identifier = identifier
        self.args = args
        self.arg_types = arg_types
        self.body = body
        self.return_type = return_type

    @property
    def pos(self) -> Position:
        return self.identifier.pos

    def json(self) -> dict:
        args = [a.__str__() for a in self.args]
        arg_types = [at.__str__() for at in self.arg_types]
        params = dict(zip(args, arg_types))
        return {'type': 'fun_def', 'identifier': self.identifier.__str__(), 'params': params,
                'fun_body': self.body.json(), 'ret_type': self.return_type.__str__()}


class StringNode(Node):
    def __init__(self, value: Token):
        self.value = value

    @property
    def pos(self) -> Position:
        return self.value.pos

    def json(self) -> dict:
        return {'type': 'str', 'value': self.value.__str__()}


class ListNode(Node):
    def __init__(self, content: List[Node]):
        self.content = content

    @property
    def pos(self) -> Position:
        return self.content[1].pos

    def json(self) -> dict:
        exprs = [e.json() for e in self.content]
        return {'type': 'list', 'content': exprs}


class StatementNode(Node):
    def __init__(self, expressions: List[Node]):
        self.expressions = expressions

    @property
    def pos(self) -> Position:
        return self.expressions[1].pos

    def json(self) -> dict:
        exprs = [e.json() for e in self.expressions]
        return {'type': 'statement', 'body': exprs}


class ListAssignNode(Node):
    def __init__(self, lst: Node, index: Node, value: Node):
        self.list = lst
        self.index = index
        self.value = value

    @property
    def pos(self) -> Position:
        return self.list.pos

    def json(self) -> dict:
        return {'type': 'list_assign', 'list': self.list.json(), 'index': self.index.__str__(),
                'value': self.value.json()}


class StructDefNode(Node):
    def __init__(self, identifier: Token, values: dict[Token, Token], functions: list[Node]):
        self.values = values
        self.identifier = identifier
        self.functions = functions

    @property
    def pos(self) -> Position:
        return self.identifier.pos

    def json(self) -> dict:
        funcs = [f.json() for f in self.functions]
        return {'type': 'class_def', 'fields': self.values.__str__(), 'functions': funcs}


class StructAssignNode(Node):
    def __init__(self, obj: Node, key: Token, value: Node):
        self.obj = obj
        self.key = key
        self.value = value

    @property
    def pos(self) -> Position:
        return self.obj.pos

    def json(self) -> dict:
        return {'type': 'object_assign', 'object': self.obj.json(), 'key': self.key.__str__(),
                'value': self.value.json()}


class StructReadNode(Node):
    def __init__(self, obj: Node, key: Token):
        self.obj = obj
        self.key = key

    @property
    def pos(self) -> Position:
        return self.obj.pos

    def json(self) -> dict:
        return {'type': 'object_read', 'object': self.obj.json(), 'key': self.key.__str__()}


class ImportNode(Node):
    def __init__(self, file_path: Token):
        self.file_path = file_path

    @property
    def pos(self) -> Position:
        return self.file_path.pos

    def json(self) -> dict:
        return {'type': 'import', 'file': self.file_path.__str__()}


class PassNode(Node):
    def __init__(self, pos: Position):
        self.position = pos

    def json(self) -> dict:
        return {'type': 'pass'}

    @property
    def pos(self) -> Position:
        return self.position


class ReturnNode(Node):
    def __init__(self, value: Node | None, pos: Position):
        self.value = value
        self.position = pos

    @property
    def pos(self) -> Position:
        return self.position

    def json(self) -> dict:
        return {'type': 'return', 'value': self.value.json() if self.value else 'none'}


class BreakNode(Node):
    def __init__(self, pos: Position):
        self.position = pos

    @property
    def pos(self) -> Position:
        return self.position

    def json(self) -> dict:
        return {'type': 'break'}


class ContinueNode(Node):
    def __init__(self, pos: Position):
        self.position = pos

    @property
    def pos(self) -> Position:
        return self.position

    def json(self) -> dict:
        return {'type': 'continue'}
