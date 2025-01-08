class Position:
    def __init__(self, index, line, column, fn, fcnt):
        self.index = index
        self.line = line
        self.column = column
        self.fn = fn
        self.fcnt = fcnt

    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == "\n":
            self.line += 1
            self.column = 0
        return self
    def back(self, current_char=None):
        self.index -= 1
        self.column -= 1

        if current_char == "\n":
            self.line -= 1
            self.column = 0
        return self

    def get_pos(self):
        return Position(self.index, self.line, self.column, self.fn, self.fcnt)
