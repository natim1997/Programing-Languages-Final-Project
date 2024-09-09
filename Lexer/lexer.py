
from Lexer.mytoken import Token, Tokens
from error import IllegalCharError, Position


class Lexer:
    def __init__(self, file_name, text):
        self.text = text
        self.fn = file_name
        self.current_char = None
        self.position = Position(-1, 0, -1, self.fn, self.text)
        self.advance()

    # Move to the next character in the input text
    def advance(self):
        self.position.advance()
        if self.position.index < len(self.text):
            self.current_char = self.text[self.position.index]
        else:
            self.current_char = None

    # Move back to the previous character in the input text
    def comeback(self):
        self.position.comeback()
        if self.position.index < len(self.text):
            self.current_char = self.text[self.position.index]
        else:
            self.current_char = None

    # Tokenizes the input source code into a list of tokens
    def tokenize(self):
        # Tokenizes the input source code into a list of tokens
        tokens = []

        while self.current_char is not None:
            if self.current_char in Tokens.WHITESPACE:
                self.advance()
            elif self.current_char in ';\n':
                tokens.append(Token(Tokens.NEWLINE, position_start=self.position))
                self.advance()
            elif self.current_char in Tokens.LETTERS:
                token, error = self.identifier_keyword()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char in Tokens.DIGITS:
                tokens.append(self.identifier_number())
            elif self.current_char == '+':
                tokens.append(Token(Tokens.ADD, position_start=self.position))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.identifier_minus_or_arrow())
                # self.advance()
            elif self.current_char == '*':
                tokens.append(Token(Tokens.MUL, position_start=self.position))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(Tokens.MOD, position_start=self.position))
                self.advance()
            elif self.current_char == '/':
                tokens.append(self.identifier_div())
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.identifier_equal(Tokens.EQUAL, Tokens.ASSIGN))
                self.advance()
            elif self.current_char == '!':
                tokens.append(self.identifier_equal(Tokens.NOT_EQUAL, Tokens.NOT))
                self.advance()
            elif self.current_char == '<':
                tokens.append(self.identifier_equal(Tokens.LESS_EQUAL, Tokens.LESS))
                self.advance()
            elif self.current_char == '>':
                tokens.append(self.identifier_equal(Tokens.GREATER_EQUAL, Tokens.GREATER))
                self.advance()
            elif self.current_char == 'false' or self.current_char == 'true':
                token, error = self.identifier_boolean()
                if error:
                    return [], error
                tokens.append(token)
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(Tokens.LEFT_PAREN, position_start=self.position))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(Tokens.RIGHT_PAREN, position_start=self.position))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(Tokens.LEFT_BRACE, position_start=self.position))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(Tokens.RIGHT_BRACE, position_start=self.position))
                self.advance()
            elif self.current_char == '|':
                token, error = self.identifier_or()
                if error:
                    return [], error
                tokens.append(token)
                self.advance()
            elif self.current_char == '&':
                token, error = self.identifier_and()
                if error:
                    return [], error
                tokens.append(token)
                self.advance()
            elif self.current_char == '#':
                self.skip_comment()

            elif self.current_char == ',':
                tokens.append(Token(Tokens.COMMA, position_start=self.position))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(Tokens.COLON, position_start=self.position))
                self.advance()
            else:
                # Raise an exception for any illegal character
                position_start = self.position.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(position_start, self.position, "'" + char + "'")
        tokens.append(Token(Tokens.EOF, position_start=self.position))
        return tokens, None

    # Create a token representing a number
    def identifier_number(self):
        # Creates a token representing a number
        number_str = ''
        position_start = self.position.copy()
        while self.current_char is not None and self.current_char in Tokens.DIGITS:
            number_str += self.current_char
            self.advance()
        return Token(Tokens.INT, int(number_str), position_start=position_start, position_end=self.position)

    # Create a token representing a boolean value (true/false)
    def identifier_boolean(self):
        position_start = self.position.copy()
        string_boolean = ''

        if self.current_char == 'true':
            for i in range(4):
                string_boolean += self.current_char
                self.advance()
                if self.current_char not in Tokens.TRUE or self.current_char is None:
                    break
            if string_boolean == 'true':
                self.comeback()
                return Token(Tokens.BOOL, True, position_start=position_start, position_end=self.position), None

        elif self.current_char == 'false':
            for i in range(5):
                string_boolean += self.current_char
                self.advance()
                if self.current_char not in Tokens.FALSE or self.current_char is None:
                    break
            if string_boolean == 'false':
                self.comeback()
                return Token(Tokens.BOOL, False, position_start=position_start, position_end=self.position), None
        return None, IllegalCharError(position_start, self.position, "Invalid boolean")

    def identifier_or(self):
        position_start = self.position.copy()
        self.advance()

        if self.current_char == '|':
            return Token(Tokens.OR, position_start=position_start), None
        return None, IllegalCharError(position_start, self.position, "Invalid |")

    def identifier_equal(self, token_type, token_type2):
        position_start = self.position.copy()
        self.advance()
        if self.current_char == '=':
            return Token(token_type, position_start=position_start)
        self.comeback()
        return Token(token_type2, position_start=position_start)

    def identifier_div(self):
        position_start = self.position.copy()
        self.advance()

        if self.current_char == '/':
            return Token(Tokens.INTEGER_DIV, position_start=position_start, position_end=self.position)
        self.comeback()
        return Token(Tokens.DIV, position_start=position_start)

    def identifier_and(self):
        position_start = self.position.copy()
        self.advance()

        if self.current_char == '&':
            return Token(Tokens.AND, position_start=position_start), None
        return None, IllegalCharError(position_start, self.position, "Invalid &")

    # Handle keywords and identifiers
    def identifier_keyword(self):
        position_start = self.position.copy()
        id_str = ''
        while self.current_char is not None and self.current_char in Tokens.LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()
        id_str = id_str.lower()
        if id_str == 'function':
            return Token(Tokens.FUNCTION, position_start=position_start), None
        if id_str in Tokens.KEYWORDS:
            return Token(Tokens.KEYWORD, id_str, position_start=position_start, position_end=self.position), None
        elif id_str in Tokens.BOOL:
            if id_str == 'true':
                return Token(Tokens.BOOL, True, position_start=position_start, position_end=self.position), None
            elif id_str == 'false':
                return Token(Tokens.BOOL, False, position_start=position_start, position_end=self.position), None
        elif id_str in Tokens.IDENTIFIER:
            return Token(Tokens.IDENTIFIER, id_str, position_start=position_start, position_end=self.position), None
        return Token(Tokens.IDENTIFIER, id_str, position_start=position_start, position_end=self.position), None

    # Handle '-' (subtraction) or '->' (arrow) token
    def identifier_minus_or_arrow(self):
        token_type = Tokens.SUB
        position_start = self.position.copy()
        self.advance()
        if self.current_char == '>':
            self.advance()
            token_type = Tokens.ARROW
        return Token(token_type, position_start=position_start, position_end=self.position)

    def skip_comment(self):
        self.advance()
        while self.current_char != '\n':
            self.advance()
        self.advance()