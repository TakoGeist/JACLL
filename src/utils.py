from enum import IntEnum
    
class DataType(IntEnum):
    INT = 1
    FLOAT = 2
    BOOL = 3
    STR = 4
    LIST = 5

    def is_valid(self, op):
        if op in ['==', '!=', '<=', '<', '>=', '>', '&&', '||'] and self not in [DataType.STR, DataType.LIST] :
            return True
        if op in ['+', '-', '*', '/'] and self in [DataType.INT, DataType.FLOAT]:
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

    def get_type(self):
        if self.children[0] == DataType.LIST:
            return self.children[1].get_type()
        return self.children[0]

    def validate_op(self):
        if self.type not in ['BinOp', 'neg', 'not']:
            return AttributeError(f"Instance of '{self.type}' has no attribute 'validate_op'.")
        if len(self.children) < 2:
            return IndexError(f"Invalid operation on {self.type.__str__()} of length {len(self.children)}.")
        elif len(self.children) == 2:
            self.children[0] = self.children[1].get_type()    
        elif len(self.children) == 3:
            self.children[0] = DataType.BOOL if self.type == 'not' else self.children[1].get_type()
        else:
            left = self.children[2].get_type()
            right = self.children[3].get_type()
            if left != right:
                return TypeError(f"Mismatched types. Instance of {left} and {right} found.")
            if not self.children[2].get_type().is_valid(self.children[1]):
                return SyntaxError(f"Invalid use of {self.children[1]} operator with value of type {self.children[2].get_type()}.")
            if self.children[1] in ['==', '!=', '<=', '<', '>=', '>', '&&', '||']:
                self.children[0] = DataType.BOOL
            else:
                self.children[0] = self.children[2].get_type()
        return 0            
            

    def __str__(self) -> str:
        return f"{self.type.__str__()} -> {', '.join([stringify(x) for x in self.children])}\n"
    

def stringify(value):
    match value:
        case list():
            return ", ".join([stringify(x) for x in value])
        case RoseTree():
            return value.__str__()           
        case _:
            return str(value)

