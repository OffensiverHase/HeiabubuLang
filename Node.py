from typing import List

from Token import Token, TT


class Node:
    def __repr__(self):
        return self.__str__()


class NumberNode(Node):
    def __init__(self, number: Token):
        self.token = number

    def __str__(self):
        return self.token.__str__()


class BinOpNode(Node):
    def __init__(self, left: Node, operator: Token, right: Node):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f'({self.left, self.operator, self.right}'


class UnaryOpNode(Node):
    def __init__(self, operator: Token, node: Node):
        self.operator = operator
        self.node = node

    def __str__(self):
        return f'({self.operator, self.node})'


class VarAccessNode(Node):
    def __init__(self, name: Token):
        self.name = name

    def __str__(self):
        return f'({self.name})'


class VarAssignNode(Node):
    def __init__(self, name: Token, type_token: Token | None, value: Node):
        self.name = name
        self.type = type_token
        self.value = value

    def __str__(self):
        if self.type:
            return f'({self.name}: {self.type} <- {self.value})'
        else:
            return f'({self.name} <- {self.value})'


class IfNode(Node):
    def __init__(self, bool_node: Node, expr: Node, else_expr: Node | None):
        self.bool = bool_node
        self.expr = expr
        self.else_expr = else_expr

    def __str__(self):
        return f'(if {self.bool} { {self.expr} } else { {self.else_expr} })' if self.else_expr else f'(if {self.bool} { {self.expr} })'


class WhileNode(Node):
    def __init__(self, bool_node: Node, expr: Node):
        self.bool = bool_node
        self.expr = expr

    def __str__(self):
        return f'(while {self.bool} { {self.expr} })'


class ForNode(Node):
    def __init__(self, identifier: Token, from_node: Node, to: Node, step: Node | None, expr: Node):
        self.identifier = identifier
        self.from_node = from_node
        self.to = to
        self.step = step if step else NumberNode(Token(TT.INT, 1, identifier.pos))
        self.expr = expr

    def __str__(self):
        if self.step != 1:
            return f'(for {self.identifier} <- {self.from_node} .. {self.to} step {self.step} { {self.expr} })'
        else:
            return f'(for {self.identifier} <- {self.from_node} .. {self.to} { {self.expr} })'


class FunCallNode(Node):
    def __init__(self, identifier: Token, args: List[Node]):
        self.identifier = identifier
        self.args = args

    def __str__(self):
        return f'({self.identifier}({self.args.__str__().removeprefix('[').removesuffix(']')}))'


class FunDefNode(Node):
    def __init__(self, identifier: Token, args: List[Token], arg_types: List[Token], body: Node, return_type: Token):
        self.identifier = identifier
        self.args = args
        self.arg_types = arg_types
        self.body = body
        self.return_type = return_type

    def __str__(self):
        params = ''
        for i in range(len(self.args)):
            params += f'{self.args[i].value}: {self.arg_types[i].value}, '

        return f'(fun {self.identifier}({params}) -> {self.return_type} { {self.body} })'


class StringNode(Node):
    def __init__(self, value: Token):
        self.value = value

    def __str__(self):
        return f"('{self.value}')"


class ListNode(Node):
    def __init__(self, content: List[Node]):
        self.content = content

    def __str__(self):
        return f'({self.content.__str__()})'


class StatementNode(Node):
    def __init__(self, expressions: List[Node]):
        self.expressions = expressions

    def __str__(self):
        return f'({self.expressions.__str__().removeprefix('[').removesuffix(']')})'


class ListAssignNode(Node):
    def __init__(self, lst: Node, index: Node, value: Node):
        self.list = lst
        self.index = index
        self.value = value

    def __str__(self):
        return f'({self.list}[{self.index}] <- {self.value})'


class StructDefNode(Node):
    def __init__(self, identifier: Token, values: dict[Token, Token]):
        self.values = values
        self.identifier = identifier

    def __str__(self):
        return f'(struct {self.identifier} {self.values} )'


class StructAssignNode(Node):
    def __init__(self, obj: Node, key: Token, value: Node):
        self.obj = obj
        self.key = key
        self.value = value

    def __str__(self):
        return f'({self.obj}.{self.key} <- {self.value})'


class StructReadNode(Node):
    def __init__(self, obj: Node, key: Token):
        self.obj = obj
        self.key = key

    def __str__(self):
        return f'({self.obj}.{self.key})'


class ImportNode(Node):
    def __init__(self, file_path: Token):
        self.file_path = file_path

    def __str__(self):
        return f'(import {self.file_path})'


class PassNode(Node):
    def __str__(self):
        return '(pass)'


class ReturnNode(Node):
    def __init__(self, value: Node | None):
        self.value = value

    def __str__(self):
        return f'(return {self.value})' if self.value else '(return)'


class BreakNode(Node):
    def __str__(self):
        return '(break)'


class ContinueNode(Node):
    def __str__(self):
        return '(continue)'
