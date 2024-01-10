from utils import *
from copy import deepcopy
import ply.yacc as yacc
from jacll_lexer import tokens, lexer

precedence = (
              ('left', 'OR'),
              ('left', 'AND'),
              ('nonassoc', 'LEQUAL', 'NEQUAL'),
              ('nonassoc','GREATERE', 'GREATER', 'LOWERE', 'LOWER'),
              ('right', 'NOT'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'MULT', 'DIV', 'MOD'),
              ('right', 'UMINUS'),
              ('left', 'LPAR', 'RPAR'),
              )

def p_prog(p):
    """prog : listFuncs
    """
    p[0] = RoseTree('Prog', p[1])
        
def p_listFuncs(p):
    """listFuncs : funcHeader funcBody listFuncs
                 | funcHeader funcBody"""

    if p[1].children[0] != None and p[2][-1].children[0].get_type() != p[1].children[0]:
        raise SyntaxError(p.lineno(1),f"Invalid return type found for function {p[1].children[1]}. Expected type {p[1].children[0]} but found {p[2][-1].children[0].get_type()} instead.")
    
    p[1].add_child(p[2])
    if len(p) > 3:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_funcHeader(p):
    """funcHeader : FUNC VARNAME LPAR args RPAR output"""
    p.parser.scope.update(dict([(elem.children[1], elem) for elem in p[4]]))
    if p[2] in p.parser.functions:
        raise SyntaxError(p.lineno(1),f"Previous declaration of function {p[2]} found.")
    
    p[0] = RoseTree('func', [p[6], p[2], p[4]])

    p.parser.functions[p[2]] = p[0]

def p_funcBody(p):
    """funcBody : LCURLY funcCode RCURLY"""
    p[0] = p[2]
    p.parser.scope = {}

def p_return(p):
    """output : EQUAL GREATER type
              | 
    """
    
    if len(p) > 1:
        p[0] = p[3]
    else: 
        p[0] = None

def p_args(p):
    """ args : var listarg
             |
    """
    
    if len(p) > 1:
        if type(p[1].children[0]) == list:
            p[1].add_child(p[1].children[0][1])
            p[1].children[0] = p[1].children[0][0]
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_listarg(p):
    """listarg : COMMA var listarg
               |
    """
    
    if len(p) > 1:
        if type(p[2].children[0]) == list:
            p[2].add_child(p[2].children[0][1])
            p[2].children[0] = p[2].children[0][0]
            p[0] = [p[2]] + p[3]
        else:
            p[0] = [p[2]] + p[3]
    else: 
        p[0] = []

def p_funcCode(p):
    """funcCode : code RETURN retval"""
    p[0] = p[1] + p[3]

def p_code(p):
    """ code : line ENDLINE code
             | forLoop code
             | ifClause code
             |
    """
    if len(p) == 4:
        if p[1] != []:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = p[3]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else: 
        p[0] = []
    
def p_retval(p):
    """ retval : evaluation ENDLINE
               | ENDLINE
    """
    if len(p) == 2:
        p[0] = [RoseTree('ret', [])]
    else:   
        p[0] = [RoseTree('ret', [p[1]])]

def p_line(p):
    """ line : declaration
             | expr
             | print
             | read
             |
    """
    if len(p) > 1:
        p[0] = p[1]
    else: 
        p[0] = []

def p_print(p):
    """print : PRINT LPAR val RPAR"""

    if p[3].get_type() == DataType.STR:
        p[0] = RoseTree('print', [p[3]])
        return
    
    if p[3].type == 'call':
        p[0] = RoseTree('print', [p[3]])
        return

    if p[3].name() not in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Use of undeclared variable {p[3]}.")   
    
    p[0] = RoseTree('print', [p[3]])

def p_read(p):
    """read : READ LPAR val RPAR"""

    if p[3].get_type() == DataType.STR:
        raise SyntaxError(p.lineno(1),f"Illegal use of 'read' internal function.")   
    
    if p[3].name() not in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Use of undeclared variable {p[3]}.")   

    p[0] = RoseTree('read', [p[3]])    

def p_ifClause(p):
    """ifClause : IF evaluation LCURLY code RCURLY elseClause"""
    if p[2].children[0] != DataType.BOOL:
        raise SyntaxError(p.lineno(1),"Invalid expression found. Does not evaluate to 'bool'.")
    
    if p[6] != None:
        p[0] = RoseTree('if', [p[2], p[4], p[6]])
    else:
        p[0] = RoseTree('if', [p[2], p[4]])

