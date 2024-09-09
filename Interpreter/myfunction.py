import os

from Interpreter.context import Context
from error import RunTimeError
from Interpreter.number import Number
from Interpreter.mytype import Type


class RegularFunction(Type):
    def __init__(self, value, arg_names, body_node, position_start=None, position_end=None, context=None):
        super().__init__(value, position_start, position_end, context)
        self.name = value or "<anonymous>"
        self.arg_names = arg_names
        self.body_node = body_node

    # Generate a new context for the function execution
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.position_start)
        return new_context

    # Check if the number of arguments passed matches the expected number of arguments
    def check_args(self, arg_names, args):
        from Interpreter.interpreter import RunTimeResult
        result = RunTimeResult()
        if len(args) > len(arg_names):
            return result.failure(RunTimeError(self.position_start, self.position_end, f"{len(args) - len(arg_names)} "f"too "f"many arguments passed into "f"'{self.name}'", self.context))
        if len(args) < len(arg_names):
            return result.failure(RunTimeError(self.position_start,
                                               self.position_end, f"{len(arg_names) - len(args)} "f"too few arguments passed into "f"'{self.name}'", self.context))
        return result.success(None)

    # Populate the arguments in the function's execution context
    @staticmethod
    def populate_args(args_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = args_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx).set_position(arg_value.position_start, arg_value.position_end)
            exec_ctx.symbol_table.add(arg_name, arg_value)

    # Check arguments and populate them in the context if valid
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        from Interpreter.interpreter import RunTimeResult
        result = RunTimeResult()
        result.register(self.check_args(arg_names, args))
        if result.error:
            return result
        self.populate_args(arg_names, args, exec_ctx)
        return result


class Function(RegularFunction):
    def __init__(self, value, arg_names, body_node, should_auto_return, position_start=None, position_end=None, context=None):
        super().__init__(value, position_start, position_end, context)
        self.name = value or "<anonymous>"
        self.arg_names = arg_names
        self.body_node = body_node
        self.should_auto_return = should_auto_return

    # Execute the function with the provided arguments
    def execute(self, args):
        from Interpreter.interpreter import Interpreter, RunTimeResult
        result = RunTimeResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        result.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if result.error:
            return result
        value = result.register(interpreter.visit(self.body_node, exec_ctx))
        if result.error:
            return result
        return result.success(value)

    def copy(self):
        copy = Function(self.name, self.arg_names, self.body_node, self.should_auto_return, self.position_start, self.position_end, self.context)
        copy.set_context(self.context)
        copy.set_position(self.position_start, self.position_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(RegularFunction):
    def __init__(self, value, arg_names=None, body_node=None, position_start=None, position_end=None, context=None):
        super().__init__(value, arg_names, body_node, position_start, position_end, context)
        self.name = value or "<anonymous>"

    # Execute the built-in function with the provided arguments
    def execute(self, args):
        from Interpreter.interpreter import RunTimeResult
        result = RunTimeResult()
        exec_ctx = self.generate_new_context()
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if result.error:
            return result
        return_value = result.register(method(exec_ctx))
        if result.error:
            return result
        return result.success(return_value)

    # Handle the case where the function is not defined
    def no_visit_method(self):
        from Interpreter.interpreter import RunTimeResult
        result = RunTimeResult()
        return result.failure(RunTimeError(self.position_start, self.position_end, f"'{self.name}' is not defined", self.context))

    def copy(self):
        copy = BuiltInFunction(self.name, self.arg_names, self.body_node, self.position_start, self.position_end, self.context)
        copy.set_position(self.position_start, self.position_end)
        return copy

    # Built-in print function: prints the value passed to it
    def execute_print(self, exec_ctx):
        from Interpreter.interpreter import RunTimeResult
        print(str(exec_ctx.symbol_table.get('value')))
        return RunTimeResult().success(Number.null)

    execute_print.arg_names = ['value']

    # Built-in clear function: clears the console screen
    def execute_clear(self):
        from Interpreter.interpreter import RunTimeResult
        os.system('cls' if os.name == 'nt' else 'clear')
        return RunTimeResult().success(Number.null)

    execute_clear.arg_names = []

    # Built-in input function: takes an integer input from the user
    def execute_input_int(self):
        from Interpreter.interpreter import RunTimeResult
        while True:
            txt = input()
            try:
                number = int(txt)
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        return RunTimeResult().success(Number(number))
    execute_input_int.arg_names = []

    @staticmethod
    def execute_is_number(exec_ctx):
        from Interpreter.interpreter import RunTimeResult
        is_number = isinstance(exec_ctx.symbol_table.get('value'), Number)
        return RunTimeResult().success(Number.true if is_number else Number.false)

    @staticmethod
    def execute_is_function(exec_ctx):
        from Interpreter.interpreter import RunTimeResult
        is_function = isinstance(exec_ctx.symbol_table.get('value'), RegularFunction)
        return RunTimeResult().success(Number.true if is_function else Number.false)

    def __repr__(self):
        return f"<built-in function {self.name}>"


BuiltInFunction.print = BuiltInFunction('print', ['value'])
BuiltInFunction.int = BuiltInFunction('input_int', [])
BuiltInFunction.clear = BuiltInFunction('clear', [])
BuiltInFunction.is_number = BuiltInFunction('is_number', ['value'])
BuiltInFunction.is_function = BuiltInFunction('is_function', ['value'])
