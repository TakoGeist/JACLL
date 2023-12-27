from enum import Enum

class DataType(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STR = 3
    LIST = 4

    def inferetype(value):
        return

    def datatype(type: str):
        match type:
            case 'INT':
                return DataType.INT
            case 'FLOAT':
                return DataType.FLOAT
            case 'BOOL':
                return DataType.BOOL
            case 'STR':
                return DataType.STR
            case 'LIST':
                return DataType.LIST

class Comparator:
    def __eq__(self, other) -> bool:
        return self.name == other.name
    
    def __eq__(self, other: str) -> bool:
        return self.name == other

class RoseTree:
    def __init__(self, _type, _node, _children=[]):
        self.type = _type
        self.node = _node
        self.children = _children

    def add_child(self, child):
        self.children.append(child)

    def __str__(self) -> str:
        return f"{self.type} -> {self.node} with {[x.__str__() for x in self.children]}"

class ForLoop:
    def __init__(self, _condition, _initial= None, _repetition= None):
        self.condition = _condition
        self.initial = _initial
        self.repetition = _repetition

class IfClause:
    def __init__(self, _condition, _true, _false= None):
        self.condition = _condition
        self.true = _true
        self.false = _false

class Var(Comparator):
    def __init__(self, _name, _type, _value):
        self.name = _name
        self.type = _type
        self.value = _value

class Print:
    def __init__(self, _arg):
        self.arg = _arg

class Call:
    def __init__(self, _name, _args, _type) -> None:
        self.name = _name
        self.args = _args
        self.type = _type

class Func(Comparator):
    def __init__(self, _name, _args= [], _output= None):
        self.name = _name
        self.args = _args
        self.output = _output

    def __str__(self) -> str:
        ret = f"{self.name}"
        if self.args != []:
            ret += f" with {self.args}"
        if self.output != None:
            ret += f" returns {self.output}"
        return ret

class Prog:
    def __init__(self, _name):
        self.name = _name

    def __str__(self) -> str:
        return f"{self.name}"
