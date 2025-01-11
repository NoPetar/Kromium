from typing import Union


class IntegerNode:
    def __init__(self, tok: int):
        self.tok = tok
        self.start = self.tok.start
        self.end = self.tok.end
        self.data_type = 'int'
    
    def get_child(self):
        return self.data_type
    
    def __repr__(self):
        return str(self.tok)
    
class DoubleNode:
    def __init__(self, tok: float):
        self.tok = tok
        self.start = self.tok.start
        self.end = self.tok.end
        self.data_type = 'double'

    def get_child(self):
        return self.data_type
    
    def __repr__(self):
        return str(self.tok)

class StringNode:
    def __init__(self, tok: str):
        self.tok = tok
        self.start = self.tok.start
        self.end = self.tok.end
        self.data_type = 'string'

    def get_child(self):
        return self.data_type
    
    def __repr__(self):
        return str(self.tok)

class BinOpNode:
    def __init__(self, leftn, op, rightn):
        self.leftn = leftn
        self.op = op
        self.rightn = rightn

        self.start = self.leftn.start
        self.end = self.rightn.end
    
    def get_child(self):
        return self.leftn , self.rightn
    
    def __repr__(self):
        return f"({self.leftn},{self.op},{self.rightn})"


class UnaryOpNode:
    def __init__(self, op_tok, node: Union[IntegerNode, DoubleNode, BinOpNode]):
        self.op = op_tok
        self.node = node
        self.start = self.op.start
        self.end = self.node.end

    def get_child(self):
        return self.node
    
    
    def __repr__(self):
        return f"({self.op}, {self.node})"

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.start = self.var_name_tok.start
        self.end = self.var_name_tok.end

class VarAssignNode:
    def __init__(self, var_name_tok , var_type_tok, value_node, is_const):
        self.var_name_tok = var_name_tok
        self.var_type_tok = var_type_tok
        self.value_node = value_node
        self.is_const = is_const
        self.start = self.var_name_tok.start
        self.end = self.var_name_tok.end

class VarReAssignNode:
    def __init__(self, var_name_tok, value_node, op):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.op = op
        self.start = self.var_name_tok.start
        self.end = self.var_name_tok.end

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
        self.start = self.cases[0][0].start
        self.end = (self.else_case or self.cases[-1])[0].end
        
        
class ForNode:
    def __init__(self, var_name_tok , op_start, end_value_node, op_end, step_value_node, exec_node, ret_null):
        self.var_name_tok  = var_name_tok 
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.exec_node = exec_node
        self.op_start = op_start
        self.op_end = op_end
        self.should_return_null = ret_null

        self.start = self.var_name_tok.start
        self.end = self.exec_node.end
        
class WhileNode:
    def __init__(self, condition, exec_node, ret_null):
        self.condition = condition
        self.exec_node = exec_node
        self.should_return_null = ret_null
        self.start = self.condition.start
        self.end = self.exec_node.end

class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, exec_code, ret_null):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.exec_code = exec_code
        self.should_return_null= ret_null
        if self.var_name_tok: self.start = self.var_name_tok.start
        elif len(self.arg_name_toks) >= 1: self.start = self.arg_name_toks[0].start
        else: self.start = self.exec_code.start
        
        self.end = self.exec_code.end
        
class CallFuncNode:
    def __init__(self, caller, arg_nodes):
        self.caller = caller
        self.arg_nodes = arg_nodes
        self.start = self.caller.start

        if len(self.arg_nodes) >= 1: self.end = self.arg_nodes[-1].end
        else : self.end = self.caller.end

class ListNode:
    def __init__(self, element_nodes, start , end):
        self.element_nodes = element_nodes
        self.start  = start 
        self.end = end

        