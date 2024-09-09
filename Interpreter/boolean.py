from Lexer.mytoken import Tokens
from Interpreter.mytype import Type


class Boolean(Type):
    def __init__(self, value, position_start=None, position_end=None, context=None):
        super().__init__(value, position_start, position_end, context)

    def search_binary_operation(self, operation_token):
        return self.search_operation(operation_token, {
            Tokens.EQUAL: self.equal_to,
            Tokens.NOT_EQUAL: self.not_equal_to,
            Tokens.AND: self.and_to,
            Tokens.OR: self.or_to,
            Tokens.NOT: self.not_to,
        })

    def search_unary_operation(self, operation_token):
        return self.search_operation(operation_token, {
            Tokens.NOT: self.not_to,
        })

    def equal_to(self, other):
        if isinstance(other, Boolean):
            return Boolean(int(self.value == other.value)).set_context(self.context), None

    def not_equal_to(self, other):
        if isinstance(other, Boolean):
            return Boolean(int(self.value != other.value)).set_context(self.context), None

    def and_to(self, other):
        if isinstance(other, Boolean):
            return Boolean(int(self.value and other.value)).set_context(self.context), None

    def or_to(self, other):
        from number import Number
        if isinstance(other, Boolean):
            return Boolean(self.value or other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Boolean(self.value or other.value).set_context(self.context), None
        return None, "Invalid operand"

    def not_to(self):
        return Boolean(int(not self.value)).set_context(self.context), None

    def __repr__(self):
        return "True" if self.value else "False"