def p_elseClause(p):
    """elseClause : ELSE LCURLY code RCURLY
                  | """
    if len(p) == 5:
        p[0] = p[3]
    else:
        p[0] = None

def p_forLoop(p):
    """forLoop : FOR forControl LCURLY code RCURLY"""
    if p[2][1].children[0] != DataType.BOOL:
        raise SyntaxError(p.lineno(1),"Invalid expression found. Does not evaluate to 'bool'.")
    
    p[0] = RoseTree('for', [p[2][0], p[2][1], p[2][2], p[4]])

def p_forControl(p):
    """forControl : forDec ENDLINE evaluation ENDLINE expr
                  | forDec ENDLINE evaluation ENDLINE
                  | ENDLINE evaluation ENDLINE expr
                  | ENDLINE evaluation ENDLINE
    """
    if len(p) == 6:
        p[0] = [p[1], p[3], p[5]]
    elif len(p) == 5:
        if p[1] == ';':
            p[0] = [None, p[2], p[4]]
        else:
            p[0] = [p[1], p[3], None]
    else:
        p[0] = [None, p[2], None]
 
def p_forDec(p):
    """forDec : var EQUAL evaluation"""

    if var := p.parser.scope.get(p[1].children[1]):
        if var.children[0] != p[3].children[0]: 
            raise SyntaxError(p.lineno(1),f"Mismatched types. Expected {var.children[0]} but got {p[3].children[0]} instead.")
        p[0] = RoseTree('atrib', [var.children[0], var.children[1], p[3]])
    else:
        if p[1].children[0] != None and p[1].children[0] != p[3].children[0]:
            raise SyntaxError(p.lineno(1),f"Mismatched types. Expected {p[1].children[0]} but got {p[3].children[0]} instead.")
        p[0] = RoseTree('init', [p[3].children[0], p[1].children[1], p[3].children[1]])
        p.parser.scope[p[1].children[1]] = p[0]

def p_call(p):
    """call : VARNAME LPAR funcArgs RPAR"""

    if func := p.parser.functions.get(p[1]):
        if len(func.children[2]) != len(p[3]):
            raise SyntaxError(p.lineno(1),f"Mismatched number of arguments provided at function call. Expected {len(func.children[2])} but got {len(p[3])}.")
        for idx in range(len(func.children[2])):
            if func.children[2][idx].children[0] != p[3][idx].children[0]:
                raise SyntaxError(p.lineno(1),f'''Mismatched type for argument {func.children[2][idx].children[1]} of function {func.children[1]}.
Expected {func.children[2][idx].children[0]} but got {p[3][idx].children[0]} instead.''')
        p[0] = RoseTree('call', [func.children[0], func.children[1], p[3]])
    else:
        raise SyntaxError(p.lineno(1),f'''Function call made with an undefined function.
If the function is present consider moving it's declaration to before the current function.''')

def p_funcArgs(p):
    """funcArgs : evaluation listfuncArgs
                 | 
    """
    if len(p) > 1:
        p[0] = [p[1]] + p[2]
    else: 
        p[0] = []

def p_listfuncArgs(p):
    """listfuncArgs : COMMA evaluation listfuncArgs
                    |
    """
    if len(p) > 1:
        p[0] = [p[2]] + p[3]
    else: 
        p[0] = []

def p_expr(p):
    """expr : call
            | leftVar EQUAL evaluation
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1].get_elem_type() != p[3].get_elem_type():
            raise SyntaxError(p.lineno(1),f"Mismatched types. Expected {p[1].get_elem_type()} but got {p[3].get_elem_type()} instead.")
        p[0] = RoseTree('atrib', [p[1].get_type(), p[1], p[3]])

def p_leftVar_list(p):
    """leftVar : accessList
    """
    p[0] = p[1]

def p_leftVar(p):
    """leftVar : VARNAME
    """
    if p[1] not in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Use of undeclared variable {p[1]}.")
    p[0] = RoseTree('var', [p.parser.scope[p[1]].children[0], p.parser.scope[p[1]].children[1]])

def p_evaluation1(p):
    """evaluation : MINUS evaluation %prec UMINUS
                  | NOT evaluation
    """
    if p[1] == '-':
        p[0] = RoseTree('neg', [None, p[2]])
    else:
        p[0] = RoseTree('not', [None, p[2]])
    error = p[0].validate_op()
    if error != 0:
        raise error

def p_evaluation0(p):
    """evaluation : LPAR evaluation RPAR
                  | val"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_evaluation(p):
    """evaluation : evaluation PLUS evaluation
                  | evaluation MINUS evaluation
                  | evaluation MULT evaluation
                  | evaluation DIV evaluation
                  | evaluation MOD evaluation
                  | evaluation AND evaluation
                  | evaluation OR evaluation
                  | evaluation LEQUAL evaluation
                  | evaluation NEQUAL evaluation
                  | evaluation GREATER evaluation
                  | evaluation GREATERE evaluation
                  | evaluation LOWER evaluation
                  | evaluation LOWERE evaluation
    """
    p[0] = RoseTree('BinOp', [None, p[2], p[1], p[3]])
    error = p[0].validate_op()

    if error != 0:
        raise error

