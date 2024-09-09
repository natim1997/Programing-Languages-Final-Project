from stringcalc import string_calc


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.error_name = error_name
        self.details = details
        self.pos_start = pos_start
        self.pos_end = pos_end

    # Generate a string representation of the error including the file and line information
    def __str__(self):
        result = f"{self.error_name}: {self.details}"
        result += f"\nFile {self.pos_start.file_name}, line {self.pos_start.line + 1} col {self.pos_start.column}"
        result += "\n" + string_calc(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Unrecognized char', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, 'Invalid syntax', details)


class RunTimeError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime error', details)
        self.context = context

    # Generate a string representation of the runtime error, including a traceback
    def __str__(self):
        result = self.generate_traceback()
        result += f"{self.error_name}: {self.details}"
        result += f"\nFile {self.pos_start.file_name}, line {self.pos_start.line + 1} col {self.pos_start.column + 1}"
        return result

    # Generate a traceback of the error by following the context chain
    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        context = self.context

        while context:
            result = f"  File {pos.file_name}, line {str(pos.line + 1)}\n" + result
            pos = context.parent_entry_pos
            context = context.parent

        return "Traceback (most recent call last):\n" + result


class Position:
    def __init__(self, index, line, column, file_name, file_text):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text

    # Advance the position forward by one character, updating line and column numbers
    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)

    # Move the position backward by one character, updating column numbers
    def comeback(self, current_char=None):
        self.index -= 1
        self.column -= 1

        if current_char == '\n':
            # self.line -= 1
            # self.column = 0
            pass
        return self
