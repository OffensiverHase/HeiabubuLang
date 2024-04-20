from typing import Callable

from Context import Context
from Error import Error, InvalidSyntaxError
from Node import *
from Token import Token, TT


class Parser:
    def __init__(self, tokens: List[Token], context: Context):
        self.context = context
        self.tokens = tokens
        self.index = -1
        self.current_token: Token | None = None
        self.advance()

    def advance(self):
        self.index += 1
        self.current_token = self.tokens[self.index] if self.index < len(self.tokens) else None

    def peek(self) -> Token:
        return self.tokens[self.index + 1]

    def parse(self) -> Node | Error:
        if self.current_token.type == TT.EOF:
            return BreakNode()
        result = self.statement()
        if isinstance(result, Error):
            return result
        self.ignore_newlines()
        if self.current_token.type != TT.EOF:
            return self.err(f'Expected expression, got {self.current_token}')
        return result

    def atom(self) -> Node | Error:
        match self.current_token.type:
            case TT.INT:
                token = self.current_token
                self.advance()
                return NumberNode(token)
            case TT.FLOAT:
                token = self.current_token
                self.advance()
                return NumberNode(token)
            case TT.IDENTIFIER:
                token = self.current_token
                self.advance()
                if self.current_token.type == TT.LPAREN:
                    self.advance()
                    arg_node_list: List[Node] = []
                    if self.current_token.type == TT.RPAREN:
                        self.advance()
                        return FunCallNode(token, arg_node_list)
                    else:
                        op_expr = self.op_expr()
                        if isinstance(op_expr, Error):
                            return op_expr
                        arg_node_list.append(op_expr)
                    while self.current_token.type == TT.COMMA:
                        self.advance()
                        param = self.op_expr()
                        if isinstance(param, Error):
                            return param
                        arg_node_list.append(param)
                    if self.current_token.type != TT.RPAREN:
                        return self.err(f"Expected ')', got {self.current_token}")
                    self.advance()
                    return FunCallNode(token, arg_node_list)
                elif self.current_token.type == TT.DOT:
                    self.advance()
                    if self.current_token.type != TT.IDENTIFIER:
                        return self.err(f"Expected identifier after '.', got {self.current_token}")
                    key = self.current_token
                    self.advance()
                    if self.current_token.type == TT.ASSIGN:
                        self.advance()
                        value = self.atom()
                        if isinstance(value, Error):
                            return value
                        return ObjectAssignNode(VarAccessNode(token), key, value)
                    return ObjectReadNode(VarAccessNode(token), key)
                return VarAccessNode(token)
            case TT.LPAREN:
                self.advance()
                expression = self.expression()
                if self.current_token.type == TT.RPAREN:
                    self.advance()
                    return expression
                else:
                    return self.err(f"Expected ')', got {self.current_token}")
            case TT.STRING:
                token = self.current_token
                self.advance()
                return StringNode(token)
            case TT.LSQUARE:
                lst: List[Node] = []
                self.advance()
                if self.current_token.type == TT.RSQUARE:
                    self.advance()
                else:
                    value = self.atom()
                    if isinstance(value, Error):
                        return value
                    lst.append(value)
                    while self.current_token.type == TT.COMMA:
                        self.advance()
                        val = self.atom()
                        if isinstance(val, Error):
                            return val
                        lst.append(val)
                    if self.current_token.type != TT.RSQUARE:
                        return self.err(f"Expected ']' or ',', got {self.current_token}")
                    self.advance()
                return ListNode(lst)
            case TT.KEYWORD:
                match self.current_token.value:
                    case 'IF':
                        self.advance()
                        bool_expr = self.op_expr()
                        if isinstance(bool_expr, Error):
                            return bool_expr
                        if_expr = self.body_expr()
                        if isinstance(if_expr, Error):
                            return if_expr
                        else_expr: Node | None | Error = None
                        if self.current_token.type == TT.NEWLINE and self.peek().value == 'ELSE':
                            self.advance()
                        if self.current_token.value == 'ELSE':
                            self.advance()
                            else_expr = self.body_expr()
                        if isinstance(else_expr, Error):
                            return else_expr
                        return IfNode(bool_expr, if_expr, else_expr)
                    case 'OBJECT':
                        self.advance()
                        if self.current_token.type != TT.LCURLY:
                            return self.err("Expected '{' or ':', got " + f"{self.current_token}")
                        self.advance()
                        self.ignore_newlines()
                        values: dict[Token, Node] = dict()
                        while self.current_token.type == TT.IDENTIFIER:
                            key = self.current_token
                            self.advance()
                            if self.current_token.type != TT.ASSIGN:
                                return self.err(f"Expected '<-', got {self.current_token}")
                            self.advance()
                            value = self.atom()
                            if isinstance(value, Error):
                                return value
                            values[key] = value
                            if self.current_token.type != TT.NEWLINE and self.current_token.type != TT.RCURLY:
                                return self.err("Expected newline, ';' or '}', got " + f"{self.current_token}")
                            if self.current_token.type != TT.RCURLY:
                                self.advance()
                            self.ignore_newlines()
                        if self.current_token.type != TT.RCURLY:
                            return self.err("Expected newline, ';' or '}', got " + f'{self.current_token}')
                        self.advance()
                        return ObjectNode(values)
                    case _:
                        return self.err(f'Expected object or if, got {self.current_token}')
            case _:
                return self.err(f'Expected identifier, literal or if, got {self.current_token}')

    def power(self) -> Node | Error:
        left = self.atom()
        if isinstance(left, Error):
            return left
        if self.current_token.type == TT.LSQUARE:
            operator = Token(TT.GET, None, self.current_token.pos)
            self.advance()
            right = self.arithm_expr()
            if isinstance(right, Error):
                return right
            if self.current_token.type != TT.RSQUARE:
                return self.err(f"Expected '] after [ with list index, got {self.current_token}")
            self.advance()
            left = BinOpNode(left, operator, right)
            if self.current_token.type == TT.ASSIGN:
                self.advance()
                right = self.atom()
                if isinstance(right, Error):
                    return right
                list_node = left.left
                index = left.right
                left = ListAssignNode(list_node, index, right)
        while self.current_token.type == TT.POW:
            operator = self.current_token
            self.advance()
            right = self.factor()
            if isinstance(right, Error):
                return right
            left = BinOpNode(left, operator, right)
        return left

    def factor(self) -> Node | Error:
        if self.current_token.type == TT.PLUS or self.current_token.type == TT.MINUS:
            unary = self.current_token
            self.advance()
            right = self.power()
            if isinstance(right, Error):
                return right
            return UnaryOpNode(unary, right)
        return self.power()

    def term(self) -> Node | Error:
        left = self.bin_op_node([TT.MUL, TT.DIV, TT.MOD], self.factor)
        return left

    def arithm_expr(self) -> Node | Error:
        left = self.bin_op_node([TT.PLUS, TT.MINUS], self.term)
        return left

    def comp_expr(self) -> Node | Error:
        if self.current_token.type == TT.NOT:
            operator = self.current_token
            self.advance()
            val = self.comp_expr()
            if isinstance(val, Error):
                return val
            return UnaryOpNode(operator, val)

        left = self.bin_op_node([TT.EQUALS, TT.UNEQUALS, TT.LESS, TT.GREATER, TT.LESSEQUAL, TT.GREATEREQUAL], self.arithm_expr)
        return left

    def op_expr(self) -> Node | Error:
        left = self.bin_op_node([TT.AND, TT.OR, TT.XOR], self.comp_expr)
        return left

    def expression(self) -> Node | Error:
        self.ignore_newlines()
        token = self.current_token
        if token.type == TT.KEYWORD:
            match token.value:
                case 'WHILE':
                    self.advance()
                    bool_expr = self.op_expr()
                    if isinstance(bool_expr, Error):
                        return bool_expr
                    expr = self.body_expr()
                    if isinstance(expr, Error):
                        return expr
                    return WhileNode(bool_expr, expr)
                case 'FOR':
                    self.advance()
                    if self.current_token.type != TT.IDENTIFIER:
                        return self.err(f'Expected identifier in for, got {self.current_token}')
                    identifier = self.current_token
                    self.advance()
                    if self.current_token.type != TT.ASSIGN:
                        return self.err(f'Expected <-, got {self.current_token}')
                    self.advance()
                    from_expr = self.factor()
                    if isinstance(from_expr, Error):
                        return from_expr
                    if self.current_token.type != TT.TO:
                        return self.err(f'Expected .. in for, got {self.current_token}')
                    self.advance()
                    to = self.arithm_expr()
                    if isinstance(to, Error):
                        return to
                    step: Node | Error | None = None
                    if self.current_token.value == 'STEP':
                        self.advance()
                        step = self.factor()
                        if isinstance(step, Error):
                            return step
                    expr = self.body_expr()
                    if isinstance(expr, Error):
                        return expr
                    return ForNode(identifier, from_expr, to, step, expr)
                case 'FUN':
                    self.advance()
                    if self.current_token.type != TT.IDENTIFIER:
                        return self.err(f'Expected identifier, got {self.current_token}')
                    identifier = self.current_token
                    self.advance()
                    if self.current_token.type != TT.LPAREN:
                        return self.err(f"Expected '(', got {self.current_token}")
                    self.advance()
                    arg_list: List[Token] = []
                    arg_types: List[Token] = []
                    if self.current_token.type == TT.IDENTIFIER:
                        arg_list.append(self.current_token)
                        self.advance()
                        if self.current_token.type != TT.COLON:
                            return self.err(f"Expected ':' for type, got {self.current_token}")
                        self.advance()
                        if self.current_token.type != TT.TYPE:
                            return self.err(f'Expected type, got {self.current_token}')
                        arg_types.append(self.current_token)
                        self.advance()
                    while self.current_token.type == TT.COMMA:
                        self.advance()
                        if self.current_token.type != TT.IDENTIFIER:
                            return self.err(f'Expected identifier, got {self.current_token}')
                        arg_list.append(self.current_token)
                        self.advance()
                        if self.current_token.type != TT.COLON:
                            return self.err(f"Expected ':' for type, got {self.current_token}")
                        self.advance()
                        if self.current_token.type != TT.TYPE:
                            return self.err(f'Expected type, got {self.current_token}')
                        arg_types.append(self.current_token)
                        self.advance()
                    if self.current_token.type != TT.RPAREN:
                        return self.err(f"Expected ')', got {self.current_token}")
                    self.advance()
                    return_type = Token(TT.TYPE, 'null', self.current_token.pos)
                    if self.current_token.type == TT.ARROW:
                        self.advance()
                        if self.current_token.type != TT.TYPE:
                            return self.err(f'Expected type, got {self.current_token}')
                        return_type = self.current_token
                        self.advance()
                    body_node = self.body_expr()
                    if isinstance(body_node, Error):
                        return body_node
                    return FunDefNode(identifier, arg_list, arg_types, body_node, return_type)
                case 'PASS':
                    self.advance()
                    return PassNode()
                case 'RETURN':
                    self.advance()
                    if self.current_token.type == TT.NEWLINE or self.current_token.type == TT.EOF:
                        return ReturnNode(None)
                    val = self.op_expr()
                    if isinstance(val, Error):
                        return val
                    return ReturnNode(val)
                case 'BREAK':
                    self.advance()
                    return BreakNode()
                case 'CONTINUE':
                    self.advance()
                    return ContinueNode()
        elif self.current_token.type == TT.IDENTIFIER:
            var_name = self.current_token
            if self.peek().type in [TT.COLON, TT.ASSIGN]:
                self.advance()  # to the : or <-
                self.advance()  # past the : or <-
                type_token: Token | None = None
                if self.current_token.type == TT.TYPE:
                    type_token = self.current_token
                    self.advance()
                    if self.current_token.type != TT.ASSIGN:
                        return self.err(f"Expected '<-', got {self.current_token}")
                    self.advance()
                expr = self.expression()
                if isinstance(expr, Error):
                    return expr
                return VarAssignNode(var_name, type_token, expr)
        return self.op_expr()

    def statement(self) -> Node | Error:
        self.ignore_newlines()
        expressions: List[Node] = []
        expr = self.expression()
        if isinstance(expr, Error):
            return expr
        expressions.append(expr)

        while self.current_token.type == TT.NEWLINE:
            self.ignore_newlines()
            if self.current_token.type == TT.RCURLY or self.current_token.type == TT.EOF:
                if self.current_token.type == TT.RCURLY:
                    self.advance()
                break
            expr = self.expression()
            if isinstance(expr, Error):
                return expr
            expressions.append(expr)
        return StatementNode(expressions)

    def ignore_newlines(self):
        while self.current_token.type == TT.NEWLINE:
            self.advance()

    def body_expr(self) -> Node | Error:
        match self.current_token.type:
            case TT.LCURLY:
                self.advance()
                return self.statement()
            case TT.COLON:
                self.advance()
                return self.expression()
            case _:
                return self.err("Expected '{' or ':', got " + f"{self.current_token}")

    def bin_op_node(self, tokens: List[TT], func: Callable[[], Node | Error]) -> Node | Error:
        left = func()
        if isinstance(left, Error):
            return left
        while self.current_token.type in tokens:
            operator = self.current_token
            self.advance()
            right = func()
            if isinstance(right, Error):
                return right
            left = BinOpNode(left, operator, right)
        return left

    def err(self, details: str) -> Error:
        return InvalidSyntaxError(details, self.current_token.pos, self.context, 'parsing')