def p_declaration_list(p):
    """declaration : LET var EQUAL listInit
    """
    if p[2].children[1] in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Redeclaration of variable {p[2].children[1]}")
    
    if len(p[2].children) == 1:
        raise SyntaxError(p.lineno(1),f"Mismatched data types. Expected {p[2].children[0]} but got 'array' instead.")

    line = 0
    if len(p[2].children[0][1]) == 3:
        line = p[2].children[0][1].pop(2)

    if p[4].children[1] == 0:
        if p[2].children[0][0] == DataType.STR:
            raise SyntaxError(p.lineno(1),f"Invalid initialization of variable {p[2].children[1]}. Value must not be empty.")
        p[0] = RoseTree('init', [DataType.LIST, p[2].children[1], [0], p[2].children[0][1][1], p[2].get_type()])
        p.parser.scope[p[2].children[1]] = p[0]
    else:
        if p[2].children[0][1] != None and p[2].children[0][1][1] != len(p[4].children[1]):
            raise SyntaxError(p.lineno(1),f"Mismatched sizes on {p[2].children[1]} declaration. Expected size {p[2].children[0][1][1]} but got {len(p[4].children[1])} instead.")
        p[0] = RoseTree('init', [DataType.LIST, p[2].children[1], p[4].children[1], len(p[4].children[1]), p[4].get_type()])
        scope = deepcopy(p[0])
        scope.add_child(line)
        p.parser.scope[p[2].children[1]] = scope

def p_declaration(p):
    """declaration : LET var EQUAL evaluation
    """

    if p[2].children[1] in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Redeclaration of variable {p[2].children[1]}.")
    

    if p[2].children[0] != None and p[2].children[0] != p[4].children[0]:
        raise SyntaxError(p.lineno(1),f"Mismatched data types. Expected '{p[2].children[0]}' but got '{p[4].children[0]}' instead.")

    p[0] = RoseTree('init', [p[4].children[0], p[2].children[1], p[4]])
    p.parser.scope[p[2].children[1]] = p[0]

def p_declaration_implicit(p):
    """declaration : LET var"""
    if p[2].children[1] in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Redeclaration of variable {p[2].children[1]}")

    if type(p[2].children[0]) == list:
        p[0] = RoseTree('init', [DataType.LIST, p[2].children[1], [0], p[2].children[0][1], p[2].children[0][0]])
    else:
        p[0] = RoseTree('init', [DataType.INT, p[2].children[1], 0])
    p.parser.scope[p[2].children[1]] = p[0]

def p_listInit(p):
    """ listInit : listList
                 | LBRA RBRA
    """

    if len(p) == 3:
        p[0] = RoseTree("val", [DataType.INT, 0])
    else:
        if type(p[1][0]) == list:
            flatten = [elem for line in p[1] for elem in line]
            diff = len(set(map(lambda x: len(x), p[1])))
        else:
            flatten = [elem for elem in p[1]]
            diff = 1
        if sum(map(lambda x: x.children[0], flatten)) // flatten[0].children[0] != len(flatten):
            raise SyntaxError(p.lineno(1),f"Array elements have different types.")
        if diff != 1:
            raise SyntaxError(p.lineno(1),f"Array elements have different sizes.")
        
        p[0] = RoseTree("val", [flatten[0].children[0], flatten])

def p_listList(p):
    """ listList : LBRA list2Deep RBRA 
                 | LBRA listElems RBRA
    """
    p[0] = p[2]

def p_list2Deep(p):
    """ list2Deep : list2Deep COMMA LBRA listElems RBRA
                  | LBRA listElems RBRA
    """
    if len(p) == 4:
        p[0] = [p[2]]
    else:
        p[0] = p[1] + [p[4]]

