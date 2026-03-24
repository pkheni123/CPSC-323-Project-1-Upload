from LoxCallable import LoxCallable
from Environment import Environment
from Return import LoxReturn

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturn as return_value:
            return return_value.value
        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
