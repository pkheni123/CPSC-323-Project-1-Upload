import sys

from Scanner import Scanner
from TokenType import TokenType
from Parser import Parser
from Interpreter import Interpreter
from RuntimeError import LoxRuntimeError

class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run_file(self, path):
        with open(path, 'r') as f:
            source = f.read()
        self.run(source)
        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            self.run(line)
            self.had_error = False

    def run(self, source):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens, self)
        statements = parser.parse()

        if self.had_error:
            return

        self.interpreter.interpret(statements)

    def error(self, line, message):
        self._report(line, "", message)

    def error_token(self, token, message):
        if token.type == TokenType.EOF:
            self._report(token.line, " at end", message)
        else:
            self._report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error):
        print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
        self.had_runtime_error = True

    def _report(self, line, where, message):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True


def main():
    lox = Lox()
    if len(sys.argv) > 2:
        print("Usage: python3 lox.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()


if __name__ == "__main__":
    main()
