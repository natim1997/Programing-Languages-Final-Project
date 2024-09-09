
from Interpreter.boolean import Boolean
from error import RunTimeError
from Lexer.mytoken import Tokens
from Interpreter.mytype import Type


class Number(Type):
    def __init__(self, value, position_start=None, position_end=None, context=None):
        super().__init__(value, position_start, position_end, context)

    def search_binary_operation(self, operation_token):
        return self.search_operation(operation_token, {
            Tokens.ADD: self.add_to,
            Tokens.SUB: self.sub_to,
            Tokens.MUL: self.mul_to,
            Tokens.DIV: self.div_to,
            Tokens.INTEGER_DIV: self.int_div_to,
            Tokens.MOD: self.mod_to,
            Tokens.EQUAL: self.equal_to,
            Tokens.NOT_EQUAL: self.not_equal_to,
            Tokens.LESS: self.less_than,
            Tokens.LESS_EQUAL: self.less_than_equal,
            Tokens.GREATER: self.greater_than,
            Tokens.GREATER_EQUAL: self.greater_than_equal,
        })

    def search_unary_operation(self, operation_token):
        return self.search_operation(operation_token, {
            Tokens.ADD: self.sign_to,
            Tokens.SUB: self.neg_to,
        })

    def add_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def sign_to(self):
        return Number(self.value).set_context(self.context), None

    def sub_to(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def neg_to(self):
        return Number(-self.value).set_context(self.context), None

    def mul_to(self, other):
        if isinstance(other, Boolean):
            other = Number(1 if other.value else 0)
        elif not isinstance(other, Number):
            return None, "Invalid operand"
        return Number(self.value * other.value).set_context(self.context), None

    def div_to(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.position_start, other.position_end, "Division by zero", self.context)
            return Number(self.value / other.value).set_context(self.context), None

    def int_div_to(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.position_start, other.position_end, "Division by zero", self.context)
            return Number(self.value // other.value).set_context(self.context), None

    def mod_to(self, other):
        if isinstance(other, Number):
            return Number(self.value % other.value).set_context(self.context), None

    def equal_to(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value == other.value)).set_context(self.context), None

    def not_equal_to(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value != other.value)).set_context(self.context), None

    def less_than(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value < other.value)).set_context(self.context), None

    def less_than_equal(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value <= other.value)).set_context(self.context), None

    def greater_than(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value > other.value)).set_context(self.context), None

    def greater_than_equal(self, other):
        if isinstance(other, Number):
            return Boolean(int(self.value >= other.value)).set_context(self.context), None

    def copy(self):
        return Number(self.value).set_context(self.context).set_position(self.position_start, self.position_end)

    def set_value(self, value):
        self.value = value
        return self

    def __repr__(self):
        return f"{self.value}"


Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)