def p_listElems(p):
    """ listElems : listElems COMMA val
                  | val
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
        
def p_var(p):
    """var : VARNAME typeAtrib"""
    p[0] = RoseTree('var', [p[2], p[1]])

def p_typeAtrib(p):
    """typeAtrib : DDOT type
                 | 
    """
    if len(p) > 1:
        p[0] = p[2]
    else: 
        p[0] = None

def p_val_var(p):
    """val : VARNAME"""

    if p[1] not in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Use of undeclared variable {p[1]}.")

    if p.parser.scope[p[1]].get_type() == DataType.LIST:
        p[0] = RoseTree('valList', [p.parser.scope[p[1]].children[0], p[1], 0])
    else:
        p[0] = RoseTree('val', [p.parser.scope[p[1]].children[0], p[1]])

def p_val_list(p):
    """val : accessList
    """
    p[0] = p[1]

def p_val_call(p):
    """val : call
    """
    p[0] = p[1]

def p_val(p):
    """val : INTEGER
           | FLOATING
           | STRING
           | BOOLEAN
    """
    type = DataType.inferetype(p[1])
    p[0] = RoseTree('val', [type, p[1]])

def p_type(p):
    """type : INT
            | FLOAT
            | BOOL
            | STR
    """
    p[0] = DataType.datatype(p[1])

def p_type_flist(p):
    """type : flist
    """
    p[0] = [DataType.datatype(p[1][0]), p[1][1]]

def p_type_list(p):
    """type : list
    """
    p[0] = p[1]

def p_flist(p):
    """flist : LBRA type RBRA
    """
    if type(p[2]) != list:
        p[0] = ["list", p[2]] 
    else:
        p[0] = p[2] 

def p_list(p):
    """list : LBRA type COMMA INTEGER RBRA
    """
    if type(p[2]) != list:
        p[0] = [DataType.LIST,[p[2], p[4]]]
    else:
        p[0] = [DataType.LIST,[p[2][1][0], p[4] * p[2][1][1]]]

def p_accessList(p):
    """accessList : VARNAME listIndex listIndex
                  | VARNAME listIndex"""

    if p[1] not in p.parser.scope:
        raise SyntaxError(p.lineno(1),f"Use of undeclared variable '{p[1]}'.")
    
    if p.parser.scope[p[1]].get_type() != DataType.LIST:
        raise SyntaxError(p.lineno(1),f"Token '{p.parser.scope[p[1]].children[1]}' of type '{p.parser.scope[p[1]].children[0]}' doesn't allow indexing.")

    if len(p) == 4:
        p[0] = RoseTree('valList', 
                        [p.parser.scope[p[1]].children[0], 
                         p[1],
                         RoseTree('BinOp', 
                            [DataType.INT, 
                            '+', 
                            RoseTree('BinOp', 
                                     [DataType.INT,
                                      '*', 
                                      RoseTree('val',[DataType.INT, p.parser.scope[p[1]].children[-1]]), 
                                      p[2]
                                     ]),
                            p[3]
                            ]), 
                         p.parser.scope[p[1]].get_elem_type()]
                         )
    else:
        if len(p.parser.scope[p[1]].children) > 5:
            p[0] = RoseTree('valList', [p.parser.scope[p[1]].children[0], p[1], p[2], p.parser.scope[p[1]].get_elem_type()])
        else:
            p[0] = RoseTree('valList', [p.parser.scope[p[1]].children[0], p[1], p[2], p.parser.scope[p[1]].get_elem_type()])

def p_listIndex(p):
    """listIndex : LBRA evaluation RBRA
    """
    if p[2].children[0] != DataType.INT:
        raise SyntaxError(p.lineno(1),f"Cannot use '{p[2].children[0]}' to index 'array'. Consider using 'int' instead.")
    p[0] = p[2]

def p_error(p):
    raise SyntaxError(p.lineno, f"Found unexpected token '{p.value}'. Possible ';' missing at previous end of line.")

parser = yacc.yacc()

parser.scope = {}
parser.functions = {}

if __name__ == '__main__':
    
    examples = ['sum', 'array', 'control_flow', 'function_call', 'iostream', 'fibonacciMemo']
    
    for example in [examples[0]]:

        data = open('../examples/code/' + example + '.jacll').read()

        out = parser.parse(data, lexer= lexer, debug= False)

        parser.scope = {}
        parser.functions = {}

        file_out = open("../testing/" + example + "_parse_tree.txt", "w")
        file_out.write(out.__repr__())
        file_out.close()
