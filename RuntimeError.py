class LoxRuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token
