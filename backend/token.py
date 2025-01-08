import json
import os
path =  f'{os.path.dirname(os.path.abspath(__file__))}\..\\assets\\tok_values.json'
vals = json.load(open(path))


class Token:
    def __init__(self, type_: any,  start=None, end=None, data_type = None,value=None,):
        self.type = type_
        if vals.get(self.type) != None:
            self.value = vals.get(self.type)
        else:
            self.value = value
        self.data_type = data_type

        if start:
            self.start = start.get_pos()
            self.end = start.get_pos().advance()
        if end:
            self.end = end

    def matches(self, type_ , value_):
        return self.type == type_ and self.value == value_
    
    def data_type_match(self, type_):
        return type(self.data_type) == type_
    
    def __repr__(self):
        return f"{self.type}:{self.value}" if self.value else f"{self.type}"
