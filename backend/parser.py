from numpy import float64
from . import tokens as t
from . import nodes as n
from .errs import InvalidSyntaxError
from .nodes import BinOpNode


class ParseRes:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_loged_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def log_advancement(self):
        self.last_loged_advance_count = 1
        self.advance_count += 1

    def log(self, res):
        self.last_loged_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_log(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.log(res)

    def success(self, node):
        self.node = node
        return self

    def fail(self, error):
        if not self.error or self.last_loged_advance_count == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_tok()
        return self.current_tok

    def update_tok(self):
        if self.tok_idx < len(self.tokens) and self.tok_idx >= 0:
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if res.error and self.current_tok.type != t.TT_EOF:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "Expected '+', '-', '*' or '/'",
                )
            )
        return res

    ###################################

    def quark(self):
        res = ParseRes()
        tok = self.current_tok

        if tok.type in (t.TT_INT, t.TT_DOUBLE):
            res.log_advancement()
            self.advance()
            if isinstance(tok.value, int):

                return res.success(n.IntegerNode(tok))
            elif isinstance(tok.value, float64):
                return res.success(n.DoubleNode(tok))

        if tok.type in (t.TT_STRING):
            res.log_advancement()
            self.advance()

            return res.success(n.StringNode(tok))

        elif tok.type == t.TT_IDENTIFIER:
            res.log_advancement()
            self.advance()
            if self.current_tok.type == t.TT_EQ:
                res.log_advancement()
                self.advance()
                new_value = res.log(self.expr())
                if res.error:
                    return res
                op = "="
                return res.success(n.VarReAssignNode(tok, new_value, op))
            elif self.current_tok.type == t.TT_PLUSEQ:
                res.log_advancement()
                self.advance()
                new_value = res.log(self.expr())
                if res.error:
                    return res
                op = "+"
                return res.success(n.VarReAssignNode(tok, new_value, op))
            elif self.current_tok.type == t.TT_MINUSEQ:
                res.log_advancement()
                self.advance()
                new_value = res.log(self.expr())
                if res.error:
                    return res
                op = "-"
                return res.success(n.VarReAssignNode(tok, new_value, op))
            elif self.current_tok.type == t.TT_MULEQ:
                res.log_advancement()
                self.advance()
                new_value = res.log(self.expr())
                if res.error:
                    return res
                op = "*"
                return res.success(n.VarReAssignNode(tok, new_value, op))
            elif self.current_tok.type == t.TT_DIVEQ:
                res.log_advancement()
                self.advance()
                new_value = res.log(self.expr())
                if res.error:
                    return res
                op = "/"
                return res.success(n.VarReAssignNode(tok, new_value, op))
            return res.success(n.VarAccessNode(tok))

        elif tok.type == t.TT_LPAREN:
            res.log_advancement()
            self.advance()
            expr = res.log(self.expr())
            if res.error:
                return res
            if self.current_tok.type == t.TT_RPAREN:
                res.log_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected ')'"
                    )
                )
        elif tok.matches(t.TT_KEYWORD, "if"):
            if_expr = res.log(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(t.TT_KEYWORD, "for"):
            for_expr = res.log(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)
        elif tok.matches(t.TT_KEYWORD, "while"):
            while_expr = res.log(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)
        elif tok.matches(t.TT_KEYWORD, "func"):
            func_def_expr = res.log(self.func_def())
            if res.error:
                return res
            return res.success(func_def_expr)
        elif tok.type == t.TT_LSQRBRCKT:
            list_expr = res.log(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
        elif tok.type == t.TT_EOF:
            return res.success(None)
        return res.fail(
            InvalidSyntaxError(
                tok.start,
                tok.end,
                "Expected int, double, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'not' or 'func'",
            )
        )

    def power(self):
        return self.bin_op(self.CallFunc, (t.TT_POW,), self.factor)

    def factor(self):
        res = ParseRes()
        tok = self.current_tok

        if tok.type in (t.TT_PLUS, t.TT_MINUS):
            res.log_advancement()
            self.advance()
            factor = res.log(self.factor())
            if res.error:
                return res
            return res.success(n.UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (t.TT_MUL, t.TT_DIV))

    def expr(self):
        res = ParseRes()
        if self.current_tok.matches(t.TT_KEYWORD, "new"):
            is_const = False
            res.log_advancement()
            self.advance()

            if self.current_tok.matches(t.TT_KEYWORD, "const"):
                is_const = True
                res.log_advancement()
                self.advance()

            if (
                self.current_tok.type != t.TT_KEYWORD
                or self.current_tok.value not in t.DATA_TYPES
            ):
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        f"Expected keyword, but got {self.current_tok.value}",
                    )
                )
            var_type = self.current_tok
            res.log_advancement()
            self.advance()

            if self.current_tok.type == t.TT_IDENTIFIER:
                var_name = self.current_tok
                res.log_advancement()
                self.advance()
            else:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        "Expected identifier",
                    )
                )

            if self.current_tok.type != t.TT_EQ:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        f'Expected "=", but got {self.current_tok.value}',
                    )
                )
            res.log_advancement()
            self.advance()
            expr_ = res.log(self.expr())
            if res.error:
                return res

            return res.success(n.VarAssignNode(var_name, var_type, expr_, is_const))
        

        node = res.log(
            self.bin_op(
                self.comp_expr,
                (
                    (t.TT_KEYWORD, "and"),
                    (t.TT_KEYWORD, "or"),
                    (t.TT_AMPR, "&"),
                    (t.TT_LINE, "|"),
                ),
            )
        )
        if res.error:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "Expected 'new', 'if', 'for', 'while', 'func' int, double, identifier, '+', '-' '(', '[' or 'not'"
                )
            )
        return res.success(node)

    def comp_expr(self):
        res = ParseRes()

        if self.current_tok.matches(t.TT_KEYWORD, "not"):
            op_tok = self.current_tok
            res.log_advancement()
            self.advance()

            node = res.log(self.comp_expr())
            if res.error:
                return res
            return res.success(n.UnaryOpNode(op_tok, node))
        node = res.log(
            self.bin_op(
                self.arith_expr,
                (t.TT_DEQ, t.TT_LTE, t.TT_GTE, t.TT_LT, t.TT_GT, t.TT_NE),
            )
        )

        if res.error:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "Expected int, double, identifier, '+', '-', '(', '[' or 'not'",
                )
            )
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (t.TT_PLUS, t.TT_MINUS))

    def if_expr(self):
        res = ParseRes()
        all_cases = res.log(self.if_expr_cases('if'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(n.IfNode(cases, else_case))

    def if_expr_cases(self, keyword):
        res = ParseRes()
        cases = []
        else_case = None
        if not self.current_tok.matches(t.TT_KEYWORD, keyword):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, f"Expected {keyword}"
                )
            )
        res.log_advancement()
        self.advance()

        condition = res.log(self.statement())
        if res.error:
            return res

        if self.current_tok.type != t.TT_LCRLBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '{'"
                )
            )
        res.log_advancement()
        self.advance()
        
        if self.current_tok.type == t.TT_NEWL:
            

            statements = res.log(self.statements())
            
            if res.error:
                return res
            cases.append((condition, statements, True))
            
            if self.current_tok.type == t.TT_RCRLBRCKT:
                res.log_advancement()
                self.advance()
                while self.current_tok == t.TT_NEWL:
                    res.log_advancement()
                    self.advance()
                if self.current_tok.matches(t.TT_KEYWORD, 'else') or self.current_tok.matches(t.TT_KEYWORD, 'elif'):
                    all_cases = res.log(self.if_expr_b_or_c())
                    if res.error:
                        return res
                    new, else_case = all_cases
                    cases.extend(new)
            else:
                return res.fail(InvalidSyntaxError(self.current_tok.start, self.current_tok.end, "Expected '}'"))
        else:
            expr = res.log(self.expr())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.log(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
    
        return res.success((cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        res = ParseRes()
        else_case = None
        
        if self.current_tok.matches(t.TT_KEYWORD, "else"):
            res.log_advancement()
            self.advance()

            if self.current_tok.type == t.TT_LCRLBRCKT:
                res.log_advancement()
                self.advance()
            else:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, 'Expected "{"'
                    )
                )

            if self.current_tok.type == t.TT_NEWL:
                res.log_advancement()
                self.advance()
                
                statments = res.log(self.statements())
                if res.error:
                    return res
                else_case = (statments, True)

                if self.current_tok.type == t.TT_RCRLBRCKT:
                    res.log_advancement()
                    self.advance()
                else:
                    return res.fail(
                        InvalidSyntaxError(
                            self.current_tok.start, self.current_tok.end, 'Expected "}"'
                        )
                    )
            else:
                expr = res.log(self.statement())
                if res.error:
                    return res
                else_case = (expr, False)
        
        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseRes()
        cases, else_case = [], None
        if self.current_tok.matches(t.TT_KEYWORD, 'elif'):
            all_cases = res.log(self.if_expr_b())
            if res.error : return res
            cases, else_case = all_cases
        else:
            else_case = res.log(self.if_expr_c())
            if res.error: return res
        return res.success((cases, else_case))
    
    def for_expr(self):
        res = ParseRes()

        if not self.current_tok.matches(t.TT_KEYWORD, "for"):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected 'for'"
                )
            )

        res.log_advancement()
        self.advance()

        if not self.current_tok.type == t.TT_IDENTIFIER:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected identifier"
                )
            )
        var_name = self.current_tok
        res.log_advancement()
        self.advance()

        if not self.current_tok.type == t.TT_SEMICOLON:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected 'for'"
                )
            )

        res.log_advancement()
        self.advance()

        if not self.current_tok.value != var_name:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "One variable must be used while creating for loop",
                )
            )

        res.log_advancement()
        self.advance()

        if self.current_tok.type not in (
            t.TT_LT,
            t.TT_GT,
            t.TT_LTE,
            t.TT_GTE,
            t.TT_DEQ,
        ):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "Expected '==', '>', '<', '>=', '<='",
                )
            )

        op_start = self.current_tok
        res.log_advancement()
        self.advance()

        until = res.log(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == t.TT_SEMICOLON:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected semicolon"
                )
            )

        res.log_advancement()
        self.advance()

        if not self.current_tok.value != var_name:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "One variable must be used while creating for loop",
                )
            )

        res.log_advancement()
        self.advance()

        if self.current_tok.type not in (
            t.TT_MULEQ,
            t.TT_PLUSEQ,
            t.TT_DIVEQ,
            t.TT_MINUSEQ,
        ):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start,
                    self.current_tok.end,
                    "Expected '+=', '-=', '*=', '/='",
                )
            )
        op_end = self.current_tok
        res.log_advancement()
        self.advance()

        step = res.log(self.expr())
        if res.error:
            return res

        if self.current_tok.type != t.TT_LCRLBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '{'"
                )
            )
            
        res.log_advancement()
        self.advance()
        
        if self.current_tok.type == t.TT_NEWL:
            res.log_advancement()
            self.advance()
            
            exec_code = res.log(self.statements())
            if res.error: return res
            
            if self.current_tok.type != t.TT_RCRLBRCKT:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected '}'"
                    )
                )
            res.log_advancement()
            self.advance()
            
            return res.success(
                n.ForNode(var_name, op_start, until, op_end, step, exec_code, True)
            )
        
        exec_code = res.log(self.expr())
        if res.error:
            return res

        if self.current_tok.type != t.TT_RCRLBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '}'"
                )
            )
        return res.success(
            n.ForNode(var_name, op_start, until, op_end, step, exec_code, False)
        )

    def while_expr(self):
        res = ParseRes()

        if not self.current_tok.matches(t.TT_KEYWORD, "while"):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected 'while'"
                )
            )

        res.log_advancement()
        self.advance()

        condition = res.log(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == t.TT_LCRLBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '{'"
                )
            )

        res.log_advancement()
        self.advance()

        if self.current_tok.type == t.TT_NEWL:
            res.log_advancement()
            self.advance()
            
            exec_code = res.log(self.statements())
            if res.error: return res
            
            if self.current_tok.type != t.TT_RCRLBRCKT:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected '}'"
                    )
                )
            res.log_advancement()
            self.advance()
            
            return res.success(
                n.WhileNode(condition, exec_code, True)
            )
        
        exec_code = res.log(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == t.TT_RCRLBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '}'"
                )
            )
        
        return res.success(n.WhileNode(condition, exec_code, False))

    def func_def(self):
        res = ParseRes()

        if not self.current_tok.matches(t.TT_KEYWORD, "func"):
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected 'func'"
                )
            )

        res.log_advancement()
        self.advance()

        if self.current_tok.type == t.TT_IDENTIFIER:
            var_name = self.current_tok
            res.log_advancement()
            self.advance(),
            if not self.current_tok.type == t.TT_LPAREN:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected '('"
                    )
                )

        else:
            var_name = None
            if not self.current_tok.type == t.TT_LPAREN:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        "Expected '(' or identifier",
                    )
                )

        res.log_advancement()
        self.advance()

        arg_names = []

        if self.current_tok.type == t.TT_IDENTIFIER:
            arg_names.append(self.current_tok)
            res.log_advancement()
            self.advance()

            while self.current_tok.type == t.TT_COMMA:
                res.log_advancement()
                self.advance()

                if not self.current_tok.type == t.TT_IDENTIFIER:
                    return res.fail(
                        InvalidSyntaxError(
                            self.current_tok.start,
                            self.current_tok.end,
                            "Expected identifier",
                        )
                    )
                arg_names.append(self.current_tok)
                res.log_advancement()
                self.advance()

            if not self.current_tok.type == t.TT_RPAREN:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        "Expected ',' or ')'",
                    )
                )
        else:
            if not self.current_tok.type == t.TT_RPAREN:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        "Expected identifier or ')'",
                    )
                )
        res.log_advancement()
        self.advance()

        if self.current_tok.type == t.TT_ARROW:
            res.log_advancement()
            self.advance()

            exe = res.log(self.expr())
            if res.error:
                return res

            return res.success(n.FuncDefNode(var_name, arg_names, exe, True))
        elif self.current_tok.type == t.TT_LCRLBRCKT:
            res.log_advancement()
            self.advance()
            
            if self.current_tok.type!= t.TT_NEWL:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected new line"
                )
            )
            res.log_advancement()
            self.advance()
            
            exe = res.log(self.statements())
            if res.error: return res
            
            if not self.current_tok.type == t.TT_RCRLBRCKT:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start, self.current_tok.end, "Expected '}'"
                ))
            res.log_advancement()
            self.advance()
            
            return res.success(n.FuncDefNode(var_name, arg_names, exe, False))
        else:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, "Expected '->' or '{'"
                )
            )

    def CallFunc(self):
        res = ParseRes()
        quark = res.log(self.quark())
        if res.error:
            return res

        if self.current_tok.type == t.TT_LPAREN:
            res.log_advancement()
            self.advance()
            args = []

            if self.current_tok.type == t.TT_RPAREN:
                res.log_advancement()
                self.advance()
            else:
                args.append(res.log(self.expr()))
                if res.error:
                    return res.fail(
                        InvalidSyntaxError(
                            self.current_tok.start,
                            self.current_tok.end,
                            "Expected 'new', 'if', 'for', 'while', 'func' int, double, identifier, 'new', '+', '-' , ')', '[' or '('",
                        )
                    )

                while self.current_tok.value == ",":
                    res.log_advancement()
                    self.advance()
                    args.append(res.log(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != t.TT_RPAREN:
                    return res.fail(
                        InvalidSyntaxError(
                            self.current_tok.start,
                            self.current_tok.end,
                            "Expected ',' or ')'",
                        )
                    )
                res.log_advancement()
                self.advance()
            return res.success(n.CallFuncNode(quark, args))
        return res.success(quark)

    def list_expr(self):
        res = ParseRes()
        element_nodes = []
        pos_start = self.current_tok.start.get_pos()

        if self.current_tok.type != t.TT_LSQRBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, f"Expected '['"
                )
            )

        res.log_advancement()
        self.advance()

        if self.current_tok.type == t.TT_RSQRBRCKT:
            res.log_advancement()
            self.advance()
            return res.success(n.ListNode([], pos_start, self.current_tok.end.get_pos()))
        else:
            element_nodes.append(res.log(self.expr()))
            if res.error:
                return res.fail(
                    InvalidSyntaxError(
                        self.current_tok.start,
                        self.current_tok.end,
                        "Expected ']', 'new', 'if', 'for', 'while', 'func', int, double, identifier, '+', '-', '(', '[' or 'not'",
                    )
                )

        while self.current_tok.type == t.TT_COMMA:
            res.log_advancement()
            self.advance()

            element_nodes.append(res.log(self.expr()))
            if res.error:
                return res

        if self.current_tok.type != t.TT_RSQRBRCKT:
            return res.fail(
                InvalidSyntaxError(
                    self.current_tok.start, self.current_tok.end, f"Expected ',' or ']'"
                )
            )

        res.log_advancement()
        self.advance()

        return res.success(
            n.ListNode(element_nodes, pos_start, self.current_tok.end.get_pos())
        )

    def statements(self):
        res = ParseRes()
        statements = []
        pos_start = self.current_tok.start.get_pos()

        while self.current_tok.type == t.TT_NEWL:
            res.log_advancement()
            self.advance()
        statement = res.log(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == t.TT_NEWL:
                res.log_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            
            if not more_statements: break
            statement = res.try_log(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(n.ListNode(
        statements,
        pos_start,
        self.current_tok.end.get_pos()
        ))

    def statement(self):
        res = ParseRes()
        start = self.current_tok.start.get_pos()
        
        if self.current_tok.matches(t.TT_KEYWORD, 'return'):
            res.log_advancement()
            self.advance()
            
            expr = res.try_log(self.expr())
            
            if expr == None:
                self.reverse()
                
            return res.success(n.ReturnNode(expr, start, self.current_tok.end.get_pos()))
        if self.current_tok.matches(t.TT_KEYWORD, 'advance'):
            res.log_advancement()
            self.advance()

                
            return res.success(n.AdvanceNode(start, self.current_tok.end.get_pos()))
        if self.current_tok.matches(t.TT_KEYWORD, 'break'):
            res.log_advancement()
            self.advance()

                
            return res.success(n.BreakNode(start, self.current_tok.end.get_pos()))
        
        if self.current_tok.matches(t.TT_KEYWORD, 'include'):
            res.log_advancement()
            self.advance()
            
            str_node = res.log(self.quark())
            
            return res.success(n.IncludeNode(str_node, start, self.current_tok.end.get_pos()))
        
        expr = res.log(self.expr())
        if res.error: return res.fail(InvalidSyntaxError(
            self.current_tok.start,
            self.current_tok.end,
            "Expected 'return', 'advance', 'break', 'new', 'if', 'for', 'while', 'func' int, double, identifier, '+', '-' '(', '[' or 'not'"
        ))
        
        return res.success(expr)
    
    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseRes()
        left = res.log(func_a())
        if res.error:
            return res

        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            op_tok = self.current_tok
            res.log_advancement()
            self.advance()
            right = res.log(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
