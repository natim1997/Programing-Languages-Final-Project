from Lexer.mytoken import Tokens


# Represents a number in the AST
class NumberNode:
    def __init__(self, token_value):
        self.token_value = token_value
        self.position_start = self.token_value.position_start
        self.position_end = self.token_value.position_end

    def __repr__(self):
        return f"NumberNode({self.token_value})"


# Represents a boolean value in the AST
class BooleanNode:
    def __init__(self, value):
        self.value = value
        self.position_start = self.value.position_start
        self.position_end = self.value.position_end

    def __repr__(self):
        return f"BooleanNode({self.value})"


# Represents a unary operation (e.g., NOT) in the AST
class UnaryOperationNode:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
        self.position_start = self.operator.position_start
        self.position_end = self.operand.position_end

    def __repr__(self):
        return f"UnaryOperationNode('{self.operator}', {self.operand})"


# Represents a binary operation (e.g., addition, multiplication) in the AST
class BinaryOperationNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

        self.position_start = self.left.position_start
        self.position_end = self.right.position_end if hasattr(self.right, 'position_end') else self.left.position_end

    def __repr__(self):
        return f"BinaryOperationNode({self.left}, '{self.operator}', {self.right})"


# Represents a while loop in the AST
class WhileNode:
    def __init__(self, condition, body, position_end=None):
        self.condition = condition
        self.body = body
        self.position_start = self.condition.position_start

        if len(self.body) > 0:
            self.position_end = self.body[len(self.body)-1].position_end
        else:
            self.position_end = self.condition.position_end
        if position_end:
            self.position_end = position_end

    def __repr__(self):
        return f'while ({self.condition}) {Tokens.LEFT_BRACE} {self.body} {Tokens.RIGHT_BRACE}'


# Represents a function definition in the AST
class FunctionDefinitionNode:
    def __init__(self, token_name, arg_name, body, should_auto_return):
        self.token_name = token_name
        self.arg_name = arg_name
        self.body = body
        self.should_auto_return = should_auto_return
        if self.token_name:
            self.position_start = self.token_name.position_start
        elif len(self.arg_name) > 0:
            self.position_start = self.arg_name[0].position_start
        else:
            self.position_start = self.body.position_start
        self.position_end = self.body.position_end


# Represents a function call in the AST
class FunctionCallNode:
    def __init__(self, node_call, arg_node):
        self.node_call = node_call
        self.arg_node = arg_node
        self.position_start = self.node_call.position_start
        if len(self.arg_node) > 0:
            self.position_end = self.arg_node[len(self.arg_node)-1].position_end
        else:
            self.position_end = self.node_call.position_end


# Represents accessing a variable in the AST
class AccessNode:
    def __init__(self, token_name):
        self.token_name = token_name
        self.name = token_name.value
        self.position_start = token_name.position_start
        self.position_end = token_name.position_end

    def __repr__(self):
        return f'{self.token_name}'


# Represents a lambda function in the AST
class LambdaNode:
    def __init__(self, arg_name_toks, var_name_tok, body_node):
        self.arg_name_toks = arg_name_toks
        self.var_name_tok = var_name_tok
        self.body_node = body_node

        if self.var_name_tok:
            self.position_start = self.var_name_tok.position_start
        elif len(self.arg_name_toks) > 0:
            self.position_start = self.arg_name_toks[0].position_start
        else:
            self.position_start = self.body_node.position_start

        self.position_end = self.body_node.position_end


# Represents a continue statement in the AST (used in loops)
class ContinueNode:
    def __init__(self):
        self.position_start = None
        self.position_end = None

    def __repr__(self):
        return f'continue '


# Represents a break statement in the AST (used in loops)
class BreakNode:
    def __init__(self):
        self.position_start = None
        self.position_end = None

    def __repr__(self):
        return f'break '


# Represents a return statement in the AST (used in functions)
class ReturnNode:
    def __init__(self, node_to_return):
        self.node_to_return = node_to_return
        self.position_start = node_to_return.position_start
        self.position_end = node_to_return.position_end

    def __repr__(self):
        return f'return {self.node_to_return}'
