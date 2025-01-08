from . import lexer, parser, interpreter
import os

global_symbol_table = interpreter.SymbolTable()
global_symbol_table.set_var("null", "int", interpreter.Integer.null, True)
global_symbol_table.set_var("none", "int", interpreter.Integer.null, True)
global_symbol_table.set_var("false", "int", interpreter.Integer.false, True)
global_symbol_table.set_var("true", "int", interpreter.Integer.true, True)
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
