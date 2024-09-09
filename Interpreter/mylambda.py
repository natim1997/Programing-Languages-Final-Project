from Interpreter.context import Context
from error import RunTimeError
from Interpreter.mytype import Type
from Interpreter.symboltable import SymbolTable


class Lambda(Type):
    def __init__(self, value, arg_names, body_node, position_start=None, position_end=None, context=None):
        super().__init__(value, position_start, position_end, context)
        self.name = value or "<anonymous>"
        self.arg_names = arg_names
        self.body_node = body_node

    # Execute the lambda function with the given arguments
    def execute(self, args):
        from Interpreter.interpreter import Interpreter
        from Interpreter.interpreter import RunTimeResult
        result = RunTimeResult()
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.position_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        if len(args) > len(self.arg_names):
            return result.failure(RunTimeError(self.position_start, self.position_end,
                                               f"{len(args) - len(self.arg_names)} "
                                               f"too many arguments passed into '{self.name}'", self.context))
        if len(args) < len(self.arg_names):
            return result.failure(RunTimeError(self.position_start, self.position_end,
                                               f"{len(self.arg_names) - len(args)} "
                                               f"too few arguments passed into '{self.name}'", self.context))
        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.add(arg_name, arg_value)
        value = result.register(interpreter.visit(self.body_node, new_context))
        if result.error:
            return result
        return result.success(value)

    # Create a copy of the lambda function, preserving its state
    def copy(self):
        copy = Lambda(self.name, self.arg_names, self.body_node)
        copy.set_position(self.position_start, self.position_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f"<lambda {self.name}>"
