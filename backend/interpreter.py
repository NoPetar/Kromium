from .tokens import *
from .errs import RunTimeError, typeError
from typing import Union


class SymbolTable:
    def __init__(self, parent=None):
        self.values = {}
        self.types = {}
        self.is_const = {}
        self.parent = parent

    def get_var(self, name):
        try:
            
            value = self.values.get(name)
            data_type = self.types.get(name)
            if value == None and data_type == None:
                return self.parent.get_var(name)
        except TypeError:
            value, data_type = None, None

        return [value, data_type]

    def set_var(self, name : str, data_type : str, value : any, const : bool):
        self.values[name] = value
        self.types[name] = data_type
        self.is_const[name] = const

    def re_assign_var(self, name, value, node, ctx, res):
        var_data_type = self.types[name]
        const = self.is_const.get(name)
        if const:
            return res.fail(
                RunTimeError(
                    node.start,
                    node.end,
                    f"Variable {name} cannot be reassigned, because it is a constant",
                    ctx,
                )
            )
        self.values[name] = value
        self.types[name] = var_data_type

    def remove_var(self, name):
        del self.values[name]
        del self.types[name]
        del self.is_const[name]

    def is_var_const(self, name):
        return self.is_const[name]


class RTResult:
    def log(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def fail(self, error):
        self.error = error
        return self

    def __init__(self):
        self.value = None
        self.error = None


class Interpreter:
    def __init__(self):
        pass

    def visit(self, node, ctx):
        self.method_name = f"visit_{type(node).__name__}"
        method = getattr(self, self.method_name, self.no_visit)
        return method(node, ctx)

    def no_visit(self, node, ctx):
        raise Exception(f"Method {self.method_name} is not defined")

    def visit_IntegerNode(self, node, ctx):
        res = RTResult()
        return res.success(
            value=Integer(node.tok.value).set_context(ctx).set_pos(node.start, node.end)
        )

    def visit_DoubleNode(self, node, ctx):
        res = RTResult()
        return res.success(
            value=Double(node.tok.value).set_context(ctx).set_pos(node.start, node.end)
        )

    def visit_BinOpNode(self, node, ctx):
        res = RTResult()
        left = res.log(self.visit(node.leftn, ctx))
        right = res.log(self.visit(node.rightn, ctx))
        err, result = None, None
        if res.error:
            return res

        match node.op.value:
            case "+":
                result, err = left.addition(right)
            case "-":
                result, err = left.subtraction(right)
            case "*":
                result, err = left.multiplication(right)
            case "/":
                result, err = left.division(right)
            case "^":
                result, err = left.powed_by(right)
            case "**":
                result, err = left.powed_by(right)
            case "==":
                result, err = left.deq(right)
            case "!=":
                result, err = left.ne(right)
            case ">":
                result, err = left.gt(right)
            case "<":
                result, err = left.lt(right)
            case "<=":
                result, err = left.lte(right)
            case ">=":
                result, err = left.gte(right)
            case _:
                if node.op.matches(TT_KEYWORD, "and") or node.op.matches(TT_AMPR, "&"):
                    result, err = left.anded(right)
                elif node.op.matches(TT_KEYWORD, "or") or node.op.matches(TT_LINE, "|"):
                    result, err = left.ored(right)

        return (
            res.fail(err) if err else res.success(result.set_pos(node.start, node.end))
        )

    def visit_UnaryOpNode(self, node, ctx):
        res = RTResult()
        num = res.log(self.visit(node.node, ctx))
        if res.error:
            return res

        err = None

        if node.op.type == TT_MINUS:
            num, err = num.multiplication(Integer(-1))
        elif node.op.matches(TT_KEYWORD, "not"):
            num, err = num.notted()

        return res.fail(err) if err else res.success(num.set_pos(node.start, node.end))

    def visit_VarAccessNode(self, node, ctx):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = ctx.symbol_table.get_var(var_name)[0]
        
        if not value:
            return res.fail(
                RunTimeError(node.start, node.end, f'"{var_name}" is not defined', ctx)
            )
        try:
            value = value.copy().set_pos(node.start, node.end).set_context(ctx)
        except: pass
        return res.success(value)

    def visit_VarAssignNode(self, node, ctx):
        res = RTResult()
        var_name = node.var_name_tok.value
        var_type = node.var_type_tok.value
        value = res.log(self.visit(node.value_node, ctx))
        match var_type:
            case "int":
                var_type = Integer
            case "double":
                var_type = Double
            case "string":
                var_type = String
            case "func":
                var_type = Function
            case "list":
                var_type = List
        is_const = node.is_const
        if res.error:
            return res
        if isinstance(value, var_type):
            ctx.symbol_table.set_var(var_name, var_type, value, is_const)
            return res.success(value)
        else:
            return res.fail(
                typeError(
                    node.start,
                    node.end,
                    f"Cannot convert type '{type(value).__name__}' to '{var_type.__name__}''",
                )
            )

    def visit_VarReAssignNode(self, node, ctx):

        res = RTResult()
        var_name = node.var_name_tok.value
        value_ = res.log(self.visit(node.value_node, ctx))
        if res.error:
            return res
        if ctx.symbol_table.is_var_const(var_name):
            return res.fail(
                RunTimeError(
                    node.start,
                    node.end,
                    f"Variable {var_name} cannot be reassigned, because it is a constant ",
                    ctx,
                )
            )

        match node.op:
            case "=":
                ctx.symbol_table.re_assign_var(var_name, value_, node, ctx, res)
            case "+":
                if ctx.symbol_table.get_var(var_name)[1] == Integer:
                    r = Integer(
                        ctx.symbol_table.get_var(var_name)[0].value + value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == Double:
                    r = Double(
                        ctx.symbol_table.get_var(var_name)[0].value + value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == List:
                    new = ctx.symbol_table.get_var(var_name)[0].elements
                    new.append(value_.value)
                    r = List(new)
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
            case "-":
                if ctx.symbol_table.get_var(var_name)[1] == Integer:
                    r = Integer(
                        ctx.symbol_table.get_var(var_name)[0].value - value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == Double:
                    r = Double(
                        ctx.symbol_table.get_var(var_name)[0].value - value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == String:
                    r = String(
                        ctx.symbol_table.get_var(var_name)[0].value + value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == List:
                    new = ctx.symbol_table.get_var(var_name)[0].elements
                    new.pop(value_.value)
                    r = List(new)
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
            case "*":
                if ctx.symbol_table.get_var(var_name)[1] == Integer:
                    r = Integer(
                        ctx.symbol_table.get_var(var_name)[0].value * value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == Double:
                    r = Double(
                        ctx.symbol_table.get_var(var_name)[0].value * value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == String:
                    r = String(
                        ctx.symbol_table.get_var(var_name)[0].value * value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == List:
                    new = ctx.symbol_table.get_var(var_name)[0].elements
                    new.extend(value_.elements)
                    r = List(new)
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
            case "/":
                if ctx.symbol_table.get_var(var_name)[1] == Integer:
                    r = Integer(
                        ctx.symbol_table.get_var(var_name)[0].value / value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == Double:
                    r = Double(
                        ctx.symbol_table.get_var(var_name)[0].value / value_.value
                    )
                    ctx.symbol_table.re_assign_var(var_name, r, node, ctx, res)
                    value_ = r
                elif ctx.symbol_table.get_var(var_name)[1] == List:
                    new = ctx.symbol_table.get_var(var_name)[0].elements
                    new = new[value_.value]
                    ctx.symbol_table.re_assign_var(var_name, new, node, ctx, res)
                    value_ = new

        return res.success(value_)

    def visit_IfNode(self, node, context):
        res = RTResult()
        
        for condition, expr, shrn  in node.cases:
            condition_value = res.log(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.log(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(Integer.null if shrn else expr_value)

        if node.else_case:
            expr , shrn = node.else_case
            else_value = res.log(self.visit(expr, context))
            if res.error:
                return res
            return res.success(Integer.null if shrn else else_value)

        return res.success(Integer.null)

    def visit_ForNode(self, node, ctx):
        res = RTResult()
        elements = []
        condition = None
        start_value = ctx.symbol_table.get_var(node.var_name_tok.value)[0]

        end_value = res.log(self.visit(node.end_value_node, ctx))
        if res.error:
            return res

        step_value = res.log(self.visit(node.step_value_node, ctx))
        if res.error:
            return res

        i = start_value.value
        op_start = node.op_start.value
        op_end = node.op_end.value

        match op_start:
            case "==":
                condition = lambda: i == end_value.value
            case ">":
                condition = lambda: i > end_value.value
            case "<":
                condition = lambda: i < end_value.value
            case ">=":
                condition = lambda: i >= end_value.value
            case "<=":
                condition = lambda: i <= end_value.value

        while condition():
            ctx.symbol_table.re_assign_var(
                node.var_name_tok.value, Integer(i), node, ctx, res
            )
            match op_end:
                case "+=":
                    i += step_value.value
                case "-=":
                    i -= step_value.value
                case "*=":
                    i *= step_value.value
                case "/=":
                    i /= step_value.value
            elements.append(res.log(self.visit(node.exec_node, ctx)))
            if res.error:
                return res

        return res.success(
            Integer.null if node.should_return_null else List(elements).set_context(ctx).set_pos(node.start, node.end)
        )

    def visit_WhileNode(self, node, ctx):
        res = RTResult()
        elements = []
        while True:
            condition = res.log(self.visit(node.condition, ctx))
            if res.error:
                return res

            if not condition.is_true():
                break

            elements.append(res.log(self.visit(node.exec_node, ctx)))
            if res.error:
                return res

        return res.success(
            Integer.null if node.should_return_null else List(elements).set_context(ctx).set_pos(node.start, node.end)
        )

    def visit_StringNode(self, node, ctx):
        return RTResult().success(
            String(node.tok.value).set_context(ctx).set_pos(node.start, node.end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.exec_code
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names, node.should_return_null)
            .set_context(context)
            .set_pos(node.start, node.end)
        )

        if node.var_name_tok:
            context.symbol_table.set_var(func_name, Function, func_value, False)

        return res.success(func_value)

    def visit_CallFuncNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.log(self.visit(node.caller, context))
        if res.error:
            return res
        
        value_to_call = value_to_call.copy().set_pos(node.start, node.end)

        for arg_node in node.arg_nodes:
            args.append(res.log(self.visit(arg_node, context)))
            if res.error:
                return res

        return_value = res.log(value_to_call.execute(args))
        if res.error:
            return res
        
        if hasattr(value_to_call, 'copy'):
            value_to_call = value_to_call.copy().set_pos(node.start, node.end)
        else:
            return res.fail(
                RunTimeError(
                    node.start, node.end, f"'{value_to_call}' is not callable", context
                )
            )
        return res.success(return_value)

    def visit_ListNode(self, node, ctx):
        res = RTResult()
        els = []
        for n in node.element_nodes:
            els.append(res.log(self.visit(n, ctx)))
            if res.error:
                return res
        return res.success(List(els).set_context(ctx).set_pos(node.start, node.end))

    def visit_NoneType(self, node, ctx):
        return RTResult().success(NoneType())
    
    
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def addition(self, other):
        return None, self.illegal_operation(other)

    def subtracion(self, other):
        return None, self.illegal_operation(other)

    def multiplication(self, other):
        return None, self.illegal_operation(other)

    def division(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def eq(self, other):
        return None, self.illegal_operation(other)

    def ne(self, other):
        return None, self.illegal_operation(other)

    def lt(self, other):
        return None, self.illegal_operation(other)

    def gt(self, other):
        return None, self.illegal_operation(other)

    def lte(self, other):
        return None, self.illegal_operation(other)

    def gte(self, other):
        return None, self.illegal_operation(other)

    def anded(self, other):
        return None, self.illegal_operation(other)

    def ored(self, other):
        return None, self.illegal_operation(other)

    def notted(self, other):
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception("No copy method defined")

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RunTimeError(
            self.pos_start, other.pos_end, "Illegal operation", self.context
        )


class Integer(Value):
    def __init__(self, value):
        super().__init__()
        try:
            self.value = int(value)
        except:
            self.value = value.value
        self.str_type = 'int'

    def addition(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                (Integer(self.value + other.value).set_context(self.context), None)
                if self.value + other.value == int(self.value + other.value)
                else (Double(self.value + other.value).set_context(self.context), None)
            )
        else:
            return None, Value.illegal_operation(self, other)

    def subtraction(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                (Integer(self.value - other.value).set_context(self.context), None)
                if self.value - other.value == int(self.value - other.value)
                else (Double(self.value - other.value).set_context(self.context), None)
            )
        else:
            return None, Value.illegal_operation(self, other)

    def multiplication(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                (Integer(self.value * other.value).set_context(self.context), None)
                if self.value * other.value == int(self.value * other.value)
                else (Double(self.value * other.value).set_context(self.context), None)
            )
        elif isinstance(other, String):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def division(self, other):
        if isinstance(other, Union[Integer, Double]):
            if other.value == 0:
                return None, RunTimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )

            return (
                (Integer(self.value / other.value).set_context(self.context), None)
                if self.value / other.value == int(self.value / other.value)
                else (Double(self.value / other.value).set_context(self.context), None)
            )
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (Integer(self.value**other.value).set_context(self.context)), (
                None
                if self.value**other.value == int(self.value**other.value)
                else (Double(self.value**other.value).set_context(self.context), None)
            )
        else:
            return None, Value.illegal_operation(self, other)

    def deq(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                (Integer(self.value == other.value).set_context(self.context), None)
                if float(self.value == other.value) == int(self.value == other.value)
                else (Double(self.value == other.value).set_context(self.context), None)
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ne(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value != other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def lt(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value < other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def gt(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value > other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def lte(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value <= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def gte(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value >= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def anded(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value and other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ored(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Integer(int(self.value or other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Integer(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Integer(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

    
class Double(Value):
    def __init__(self, value):
        super().__init__()
        self.value = float(value)
        self.str_type = 'double'
        
    def addition(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subtraction(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiplication(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def division(self, other):
        if isinstance(other, Union[Integer, Double]):
            if other.value == 0:
                return None, RunTimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )

            return Double(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(self.value**other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def deq(self, other):
        if isinstance(other, Union[Double, Integer]):
            return (
                Integer(int(self.value == other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ne(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Double(int(self.value != other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def lt(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def gt(self, other):
        if isinstance(other, Union[Integer, Double]):
            return Double(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def lte(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Double(int(self.value <= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def gte(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Double(int(self.value >= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def anded(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Double(int(self.value and other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ored(self, other):
        if isinstance(other, Union[Integer, Double]):
            return (
                Double(int(self.value or other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Double(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Double(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.str_type = 'string'

    def addition(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiplication(self, other):
        if isinstance(other, Integer):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def deq(self, other):
        if isinstance(other, String):
            return (
                Integer(int(self.value == other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ne(self, other):
        if isinstance(other, String):
            return (
                Integer(int(self.value != other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.str_type = 'list'
    def addition(self, other):
        new = self.copy()
        new.elements.append(other)

        return new, None

    def multiplication(self, other):
        if isinstance(other, List):
            new = self.copy()
            new.elements.extend(other.elements)
            return new, None
        else:
            return None, Value.illegal_operation(self, other)

    def subtraction(self, other):
        if isinstance(other, Integer):
            new = self.copy()
            try:
                new.elements.pop(other.value)
                return new, None
            except Exception:
                return None, RunTimeError(
                    other.start, other.end, "List index out of bounds"
                )
        else:
            return None, Value.illegal_operation(self, other)

    def division(self, other):
        if isinstance(other, Integer):
            try:
                return self.elements[other.value], None
            except Exception:
                return None, RunTimeError(
                    other.start, other.end, "List index out of bounds"
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):

        copy = List(self.elements)
        copy.set_pos(self.pos_start).set_context(self.context)

        return copy

    def __repr__(self):
        return f"{self.elements}"


class BaseFunc(Value):
    def __init__(self, name):
        self.name = name or "<anonymous>"
        self.context = None
        self.pos_start = None
        self.pos_end = None
        
    def generate_ctx(self):
        ctx = Context(self.name, self.context, self.pos_start)
        ctx.symbol_table = SymbolTable(ctx.parent.symbol_table)
        return ctx

    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) > len(arg_names):
            return res.fail(
                RunTimeError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                    self.context,
                )
            )

        if len(args) < len(arg_names):
            return res.fail(
                RunTimeError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
                    self.context,
                )
            )
        return res.success(None)

    def populate_args(self, arg_names, args, ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(ctx)
            ctx.symbol_table.set_var(arg_name, None, arg_value, False)

    def check_and_populate(self, arg_names, args, ctx):
        res = RTResult()

        res.log(self.check_args(arg_names, args))
        if res.error:
            return res
        self.populate_args(arg_names, args, ctx)
        return res.success(None)


class Function(BaseFunc):
    def __init__(self, name, exec_code, args, should_return_null):
        super().__init__(name)
        self.exec_code = exec_code
        self.args = args
        self.shrn = should_return_null

    def execute(self, args):
        res = RTResult()
        itr = Interpreter()
        ctx = self.generate_ctx()
        

        res.log(self.check_and_populate(self.args, args, ctx))
        if res.error:
            return res

        value = res.log(itr.visit(self.exec_code, ctx))
        if res.error:
            return res
        return res.success(Integer.null if self.shrn else value)
    
    
    def copy(self):
        copy = Function(self.name, self.exec_code, self.args, self.shrn)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"

class BuiltInFunc(BaseFunc):
    def __init__(self, name):
        super().__init__(name)
    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_ctx()

        method_name = f'_{self.name}_'
        method = getattr(self, method_name, self.no_visit_method)

        res.log(self.check_and_populate(method.arg_names, args, exec_ctx))
        if res.error: return res

        return_value = res.log(method(exec_ctx))
        if res.error: return res
        return res.success(return_value)
  
    def no_visit_method(self, node, context):
        raise Exception(f'No _{self.name}_ method defined')
    
    
    def copy(self):
        copy_ = BuiltInFunc(self.name)
        copy_.set_context(self.context)
        copy_.set_pos(self.pos_start, self.pos_end)
        return copy_
    def __repr__(self):
        return f'<built-in function {self.name}>'

    def _out_(self, exec_ctx):
        print(exec_ctx.symbol_table.get_var('value')[0])    
        return RTResult().success(Integer.null)
    def _input_(self, exec_ctx):
        inputed = input()
        return RTResult().success(String(inputed))
    def _integer_(self, exec_ctx):
        arg = exec_ctx.symbol_table.get_var('value')[0]
        arg = Integer(arg)
        return RTResult().success(arg)
        
    
    def _typeof_(self, exec_ctx):
        return RTResult().success(exec_ctx.symbol_table.get_var('value')[0].str_type)
        
    def _len_(self, exec_ctx):
        v = exec_ctx.symbol_table.get_var('value')[0]
        return RTResult().success(len(str(v.value)))   
        
    _out_.arg_names = ['value']
    _input_.arg_names = []
    _integer_.arg_names = ['value']
    _typeof_.arg_names = ['value']
    _len_.arg_names = ['value']


class NoneType(Value):
    def __init__(self):
        self.value = '\n'
        self.error = None
    def __repr__(self):
        return str(Integer.null)
    
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


BuiltInFunc.out = BuiltInFunc("out")
BuiltInFunc.input = BuiltInFunc("input")
BuiltInFunc.integer = BuiltInFunc("integer")
BuiltInFunc.typeof = BuiltInFunc("typeof")
BuiltInFunc.len = BuiltInFunc("len")


Integer.null = Integer(0)
Integer.false = Integer(0)
Integer.true = Integer(1)
