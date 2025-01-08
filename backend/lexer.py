from . import tokens
from .token import Token
from string import digits, ascii_letters
from .errs import *
from .pos import Position


LETTERSDIGITS = digits + ascii_letters


class Lexer:
    def __init__(self, fn, code):
        self.code = code
        self.fn = fn
        self.pos = Position(-1, 0, -1, fn, self.code)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.code[self.pos.index] if self.pos.index < len(self.code) else None
        )

    def back(self):
        self.pos.back(self.current_char)
        self.current_char = (
            self.code[self.pos.index] if self.pos.index < len(self.code) else None
        )

    def bake_tokens(self):
        toks = []
        while self.current_char != None:
            if self.current_char == " ":
                self.advance()
            elif self.current_char in ascii_letters:
                toks.append(self.make_identifier())
                self.advance()
            elif self.current_char == "*":
                toks.append(self.make_mul_power_eq())
                self.advance()
            elif self.current_char == "+":
                toks.append(self.make_plus_eq())
                self.advance()
            elif self.current_char == "-":
                toks.append(self.make_minus_eq())
                self.advance()
            elif self.current_char == "/":
                toks.append(self.make_div_eq())
                self.advance()
            elif self.current_char == ")":
                toks.append(Token(tokens.TT_RPAREN, start=self.pos))
                self.advance()
            elif self.current_char == "(":
                toks.append(Token(tokens.TT_LPAREN, start=self.pos))
                self.advance()
            elif self.current_char == "^":
                toks.append(Token(tokens.TT_POW, start=self.pos))
                self.advance()
            elif self.current_char == "=":
                toks.append(self.make_eq())
                self.advance()
            elif self.current_char == ":":
                toks.append(Token(tokens.TT_COLON, start=self.pos))
                self.advance()
            elif self.current_char == "!":
                tok, err = self.make_not_eq()
                if err:
                    return None, err
                toks.append(tok)
                self.advance()
            elif self.current_char == "<":
                toks.append(self.make_less_than())
                self.advance()
            elif self.current_char == ">":
                toks.append(self.make_greater_than())
                self.advance()
            elif self.current_char == "&":
                toks.append(Token(tokens.TT_AMPR, start=self.pos))
                self.advance()
            elif self.current_char == "|":
                toks.append(Token(tokens.TT_LINE, start=self.pos))
                self.advance()
            elif self.current_char == "{":
                toks.append(Token(tokens.TT_LCRLBRCKT, start=self.pos))
                self.advance()
            elif self.current_char == "}":
                toks.append(Token(tokens.TT_RCRLBRCKT, start=self.pos))
                self.advance()
            elif self.current_char == "[":
                toks.append(Token(tokens.TT_LSQRBRCKT, start=self.pos))
                self.advance()
            elif self.current_char == "]":
                toks.append(Token(tokens.TT_RSQRBRCKT, start=self.pos))
                self.advance()
            elif self.current_char == ";":
                toks.append(Token(tokens.TT_SEMICOLON, start=self.pos))
                self.advance()
            elif self.current_char == '"':
                toks.append(self.bake_string())
                self.advance()
            elif self.current_char == ",":
                toks.append(Token(tokens.TT_COMMA, start=self.pos))
                self.advance()
            elif self.current_char in digits:
                toks.append(self.bake_number())
            else:
                invalid_char = self.current_char
                start_pos = self.pos.get_pos()
                self.advance()
                return [], InvalidCharError(start_pos, self.pos.get_pos(), invalid_char)
        toks.append(Token(tokens.TT_EOF, start=self.pos))
        return toks, None

    def bake_number(self):
        number_as_str = ""
        dot: bool = False
        start_pos = self.pos.get_pos()

        while self.current_char != None and self.current_char in digits + ".":
            if self.current_char == ".":
                if dot:
                    break
                dot = True
                number_as_str += "."

            else:
                number_as_str += self.current_char

            self.advance()

        if dot:
            return Token(
                tokens.TT_DOUBLE,
                start_pos,
                self.pos.get_pos(),
                "double",
                float(number_as_str),
            )
        else:
            return Token(
                tokens.TT_INT, start_pos, self.pos.get_pos(), "int", int(number_as_str)
            )

    def make_identifier(self):
        as_str = ""
        pos_start = self.pos.get_pos()

        while self.current_char != None and self.current_char in LETTERSDIGITS + "_":
            as_str += self.current_char
            self.advance()
        pos_end = self.pos.get_pos()
        self.back()
        tok_type = (
            tokens.TT_KEYWORD
            if as_str in tokens.DATA_TYPES or as_str in tokens.KEYWORDS
            else tokens.TT_IDENTIFIER
        )
        data_type = None
        match as_str:
            case "string":
                data_type = "string"
            case "int":
                data_type = "int"
            case "double":
                data_type = "double"
        return Token(tok_type, pos_start, pos_end, data_type, as_str)

    def make_not_eq(self):
        pos_start = self.pos.get_pos()
        self.advance()

        if self.current_char == "=":
            self.advance()
            end_pos = self.pos.get_pos()
            return (Token(tokens.TT_NE, start=pos_start, end=end_pos), None)

        else:
            end_pos = self.pos.get_pos()
            self.back()
        return None, ExpectedCharError(pos_start, end_pos, "'=' after '!'")

    def make_eq(self):
        tok_type = tokens.TT_EQ

        pos_start = self.pos.get_pos()
        self.advance()

        if self.current_char == "=":

            tok_type = tokens.TT_DEQ

            end_pos = self.pos.get_pos()
        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, start=pos_start, end=end_pos)

    def make_less_than(self):
        tok_type = tokens.TT_LT

        pos_start = self.pos.get_pos()
        self.advance()

        if self.current_char == "=":

            tok_type = tokens.TT_LTE

            end_pos = self.pos.get_pos()

        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, start=pos_start, end=end_pos)

    def make_greater_than(self):
        tok_type = tokens.TT_GT
        pos_start = self.pos.get_pos()
        self.advance()

        if self.current_char == "=":

            tok_type = tokens.TT_GTE

            end_pos = self.pos.get_pos()
        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, start=pos_start, end=end_pos)

    def make_plus_eq(self):
        tok_type = tokens.TT_PLUS

        pos_start = self.pos.get_pos()
        end_pos = None

        self.advance()

        if self.current_char == "=":
            tok_type = tokens.TT_PLUSEQ

        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, pos_start, end_pos)

    def make_minus_eq(self):
        tok_type = tokens.TT_MINUS
        pos_start = self.pos.get_pos()
        self.advance()

        if self.current_char == "=":
            tok_type = tokens.TT_MINUSEQ
            end_pos = self.pos.get_pos()
        elif self.current_char == ">":
            tok_type = tokens.TT_ARROW
            end_pos = self.pos.get_pos()
        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, pos_start, end_pos)

    def make_mul_power_eq(self):
        tok_type = tokens.TT_MUL

        pos_start = self.pos.get_pos()

        self.advance()

        if self.current_char == "=":
            tok_type = tokens.TT_MULEQ

            end_pos = self.pos.get_pos()
        elif self.current_char == "*":
            tok_type = tokens.TT_POW

            end_pos = self.pos.get_pos()
        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, pos_start, end_pos)

    def make_div_eq(self):
        tok_type = tokens.TT_DIV
        tok_value = "/"
        pos_start = self.pos.get_pos()

        self.advance()

        if self.current_char == "=":
            tok_type = tokens.TT_DIVEQ
            tok_value = "/="
            end_pos = self.pos.get_pos()
        else:
            end_pos = self.pos.get_pos()
            self.back()
        return Token(tok_type, start = pos_start, end = end_pos, value=tok_value)

    def bake_string(self):
        string = ""
        pos_start = self.pos.get_pos()
        escape_character = False
        self.advance()

        escape_characters = {"n": "\n", "t": "\t", "a" : "\a"}

        while self.current_char != None and (
            self.current_char != '"' or escape_character
        ):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == "\\":
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()

        
        return Token(tokens.TT_STRING, pos_start, self.pos, "string", string)
