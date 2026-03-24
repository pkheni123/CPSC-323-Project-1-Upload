import time

from TokenType import TokenType
from RuntimeError import LoxRuntimeError
from Environment import Environment
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from Return import LoxReturn
import Expr
import Stmt

class Interpreter:
    def __init__(self, lox):
        self.lox = lox
        self.globals = Environment()
        self.environment = self.globals

        # Native: clock()
        class _Clock(LoxCallable):
            def arity(self): return 0
            def call(self, interpreter, arguments): return time.time()
            def __str__(self): return "<native fn>"

        self.globals.define("clock", _Clock())

    def interpret(self, statements):
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as error:
            self.lox.runtime_error(error)

    # --- Expression visitors ---

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self._evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -right
        if expr.operator.type == TokenType.BANG:
            return not self._is_truthy(right)
        return None

    def visit_binary_expr(self, expr):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        op = expr.operator.type

        if op == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LoxRuntimeError(expr.operator,
                "Operands must be two numbers or two strings.")
        if op == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return left - right
        if op == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return left * right
        if op == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return left / right
        if op == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return left > right
        if op == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return left >= right
        if op == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return left < right
        if op == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return left <= right
        if op == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        if op == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        return None

    def visit_logical_expr(self, expr):
        left = self._evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left
        return self._evaluate(expr.right)

    def visit_variable_expr(self, expr):
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr):
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr):
        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    # --- Statement visitors ---

    def visit_expression_stmt(self, stmt):
        self._evaluate(stmt.expression)

    def visit_print_stmt(self, stmt):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if_stmt(self, stmt):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    def visit_while_stmt(self, stmt):
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        raise LoxReturn(value)

    # --- Helpers ---

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous

    def _execute(self, stmt):
        stmt.accept(self)

    def _evaluate(self, expr):
        return expr.accept(self)

    def _is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def _is_equal(self, a, b):
        return a == b

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def _stringify(self, obj):
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)
