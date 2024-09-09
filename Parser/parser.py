from Parser.astNode import NumberNode, BinaryOperationNode, UnaryOperationNode, BooleanNode, WhileNode, AccessNode, \
    FunctionDefinitionNode, FunctionCallNode, LambdaNode, ContinueNode, BreakNode, ReturnNode
from error import InvalidSyntaxError
from Lexer.mytoken import Tokens


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_pos = -1
        self.current_token = None
        self.advance()
        self.tempFunc = False
        self.tempLoop = False

    # Move to the next token and update current_token
    def advance(self):
        self.tokens_pos += 1
        if self.tokens_pos < len(self.tokens):
            self.current_token = self.tokens[self.tokens_pos]
        else:
            return self.current_token

    # Main parsing function - attempts to parse multiple statements
    def parse(self):
        result = self.statements()
        if not result.error and self.current_token.type != Tokens.EOF:
            return result.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
                                                     "Unexpected token"))
        return result

    # Parse a standard expression that can include addition or subtraction
    def parse_expression(self):
        return self.binary_operation(self.parse_term, (Tokens.ADD, Tokens.SUB))

    # Parse a boolean expression that can include AND or OR conditions
    def parse_boolean_expression(self):
        return self.binary_operation(self.parse_boolean_term, (Tokens.OR, Tokens.AND))

    # Parse a term in an expression that can include multiplication or division
    def parse_term(self):
        return self.binary_operation(self.parse_factor, (Tokens.MUL, Tokens.DIV, Tokens.INTEGER_DIV, Tokens.MOD))

    # Parse a boolean term that can include equality or inequality comparisons
    def parse_boolean_term(self):
        return self.binary_operation(self.parse_boolean_factor, (Tokens.EQUAL, Tokens.NOT_EQUAL))

    # Parse a boolean factor, which can be TRUE/FALSE or a logical operation like NOT
    def parse_boolean_factor(self):
        result = ParseResult()
        token = self.current_token
        if token.type == Tokens.BOOL:
            result.register_advancement()
            self.advance()
            return result.success(BooleanNode(token))
        elif token.type == Tokens.NOT:
            result.register_advancement()
            self.advance()
            factor = result.register(self.parse_boolean_factor())
            if result.error:
                return result
            return result.success(UnaryOperationNode(token, factor))
        else:
            compare = result.register(self.compare_expression())
            if result.error:
                return result
            return result.success(compare)

    # Parse a factor in an expression, which can be a number or an expression within parentheses
    def parse_factor(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (Tokens.ADD, Tokens.SUB):
            result.register_advancement()
            self.advance()
            factor = result.register(self.parse_factor())
            if result.error:
                return result
            return result.success(UnaryOperationNode(token, factor))
        else:
            call = result.register(self.call_expression())
            if result.error:
                return result
            return result.success(call)

    # Generic function to parse binary operations like addition, subtraction, AND, OR
    def binary_operation(self, function, options):
        result = ParseResult()
        left = result.register(function())
        if result.error:
            return result
        while self.current_token.type in options:
            operand = self.current_token
            result.register_advancement()
            self.advance()
            right = result.register(function())
            if result.error:
                return result
            left = BinaryOperationNode(left, operand, right)
        return result.success(left)

    # Parse comparison expressions like less than, greater than, etc.
    def compare_expression(self):
        return self.binary_operation(self.parse_expression, (Tokens.LESS, Tokens.LESS_EQUAL,
                                                             Tokens.GREATER, Tokens.GREATER_EQUAL,
                                                             Tokens.EQUAL, Tokens.NOT_EQUAL))

    # Parse an expression within parentheses
    def parented_expr(self):
        result = ParseResult()
        token = self.current_token
        result.register_advancement()
        self.advance()
        expression = result.register(self.parse_boolean_expression())
        if result.error:
            return result
        if self.current_token.type == Tokens.RIGHT_PAREN:
            result.register_advancement()
            self.advance()
            return result.success(expression)
        else:
            return result.failure(InvalidSyntaxError(token.position_start_,
                                                     self.current_token.position_end, "Expected ')'"))

    # Parse a WHILE loop expression
    def while_expression(self):
        result = ParseResult()
        token = self.current_token
        result.register_advancement()
        self.advance()
        condition = None
        if self.current_token.type == Tokens.LEFT_PAREN:
            result.register_advancement()
            self.advance()
            condition = result.register(self.parse_boolean_expression())
            if result.error:
                return result
            if self.current_token.type == Tokens.RIGHT_PAREN:
                result.register_advancement()
                self.advance()
            else:
                return result.failure(InvalidSyntaxError(token.position_start, self.current_token.position_end,
                                                         "Expected ')'"))
        if self.current_token.type == Tokens.LEFT_BRACE:
            token = self.current_token
            result.register_advancement()
            self.advance()
            self.tempLoop = True
            body = []
            if self.current_token.type == Tokens.NEWLINE:
                result.register_advancement()
                self.advance()
                body = result.register(self.statements())
                if result.error:
                    return result
            else:
                expression = result.register(self.statement())
                if result.error:
                    return result
                body.append(expression)

            if self.current_token.type == Tokens.RIGHT_BRACE:
                result.register_advancement()
                self.advance()
                self.tempLoop = False
                return result.success(WhileNode(condition, body, self.current_token.position_end))
            else:
                return result.failure(InvalidSyntaxError(token.position_start, self.current_token.position_end,
                                                         "Expected '}'"))
        else:
            return result.failure(InvalidSyntaxError(token.position_start, self.current_token.position_end,
                                                     "Expected '{'"))

    # Parse an atom, which is the most basic unit like a number, identifier, or expression within parentheses
    def atom(self):
        result = ParseResult()
        token = self.current_token
        if token.type in Tokens.INT:
            result.register_advancement()
            self.advance()
            return result.success(NumberNode(token))
        elif token.type in Tokens.IDENTIFIER:
            ID_name = result.register(self.make_identifier(token))
            if result.error:
                return result
            return result.success(ID_name)
        elif token.matches(Tokens.KEYWORD, Tokens.WHILE):
            expression = result.register(self.while_expression())
            if result.error:
                return result
            return result.success(expression)
        elif token.type == Tokens.LEFT_PAREN:
            return self.parented_expr()
        elif token.type == 'function':
            fun_def = result.register(self.function_definition())
            if result.error:
                return result
            return result.success(fun_def)
        elif token.type == Tokens.KEYWORD and token.value == 'lambda':
            def_lambda = result.register(self.def_lambda())
            if result.error:
                return result
            return result.success(def_lambda)
        return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                 "Expected '(,int,while', 'IDENTIFIER', 'FUNCTION' or 'KEYWORD',"
                                                 "'+','-','!','true','false'"))

    # Parse a function definition
    def function_definition(self):
        result = ParseResult()

        if self.current_token == Tokens.FUNCTION:
            return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                     self.current_token.position_end, "Expected 'function'"))

        result.register_advancement()
        self.advance()
        if self.current_token.type == Tokens.IDENTIFIER:
            token_name = self.current_token
            result.register_advancement()
            self.advance()
            if self.current_token.type != Tokens.LEFT_PAREN:
                return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                         self.current_token.position_end, "Expected '('"))
        else:
            token_name = None
            if self.current_token.type != Tokens.LEFT_PAREN:
                return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                         self.current_token.position_end,
                                                         "Expected IDENTIFIER or '('"))
        result.register_advancement()
        self.advance()
        arg_name = []
        if self.current_token.type == Tokens.IDENTIFIER:
            arg_name.append(self.current_token)
            result.register_advancement()
            self.advance()
            while self.current_token.type == Tokens.COMMA:
                result.register_advancement()
                self.advance()
                if self.current_token.type != Tokens.IDENTIFIER:
                    return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                             self.current_token.position_end,
                                                             "Expected IDENTIFIER"))
                arg_name.append(self.current_token)
                result.register_advancement()
                self.advance()
            if self.current_token.type != Tokens.RIGHT_PAREN:
                return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                         self.current_token.position_end,
                                                         "Expected ',' or ')'"))
        else:
            if self.current_token.type != Tokens.RIGHT_PAREN:
                return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                         self.current_token.position_end,
                                                         "Expected IDENTIFIER or ')'"))
        result.register_advancement()
        self.advance()
        if self.current_token.type == Tokens.ARROW:
            result.register_advancement()
            self.advance()
            body = result.register(self.parse_boolean_expression())
            if result.error:
                return result
            return result.success(FunctionDefinitionNode(token_name, arg_name, body, True))
        if self.current_token.type != Tokens.NEWLINE:
            return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                     self.current_token.position_end, "Expected '->' or NEWLINE"))
        result.register_advancement()
        self.advance()
        body = result.register(self.statements())
        if result.error:
            return result
        return result.success(FunctionDefinitionNode(token_name, arg_name, body, False))

    # Parse a function call expression
    def call_expression(self):
        result = ParseResult()
        atom = result.register(self.atom())
        if result.error:
            return result
        if self.current_token.type == Tokens.LEFT_PAREN:
            result.register_advancement()
            self.advance()
            arg_nodes = []
            if self.current_token.type == Tokens.RIGHT_PAREN:
                result.register_advancement()
                self.advance()
            else:
                arg_nodes.append(result.register(self.parse_boolean_expression()))
                if result.error:
                    return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                             self.current_token.position_end,
                                                             "Expected ')', 'int',"
                                                             "'IDENTIFIER','FUNCTION','WHILE'"))
                while self.current_token.type == Tokens.COMMA:
                    result.register_advancement()
                    self.advance()
                    arg_nodes.append(result.register(self.parse_boolean_expression()))
                    if result.error:
                        return result
                if self.current_token.type != Tokens.RIGHT_PAREN:
                    return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                             self.current_token.position_end,
                                                             "Expected ',' or ')'"))
                result.register_advancement()
                self.advance()
            return result.success(FunctionCallNode(atom, arg_nodes))
        return result.success(atom)

    # Parse an identifier, typically used to access variables
    def make_identifier(self, token):
        result = ParseResult()
        if token.type == Tokens.IDENTIFIER:
            result.register_advancement()
            self.advance()
            return result.success(AccessNode(token))
        else:
            return result.failure(InvalidSyntaxError(token.position_start, token.position_end, "Expected 'IDENTIFIER'"))

    # Parse a lambda function definition
    def def_lambda(self):
        result = ParseResult()
        if not self.current_token.matches(Tokens.KEYWORD, 'lambda'):
            return result.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
                                                     f"Expected lambda"))
        result.register_advancement()
        self.advance()
        if self.current_token.type in Tokens.IDENTIFIER:
            var_name_tok = self.current_token
            result.register_advancement()
            self.advance()
            if self.current_token.type != Tokens.LEFT_PAREN:
                return result.failure(
                    InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
                                       f"Expected '('"))
        else:
            var_name_tok = None
            if self.current_token.type != Tokens.LEFT_PAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.position_start, self.current_token.position_end, f"Expected identifier or '('"))

        result.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_token.type == Tokens.IDENTIFIER:
            arg_name_toks.append(self.current_token)
            result.register_advancement()
            self.advance()

            while self.current_token.type == Tokens.COMMA:
                result.register_advancement()
                self.advance()

                if self.current_token.type != Tokens.IDENTIFIER:
                    return result.failure(InvalidSyntaxError(self.current_token.position_start, self.current_token.
                                                             position_end, f"Expected identifier"))

                arg_name_toks.append(self.current_token)
                result.register_advancement()
                self.advance()

            if self.current_token.type != Tokens.RIGHT_PAREN:
                return result.failure(
                    InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end,
                                       f"Expected ',' or ')'"))
        else:
            if self.current_token.type != Tokens.RIGHT_PAREN:
                return result.failure(InvalidSyntaxError(self.current_token.position_start,
                                                         self.current_token.position_end, f"Expected "
                                                                                          f"identifier or ')'"))

        result.register_advancement()
        self.advance()

        if self.current_token.type != Tokens.COLON:
            return result.failure(
                InvalidSyntaxError(self.current_token.position_start, self.current_token.position_end, f"Expected ':'"))

        result.register_advancement()
        self.advance()
        node_to_return = result.register(self.parse_boolean_expression())
        if result.error:
            return result

        return result.success(LambdaNode(arg_name_toks, var_name_tok, node_to_return))

    # Parse multiple statements, handling newlines and grouping them together
    def statements(self):
        result = ParseResult()
        statements = []
        while self.current_token.type == Tokens.NEWLINE:
            result.register_advancement()
            self.advance()
        statement = result.register(self.statement())
        if result.error:
            return result
        statements.append(statement)
        while self.current_token.type == Tokens.NEWLINE:
            result.register_advancement()
            self.advance()
            while self.current_token.type == Tokens.NEWLINE:
                result.register_advancement()
                self.advance()
            if self.current_token.type == Tokens.RIGHT_BRACE:
                break
            statement = result.register(self.statement())
            if result.error:
                return result
            statements.append(statement)

        while self.current_token.type == Tokens.NEWLINE:
            result.register_advancement()
            self.advance()
        return result.success(statements)

    # Parse a single statement, which could be a continue, break, return, or an expression
    def statement(self):
        if self.current_token.matches(Tokens.KEYWORD, Tokens.CONTINUE):
            return self.continue_statement()
        elif self.current_token.matches(Tokens.KEYWORD, Tokens.BREAK):
            return self.break_statement()
        elif self.current_token.matches(Tokens.KEYWORD, Tokens.RETURN):
            return self.return_statement()
        else:
            return self.parse_boolean_expression()

    # Parse a 'continue' statement, only valid within a loop
    def continue_statement(self):
        result = ParseResult()
        token = self.current_token
        if token.matches(Tokens.KEYWORD, Tokens.CONTINUE):
            result.register_advancement()
            self.advance()
            if self.tempLoop:
                return result.success(ContinueNode(token.position_start, token.position_end))
            else:
                return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                         "Continue outside of loop"))
        else:
            return result.failure(InvalidSyntaxError(token.position_start, token.position_end, "Expected 'continue'"))

    # Parse a 'break' statement, only valid within a loop
    def break_statement(self):
        result = ParseResult()
        token = self.current_token
        if token.matches(Tokens.KEYWORD, Tokens.BREAK):
            result.register_advancement()
            self.advance()
            if self.tempLoop:
                return result.success(BreakNode(token.position_start, token.position_end))
            else:
                return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                         "Break outside of loop"))
        else:
            return result.failure(InvalidSyntaxError(token.position_start, token.position_end, "Expected 'break'"))

    # Parse a 'return' statement, only valid within a function
    def return_statement(self):
        result = ParseResult()
        token = self.current_token
        if token.matches(Tokens.KEYWORD, Tokens.RETURN):
            result.register_advancement()
            self.advance()
            if self.current_token.type == Tokens.NEWLINE:
                if self.tempFunc:
                    return result.success(ReturnNode(None, token.position_start, token.position_end))
                else:
                    return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                             "Return outside of function"))
            else:
                body = result.register(self.parse_boolean_expression())
                if result.error:
                    return result
                if self.tempFunc:
                    return result.success(ReturnNode(body, token.position_start, token.position_end))
                else:
                    return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                             "Return outside of function"))
        else:
            return result.failure(InvalidSyntaxError(token.position_start, token.position_end,
                                                     "Expected 'return'"))


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    # Register the result of a parsing operation
    def register(self, result):
        self.advance_count += result.advance_count
        if result.error:
            self.error = result.error
        return result.node

    # Track the advancement of a single token
    def register_advancement(self):
        self.advance_count += 1
        return self

    # Mark the parse as successful and store the resulting node
    def success(self, node):
        self.node = node
        return self

    # Mark the parse as failed and store the error
    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self
