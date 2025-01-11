from . import lexer, parser, interpreter
import os

global_symbol_table = interpreter.SymbolTable()
global_symbol_table.set_var("null", interpreter.Integer, interpreter.Integer.null, True)
global_symbol_table.set_var("none", interpreter.Integer, interpreter.Integer.null, True)
global_symbol_table.set_var("false", interpreter.Integer, interpreter.Integer.false, True)
global_symbol_table.set_var("true", interpreter.Integer, interpreter.Integer.true, True)

#BUILT_IN_FUNCS

global_symbol_table.set_var("out", interpreter.BuiltInFunc, interpreter.BuiltInFunc.out, True)
global_symbol_table.set_var("input", interpreter.BuiltInFunc, interpreter.BuiltInFunc.input, True)
global_symbol_table.set_var("integer", interpreter.BuiltInFunc, interpreter.BuiltInFunc.integer, True)
global_symbol_table.set_var("typeof", interpreter.BuiltInFunc, interpreter.BuiltInFunc.typeof, True)
global_symbol_table.set_var("len", interpreter.BuiltInFunc, interpreter.BuiltInFunc.len, True)

os.system("cls")

def run(fn, code):
    l = lexer.Lexer(fn=fn, code=code)
    t, err = l.bake_tokens()
    if err:
        return None, err
    
    p = parser.Parser(t)
    ast = p.parse()
    if ast.error:
        return None, ast.error
    
    i = interpreter.Interpreter()
    ctx = interpreter.Context("<main>")
    ctx.symbol_table = global_symbol_table
    

    r = i.visit(ast.node, ctx)
    return r.value, r.error
