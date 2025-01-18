from .str_with_arrows import string_with_arrows


class BaseError:
    def __init__(self, start, end, name, details):
        self.name = name
        self.details = details
        self.start = start
        self.end = end

    def as_str(self):
        return f"\n{self.name}: {self.details}\nFile: {self.start.fn}\nLine: {self.start.line + 1}\n\n {string_with_arrows(self.start.fcnt, self.start, self.end)}"


class InvalidCharError(BaseError):
    def __init__(self, start, end, details):
        super().__init__(start, end, "Invalid Character", f'"{details}"')


class InvalidSyntaxError(BaseError):
    def __init__(self, start, end, details):
        super().__init__(start, end, "Invalid Syntax", f'"{details}"')
        
class RunTimeError(BaseError):
    def __init__(self, start, end, details, context):
        super().__init__(start, end, "Runtime error occured", f'{details}')
        self.context = context
    def generate_traceback(self):
        res = ''
        pos = self.start
        ctx = self.context
        
        while ctx:
            res = f'   File "{pos.fn}",  line {pos.line + 1}, in {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return '\nTraceback (most recent call last):\n' + res
    def as_str(self):
        return self.generate_traceback() + f"\n{self.name}: {self.details}\n\n{string_with_arrows(self.start.fcnt, self.start, self.end)}"

class ExpectedCharError(BaseError):
    def __init__(self, start, end, details):
        super().__init__(start, end, "Expected ", f'{details}')

class typeError(BaseError):
    def __init__(self, start, end, details):
        super().__init__(start, end, "Type Error ", f'{details}')