from Interpreter.boolean import Boolean
from Interpreter.context import Context
from error import RunTimeError
from Interpreter.myfunction import Function
from Interpreter.mylambda import Lambda
from Lexer.mytoken import Tokens
from Interpreter.number import Number


class Interpreter:
    # Dynamically find and call the appropriate visit method for the given node
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.no_generic_visit)
        return visitor(node, context)

    # Handle cases where a visit method is not defined for the node type
    @staticmethod
    def no_generic_visit(node, context):
        result = RunTimeResult()
        return result.failure(RunTimeError(node.position_start, node.position_end,
                                           f"No visit_{type(node).__name__}"f" method defined", context))

    # Visit a number node and return its value
    @staticmethod
    def visit_NumberNode(node, context):
        result = RunTimeResult()
        return result.success(Number(node.token_value.value).set_position(node.position_start,
                                                                          node.position_end).set_context(context))

    # Visit a boolean node and return its value
    @staticmethod
    def visit_BooleanNode(node, context):
        result = RunTimeResult()
        return result.success(Boolean(node.value).set_position(node.position_start, node.position_end)
                              .set_context(context))

    # Visit a while loop node and execute its body while the condition is true
    def visit_WhileNode(self, node, context):
        result = RunTimeResult()
        while True:
            condition = result.register(self.visit(node.condition, context))
            if result.error:
                return None, result.error
            if not condition.value:
                break
            continue_loop = False
            for i in node.body:
                value = result.register(self.visit(i, context))
                if result.error:
                    return result
                if result.should_return():
                    return result
                elif result.loop_should_continue:
                    continue_loop = False
                    break
                elif result.loop_should_break:
                    return result.success(None)
        return result.success(None)

    # Visit a binary operation node and execute the operation on its operands
    def visit_BinaryOperationNode(self, node, context):
        result = RunTimeResult()
        left = result.register(self.visit(node.left, context))
        if result.error:
            return result
        if result.should_return():
            return result
        if node.operator.type == Tokens.AND:
            if left.value == 0:
                return result.success(left)
        elif node.operator.type == Tokens.OR:
            if left.value == 1:
                return result.success(left)

        right = result.register(self.visit(node.right, context))
        if result.error:
            return result
        obj, error = left.binary_opr(node.operator, right)
        if error:
            return result.failure(error)
        else:
            return result.success(obj.set_position(node.position_start, node.position_end))

    # Visit a unary operation node and execute the operation on its operand
    def visit_UnaryOperationNode(self, node, context):
        result = RunTimeResult()
        obj = result.register(self.visit(node.operand, context))
        if result.error:
            return result
        if result.should_return():
            return result
        handler, error = obj.unary_opr(node.operator)
        if error:
            return result.failure(error)
        obj, error = handler(obj)
        if error:
            return result.failure(error)
        else:
            return result.success(obj.set_position(node.position_start, node.position_end))

    # Visit a node that accesses a variable and return its value from the symbol table
    @staticmethod
    def visit_AccessNode(node, context):
        result = RunTimeResult()
        name_ = node.token_name.value
        value = context.symbol_table.get(name_)
        if value is None:
            return result.failure(RunTimeError(node.position_start, node.position_end,
                                               f"'{node.token_name.value}' is not defined", context))
        value = value.copy().set_position(node.position_start, node.position_end).set_context(context)
        return result.success(value)

    # Visit a function definition node and create a function object
    @staticmethod
    def visit_FunctionDefinitionNode(node, context):
        result = RunTimeResult()
        function_name = node.token_name.value if node.token_name else None
        body_node = node.body
        arg_names = [arg_name.value for arg_name in node.arg_name]
        function_value = Function(function_name, arg_names, body_node, node.should_auto_return).set_context(context).set_position(node.position_start, node.position_end)

        if node.token_name:
            context.symbol_table.add(function_name, function_value)
        return result.success(function_value)

    # Visit a function call node, execute the function, and return the result
    def visit_FunctionCallNode(self, node, context):
        result = RunTimeResult()
        args = []
        value_call = result.register(self.visit(node.node_call, context))
        if result.error:
            return result
        value_call = value_call.copy().set_position(node.position_start, node.position_end)
        new_context = Context(value_call.name, value_call.context, value_call.position_start)
        value_call.set_context(new_context)
        for arg_node in node.arg_node:
            args.append(result.register(self.visit(arg_node, context)))
            if result.error:
                return result
        return_value = result.register(value_call.execute(args))
        if result.error:
            return result
        return result.success(return_value.set_position(node.position_start, node.position_end).set_context(context))

    # Visit a lambda function node and create a lambda object
    @staticmethod
    def visit_LambdaNode(node, context):
        result = RunTimeResult()
        lambda_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        lambda_value = Lambda(lambda_name, arg_names, body_node).set_context(context).set_position(node.position_start, node.position_end)
        if node.var_name_tok:
            context.symbol_table.add(lambda_name, lambda_value)

        return result.success(lambda_value)

    # Visit a continue node, signaling the loop to continue
    @staticmethod
    def visit_ContinueNode(node, context):
        result = RunTimeResult()
        return result.success_continue()

    # Visit a return node and return the value from the function
    def visit_ReturnNode(self, node, context):
        result = RunTimeResult()
        if node.node_to_return:
            value = result.register(self.visit(node.node_to_return, context))
            if result.error:
                return result
        else:
            value = Number.null

        return result.success_return(value)

    # Visit a break node, signaling the loop to break
    @staticmethod
    def visit_BreakNode(node, context):
        result = RunTimeResult()
        return result.success_break()


class RunTimeResult:
    def __init__(self):
        self.value = None
        self.error = None

    # Register a result from another operation
    def register(self, res):
        if res.error:
            self.error = res.error
        self.function_return_value = res.function_return_value
        self.function_should_return = res.function_should_return
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    # Reset the runtime result to its initial state
    def reset(self):
        self.value = None
        self.error = None
        self.function_return_value = None
        self.function_should_return = False
        self.loop_should_continue = False
        self.loop_should_break = False

    # Set a successful result
    def success(self, value):
        self.reset()
        self.value = value
        return self

    # Set a successful result
    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    # Indicate a loop should break
    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    # Set a successful return value from a function
    def success_return(self, value):
        self.reset()
        self.function_return_value = value
        self.function_should_return = True
        return self

    # Check if the function should return
    def should_return(self):
        return self.function_should_return

    # Set an error result
    def failure(self, error):
        self.reset()
        self.error = error
        return self
