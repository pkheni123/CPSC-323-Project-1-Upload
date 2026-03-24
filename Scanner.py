from TokenType import TokenType
from Token import Token

KEYWORDS = {
    'and':    TokenType.AND,
    'class':  TokenType.CLASS,
    'else':   TokenType.ELSE,
    'false':  TokenType.FALSE,
    'for':    TokenType.FOR,
    'fun':    TokenType.FUN,
    'if':     TokenType.IF,
    'nil':    TokenType.NIL,
    'or':     TokenType.OR,
    'print':  TokenType.PRINT,
    'return': TokenType.RETURN,
    'super':  TokenType.SUPER,
    'this':   TokenType.THIS,
    'true':   TokenType.TRUE,
    'var':    TokenType.VAR,
    'while':  TokenType.WHILE,
}

class Scanner:
    def __init__(self, source, lox):
        self.source = source
        self.lox = lox
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self):
        c = self._advance()
        if c == '(':   self._add_token(TokenType.LEFT_PAREN)
        elif c == ')': self._add_token(TokenType.RIGHT_PAREN)
        elif c == '{': self._add_token(TokenType.LEFT_BRACE)
        elif c == '}': self._add_token(TokenType.RIGHT_BRACE)
        elif c == ',': self._add_token(TokenType.COMMA)
        elif c == '.': self._add_token(TokenType.DOT)
        elif c == '-': self._add_token(TokenType.MINUS)
        elif c == '+': self._add_token(TokenType.PLUS)
        elif c == ';': self._add_token(TokenType.SEMICOLON)
        elif c == '*': self._add_token(TokenType.STAR)
        elif c == '!':
            self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
        elif c == '=':
            self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
        elif c == '<':
            self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
        elif c == '>':
            self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
        elif c == '/':
            if self._match('/'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        elif c in (' ', '\r', '\t'):
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif self._is_alpha(c):
            self._identifier()
        else:
            self.lox.error(self.line, "Unexpected character.")

    def _identifier(self):
        while self._is_alpha_numeric(self._peek()):
            self._advance()
        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        self._add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()
        if self._is_at_end():
            self.lox.error(self.line, "Unterminated string.")
            return
        self._advance()  # closing "
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _match(self, expected):
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _is_alpha(self, c):
        return c.isalpha() or c == '_'

    def _is_alpha_numeric(self, c):
        return self._is_alpha(c) or c.isdigit()

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def _add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
