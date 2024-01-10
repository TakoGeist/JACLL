from enum import IntEnum
    
class SyntaxError(Exception):
    def __init__(self, line, message) -> None:
        self.message = f"Parser found an error at line {line}.\n{message}"
        super().__init__(self.message)

class SymbolTable():
    def __init__(self):
        self.table = {}
        self.stack = 0

    def add(self, other):
        if other.get_type() == DataType.LIST:
            self.table[other.name()] = [other.get_type(), self.stack, other.get_elem_type()]
        else:
            self.table[other.name()] = [other.get_type(), self.stack]
        
        if other.type == 'init':
            self.stack += other.get_size()
        else:
            self.stack += 1
    
    def remove(self, other):
        self.table.pop(other.name())
        
        if other.type == 'init':
            self.stack -= other.get_size()
        else:
            self.stack -= 1

    def offset(self, num):
        self.stack -= num

    def __getitem__(self, name):
        return self.table[name]

    def empty(self):
        self.table = {}
        self.stack = 0        

class DataType(IntEnum):
    INT = 1
    FLOAT = 2
    BOOL = 3
    STR = 4
    LIST = 5

    def is_valid(self, op):
        if op in ['==', '!=', '&&', '||'] and self not in [DataType.STR, DataType.LIST] :
            return True
        if op in ['+', '-', '*', '/', '<=', '<', '>=', '>'] and self in [DataType.INT, DataType.FLOAT]:
            return True
        if op == '%' and self == DataType.INT:
            return True
        if op == '+' and self == DataType.STR:
            return True
        return False

    def inferetype(value):
        match value:
            case bool():
                return DataType.BOOL
            case float():
                return DataType.FLOAT
            case int():
                return DataType.INT
            case str():
                return DataType.STR
            case RoseTree():
                return value.children[0]           
            case _:
                try:
                    if value.type == DataType.LIST:
                        return DataType.LIST
                except AttributeError:
                    return None
            
    def terminator(self):
        match self:
            case DataType.INT:
                return 'i'
            case DataType.BOOL:
                return 'i'
            case DataType.FLOAT:
                return 'f'
            case _:
                raise ValueError("Invalid type found.")

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
            
    def __str__(self):
        match self:
            case 1:
                return "INT"
            case 2:
                return "FLOAT"
            case 3:
                return "BOOL"
            case 4:
                return "STR"
            case 5:
                return "LIST"

class RoseTree:
    def __init__(self, 
                 _type, 
                 _children=[]):
        self.type = _type
        self.children = _children

    def add_child(self, 
                  child):
        self.children.append(child)

    def left(self):
        if self.type != 'BinOp':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'left'.")
        return self.children[2]

    def right(self):
        if self.type != 'BinOp':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'right'.")
        return self.children[3]

    def op(self):
        if self.type == 'neg':
            return ['pushi 0\n', 'sub\n']
        
        if self.type == 'not':
            return 'not\n'
        
        if self.type != 'BinOp':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'op'.")
                 
        if self.children[0] == DataType.FLOAT:
            type = 'f'
        else:
            type = ''
        match self.children[1]:
            case '+' if self.children[0] == DataType.STR:
                return 'concat \n'
            case '+':
                return type + 'add\n'
            case '-':
                return type + 'sub\n'
            case '*':
                return type + 'mul\n'
            case '/' if self.children[0] == DataType.INT:
                return 'div\nftoi\n' #Force int type
            case '/':
                return type + 'div\n'
            case '%':
                return 'mod\n'
            case '&&':
                return 'and\n'
            case '||':
                return 'or\n'
            case '>':
                return type + 'sup\n'
            case '>=':
                return type + 'supeq\n'
            case '<':
                return type + 'inf\n'
            case '<=':
                return type + 'infeq\n'
            case '==':
                return 'equal\n'
            case '!=':
                return 'equal\nnot\n'
                
    def name(self):
        if self.type in ['BinOp', 'neg', 'not', 'atrib']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'name'.")
        return self.children[1]

    def code(self):
        if self.type != 'func':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'code'.")
        return self.children[3]
    
    def args(self):
        if self.type not in ['func', 'call']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'args'.")
        return self.children[2]

    def val(self):
        if self.type not in ['init', 'val']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'val'.")
        if self.type == 'init':
            return self.children[2]
        else:
            return self.children[1]

    def index(self):
        if self.type != 'valList':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'index'.")
        return self.children[2]

    def get_size(self):
        if self.type in ['prog', 'func', 'for', 'if', 'print', 'call']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'get_size'.")        
        if self.get_type() == DataType.LIST:
            return len(self.children[2])
        return 1

    def get_type(self):
        if self.type == 'prog':
            return AttributeError(f"Instance of '{self.type}' has no attribute 'get_type'.")    
        if type(self.children[0]) == list:
            return DataType.LIST    
        return self.children[0]

    def get_elem_type(self):
        if type(self.children[0]) == list:
            return self.children[0][1].get_elem_type()
        if self.children[0] == DataType.LIST:
            if self.type == 'valList':
                return self.children[-1]
            else:
                if type(self.children[2]) == list:
                    if len(self.children[2]) != self.children[3]:
                        return DataType.INT
                    else:
                        return self.children[2][0].get_elem_type()
                else:
                    return self.children[2]
        return self.children[0]

    def validate_op(self):
        if self.type not in ['BinOp', 'neg', 'not']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'validate_op'.")
        if len(self.children) < 2:
            return IndexError(f"Invalid operation on {self.type.__str__()} of length {len(self.children)}.")
        elif len(self.children) == 2:
            self.children[0] = self.children[1].get_elem_type()    
        elif len(self.children) == 3:
            self.children[0] = DataType.BOOL if self.type == 'not' else self.children[1].get_elem_type()
        else:
            left = self.children[2].get_elem_type()
            right = self.children[3].get_elem_type()
            if left != right:
                return TypeError(f"Mismatched types. Instance of {left} and {right} found.")
            if not self.children[2].get_elem_type().is_valid(self.children[1]):
                return SyntaxError(f"Invalid use of {self.children[1]} operator with value of type {self.children[2].get_elem_type()}.")
            if self.children[1] in ['==', '!=', '<=', '<', '>=', '>', '&&', '||']:
                self.children[0] = DataType.BOOL
            else:
                self.children[0] = self.children[2].get_elem_type()
        return 0            
            

    def __str__(self) -> str:
        return f"{self.type.__str__()} -> {', '.join([stringify(x) for x in self.children])}\n"

    def __repr__(self):
        repr_string = f"RoseTree(\n type='{self.type}',\n children=[\n"

        for child in self.children:
            repr_string += _indent(repr(child), 4) + ",\n"

        repr_string = repr_string[:-2]
        repr_string += "\n])"

        return repr_string
    
def _indent(string="", indent=4):
    return "\n".join(f"{' ' * indent}{line}" for line in string.splitlines())

def stringify(value):
    match value:
        case list():
            return ", ".join([stringify(x) for x in value])
        case RoseTree():
            return value.__str__()           
        case _:
            return str(value)

