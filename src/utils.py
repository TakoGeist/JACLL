from enum import Enum
    
class DataType(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STR = 3
    LIST = 4

    def inferetype(value, scope):
        match value:
            case bool():
                return DataType.BOOL
            case float():
                return DataType.FLOAT
            case int():
                return DataType.INT
            case str():
                return DataType.STR
            case Func():
                return value.output   
            # case Var():
            #     if value.name not in scope:
            #         return 1
            #     else:
            #         return value.type         
            case _:
                try:
                    if value.type == DataType.LIST:
                        return DataType.LIST
                except AttributeError:
                    return None
            
    def datatype(type: str):
        match type:
            case "int":
                return DataType.INT
            case "float":
                return DataType.FLOAT
            case "bool":
                return DataType.BOOL
            case "str":
                return DataType.STR
            case "list":
                return DataType.LIST

class Comparator:
    def __eq__(self, other) -> bool:
        return self.name == other.name
    
    def __eq__(self, other: str) -> bool:
        return self.name == other

class List:
    def __init__(self,
                 _type,
                 _size):
        self.type = _type
        self.size = _size

    def __eq__(self, other):
        return other == DataType.LIST
    
    def __str__(self) -> str:
        return f"Array of {self.type.__str__()} with size {self.size.__str__()}\n"

class RoseTree:
    def __init__(self, 
                 _type, 
                 _node, 
                 _children=[]):
        self.type = _type
        self.node = _node
        self.children = _children

    def add_child(self, 
                  child):
        self.children.append(child)

    def __str__(self) -> str:
        return f"{self.type.__str__()} -> {self.node.__str__()}{{{[x.__str__() for x in self.children]}}}\n"

class ForLoop:
    def __init__(self, 
                 _condition, 
                 _initial= None, 
                 _repetition= None):
        self.condition = _condition
        self.initial = _initial
        self.repetition = _repetition

    def __str__(self) -> str:
        out = ""
        if self.initial != None:
            out += f"Start with {self.initial.__str__()} "
        out += f"repeat if {self.condition.__str__()} "
        if self.repetition != None:
            out += f"do {self.repetition.__str__()}"
        return out + "\n"

class IfClause:
    def __init__(self, 
                 _condition, 
                 _true, 
                 _false= None):
        self.condition = _condition
        self.true = _true
        self.false = _false

    def __str__(self) -> str:
        out = f"If {self.condition.__str__()} then {self.true.__str__()}"
        if self.false != None:
            out += f" else {self.false.__str__()}"
        return out + "\n"        

class Var(Comparator):
    def __init__(self, 
                 _name, 
                 _type, 
                 _value, 
                 _index= None, 
                 _row= None, 
                 _column= None):
        self.name = _name
        self.type = _type
        self.value = _value
        self.index = _index
        self.row = _row
        self.column = _column

    def __copy__(self):
        return Var(self.name, self.type, self.value, self.index, self.row, self.column)

    def __str__(self) -> str:
        out = f"{self.name.__str__()}: {self.type.__str__()} = {self.value.__str__()}"
        if self.index != None:
            out += f" at {self.index.__str__()}"
        if self.row != None:
            out += f" with size {self.row.__str__()}"
        if self.column != None:
            out += f"X{self.column.__str__()}"
        return out + "\n"

class Print:
    def __init__(self, 
                 _arg):
        self.arg = _arg

    def __str__(self) -> str:
        return f"print({self.arg.__str__()})\n"

class Call:
    def __init__(self, 
                 _name, 
                 _args, 
                 _type) -> None:
        self.name = _name
        self.args = _args
        self.type = _type

    def __str__(self) -> str:
        out = f"Function {self.name.__str__()}({self.args.__str__()})"
        if self.type != None:
            out += f" returns {self.type.__str__()}"
        return out + "\n"

class Func(Comparator):
    def __init__(self, 
                 _name, 
                 _args= [], 
                 _output= None):
        self.name = _name
        self.args = _args
        self.output = _output
        self.scope = {}

    def __str__(self) -> str:
        ret = f"{self.name}"
        if self.args != []:
            ret += f"({self.args.__str__()})"
        if self.output != None:
            ret += f" returns {self.output.__str__()}"
        return ret

class Prog:
    def __init__(self, 
                 _name):
        self.name = _name

    def __str__(self) -> str:
        return f"{self.name.__str__()}"
