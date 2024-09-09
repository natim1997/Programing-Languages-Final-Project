from error import RunTimeError


class Type:
    def __init__(self, value, position_start=None, position_end=None, context=None):
        self.value = value
        self.position_start = position_start
        self.position_end = position_end
        self.context = context

    # Set the position of the value (used for error reporting and tracing)
    def set_position(self, position_start=None, position_end=None):
        self.position_start = position_start
        self.position_end = position_end
        return self

    # Set the context of the value (used to track where in the code the value originated)
    def set_context(self, context=None):
        self.context = context
        return self

    def __repr__(self):
        return f"{self}"

    # Perform a binary operation between self and another object
    def binary_opr(self, operation_token, other):
        if operation_token.type == '||':
            if self.value:
                return self, None
            else:
                return other, None
        handler, error = self.search_binary_operation(operation_token)
        if error:
            return None, error
        if handler is None:
            return None,  f"No handler found for operation '{operation_token}'"

        result = handler(other)
        if result is None:
            return None, f"Handler for '{operation_token}' returned None"
        obj, error = result
        if error:
            return None, error
        obj.set_context(self.context)
        obj.set_position(self.position_start, other.position_end)
        return obj, None

    # Perform a unary operation on self
    def unary_opr(self, operation_token):
        handler, error = self.search_unary_operation(operation_token)
        if error:
            return None, error
        obj, error = handler(self)
        if error:
            return None, error
        obj.set_context(self.context)
        return obj, None

    # Evaluate the current object (used for constant evaluation or simple values)
    def eval(self):
        return self, None

    # Search for a handler for the binary operation (to be implemented in subclasses)
    def search_binary_operation(self, operation_token):
        pass

    # Search for a handler for the unary operation (to be implemented in subclasses)
    def search_unary_operation(self, operation_token):
        pass

    # Search for the operation in the provided operations dictionary
    def search_operation(self, operation_token, operations):
        operation = operations.get(operation_token.type, None)
        if operation is None:
            return None, RunTimeError(operation_token.position_start, operation_token.position_end,
                                      f"Operation not supported", self.context)
        else:
            return operation, None

    def get(self):
        return self.value
