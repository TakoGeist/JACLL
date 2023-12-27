from utils import *
import ply.yacc as yacc
from jacll_lexer import tokens

precedence = (
              ('left', 'OR'),
              ('left', 'AND'),
              ('nonassoc', 'LEQUAL', 'NEQUAL'),
              ('nonassoc','GREATERE', 'GREATER', 'LOWERE', 'LOWER'),
              ('right', 'NOT'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'MULT', 'DIV', 'MOD'),
              ('right', 'UMINUS'),
              ('right', 'POW'),
              ('left', 'LPAR', 'RPAR'),
              )

def p_prog(p):
    """prog : listFuncs
    """
    p[0] = RoseTree('prog', Prog('prog'), p[1])
        
def p_listFuncs(p):
    """listFuncs : func listFuncs
                 | func"""
    if p[1].node.name in p.parser.functions:
        raise SyntaxError(f"Previous declaration of function {p[1].name} found.")
    p.parser.functions[p[1].node.name] = p[1].node
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_func(p):
    """func : FUNC VARNAME LPAR args RPAR output LCURLY funcCode RCURLY"""
    p.parser.scope.update(dict(p[4]))
    p[0] = RoseTree('func', 
                    Func(p[2], p[4], p[6]),
                    p[8])
    for i in p[0].node.scope:
        p.parser.scope.pop(i)
    print(p[0])

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
        p[0] = [p[1]] + p[2]
    else: 
        p[0] = []

def p_listarg(p):
    """listarg : COMMA var listarg
               |
    """
    if len(p) > 1:
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
        p[0] = [p[1]] + p[3]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else: 
        p[0] = []
    
def p_retval(p):
    """ retval : evaluation ENDLINE
               | ENDLINE
    """
    if len(p) == 2:
        p[0] = []
    else:   
        p[0] = [p[1]]

def p_line(p):
    """ line : declaration
             | expr
             | print
             |
    """
    if len(p) > 1:
        p[0] = p[1]
    else: 
        p[0] = []

def p_print(p):
    """print : PRINT LPAR val RPAR"""
    p[0] = Print(p[3])

def p_ifClause(p):
    """ifClause : IF evaluation LCURLY code RCURLY ELSE LCURLY code RCURLY
                | IF evaluation LCURLY code RCURLY"""
    if len(p) > 6:
        p[0] = IfClause(p[1], p[3], p[8])
    else:
        p[0] = IfClause(p[1], p[2])

def p_forLoop(p):
    """forLoop : FOR forControl LCURLY code RCURLY"""
    p[0] = RoseTree('for', ForLoop(p[2][1], p[2][0], p[2][2]), p[4])

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
    if var := p.parser.scope.get(p[1].name):
        if p[3].type != var.type:
            raise SyntaxError(f"Mismatched types. Expected {p[1].type} but got {p[3].type} instead.")
        var.value = p[3].value
        p[0] = var
        p.parse.scope[p[1][0]] = var
    else:
        if p[1].type == None:
            p[1].type = p[3].type
        if p[1].type not in [DataType.INT, DataType.FLOAT]:
            raise SyntaxError("Illegal type used. Consider switching to integer or float.")
        p[0] = Var(p[1].name, p[1].type, p[3].value,True)

def p_call(p):
    """call : VARNAME LPAR funcArgs RPAR"""
    if func := p.parser.functions.get(p[1]):
        if len(func.args) != len(p[3]):
            raise SyntaxError(f"""Mismatched number of arguments provided at function call. 
Expected {len(func.args)} but got {len(p[3])}.""")
        for idx in range(len(func.args)):
            if func.args[idx].type != p[3][idx].type:
                raise SyntaxError(f"""Mismatched type for argument {func.args[idx].name} of function {func.name}.
Expected {func.args[idx].type} but got {p[3][idx].type} instead.""")
        p[0] = Call(p[1], p[3], func.output)
    else:
        raise SyntaxError(f"""Function call made with an undefined function.
If the function is present consider moving to before the current function.""")

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
        p[0] = RoseTree('expr', None, [p[1], p[3]])

def p_leftVar(p):
    """leftVar : VARNAME LBRA INTEGER RBRA
               | VARNAME
    """
    if p[1] not in p.parser.scope:
        raise SyntaxError(f"Use of undeclared variable {p[1]}.")
    var = p.parser.scope.get(p[1]).__copy__()
    var.value = None
    if len(p) == 5:
        if var.type != DataType.LIST:
            raise SyntaxError(f"{var.name} is not an array.")
        var.index = p[3]
    p[0] = var

def p_evaluation1(p):
    """evaluation : MINUS evaluation %prec UMINUS
                  | NOT evaluation
    """
    if p[1] == '-':
        p[1] = RoseTree('neg', None, [p[2]])
    else:
        p[1] = RoseTree('not', None, [p[2]])

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
                  | evaluation POW evaluation
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
    p[0] = RoseTree('BinOP', p[2], [p[1], p[3]])

def p_declaration_implicit(p):
    """declaration : LET var"""
    if p[2].name in p.parser.scope:
        raise SyntaxError(f"Redeclaration of variable {p[2].name}")
    if p[2].type == DataType.LIST:
        p[0] = Var(p[2].name, p[2].type, [0]*p[2].row, _row=p[2].row)
    else:
        p[0] = Var(p[2].name, p[2].type, 0)
    p.parser.scope[p[2].name] = p[0]

def p_declaration(p):
    """declaration : LET var EQUAL evaluation
                   | LET var EQUAL listInit
                   """
    if p[2].name in p.parser.scope:
        raise SyntaxError(f"Redeclaration of variable {p[2].name}")
    if p[2].type == DataType.LIST:
        if p[4].type != DataType.LIST:
            raise SyntaxError(f"Mismatched data types. Expected LIST but got {p[4].type} instead.")
        if p[2].row != p[4].row and p[4].row != 1 and p[4].row != 0:
            raise SyntaxError(f"Mismatched size on array declaration. Expected {p[2].row} but got {p[4].row} instead.")
        if p[4].column == None:
            if p[4].row == 1:
                p[0] = Var(p[2].name, p[2].type, p[4].value, _row= p[2].row)
            else:    
                p[0] = Var(p[2].name, p[2].type, p[4].value, _row= p[2].row)
        else:
            p[0] = Var(p[2].name, p[2].type, p[4].value, _row= p[2].row, _column= p[2]._column)


    else:
        p[0] = Var(p[2].name, p[2].type, p[4])
    p.parser.scope[p[2].name] = p[0]



    #if p[2].name in p.parser.scope:
    #    raise SyntaxError(f"Redeclaration of variable {p[2].name}")
    #if p[2].type == DataType.LIST:
    #    if p[2].row != p[4].row and p[4].row != 1 and p[4].row != 0:
    #        raise SyntaxError(f"Mismatched size on array declaration. Expected {p[2].row} but got {p[4].row} instead.")
    #    if p[4].row == 1:
    #        p[0] = Var(p[2].name, p[2].type, p[4].value*p[2].row, _row= p[2].row)
    #    else:    
    #        p[0] = Var(p[2].name, p[2].type, p[4].value, _row= p[2].row)
    #else:
    #    p[0] = Var(p[2].name, p[2].type, p[4])
    #p.parser.scope[p[2].name] = p[0]

def p_listInit(p):
    """ listInit : LBRA listElems RBRA
                 | LBRA RBRA
    """
    if len(p) == 3:
        p[0] = Var(None, DataType.LIST, 0)
    else:
        e1 = p[3][0]
        for i in range(len(p[3])):
            if type(p[3][i]) != type(e1):
                raise SyntaxError(f"Array elements have different types.")
            elif type(e1) == list:
                if len(e1) != len(p[3][i]):
                    raise SyntaxError(f"Array elements have different sizes.")
            else:
                for j in range(1,len(e1)):
                    if type(e1[0]) != type(e1[j]) or type(e1[0]) != type(p[3][i][j]):
                        raise SyntaxError(f"Array elements have different types.")
                    
        column = len(e1) if type(e1) == type([]) else None
        p[0] = Var(None, DataType.LIST, p[2], _row= len(p[2]), _column = column)

def p_listElems(p):
    """ listElems : listInit COMMA listElems
                  | val COMMA listElems
                  | val
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]
        
def p_var(p):
    """var : VARNAME typeAtrib"""
    p[0] = Var(p[1], p[2], None)

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
        raise SyntaxError(f"Use of undeclared variable {p[1]}.")
    p[0] = p.parser.scope[p[1]].__copy__()

def p_val(p):
    """val : INTEGER
           | FLOATING
           | STRING
           | BOOLEAN
           | acessList
           | call
    """
    type = DataType.inferetype(p[1], p.parser.scope)
    p[0] = Var(None, type, p[1])

def p_type(p):
    """type : INT
            | FLOAT
            | BOOL
            | STR
            | list
            | flist
    """
    p[0] = DataType.datatype(p[1])

def p_flist(p):
    """flist : LBRA type RBRA flist
             | LBRA type RBRA
    """

    p[0] = "list"

def p_list(p):
    """list : LBRA type COMMA INTEGER RBRA
            | LBRA list COMMA INTEGER RBRA
    """
    p[0] = "list"

def p_acessList(p):
    """acessList : VARNAME listIndex listIndex
                 | VARNAME listIndex"""
    if var := p.parser.scope.get(p[1]):
        if var.type != DataType.LIST:
            raise SyntaxError(f"{var.name} is not an array.")
        p[0] = var.__copy__()
        if len(p) == 3:
            if var.column != None:
                p[0].column = None
            p[0].value = p[0].value[p[2]]
            p[0].index = p[2]
        else:
            if var.column == None:
                raise SyntaxError(f"Illegal indexing. Variable {p[1]}{p[2]} is not an array.")   
            p[0].index = RoseTree('BinOp',
                                  '+',
                                  [RoseTree(
                                      'BinOp', 
                                      '*',
                                      [p[2], p[0].row]),
                                  p[3]])
    else:
        raise SyntaxError(f"Use of undeclared variable {p[1]}")

def p_listIndex(p):
    """listIndex : LBRA index RBRA
    """
    p[0] = p[2]

def p_index_var(p):
    """ index : VARNAME
    """
    if var := p.parser.scope.get(p[1]):
        p[0] = var.__copy__()
    else: 
        raise SyntaxError(f"Use of undeclared variable {p[1]}.")

def p_index_int(p):
    """ index : INTEGER
    """
    p[0] = Var(None, DataType.INT, p[1])

def p_error(p):
    print(p)
    raise SyntaxError()

parser = yacc.yacc()

parser.scope = {}
parser.functions = {}

if __name__ == '__main__':

    example = 'sum'

    data = open('../examples/' + example + '.jacll').read()

    out = parser.parse(data)

    # print(out)

    file_out = open("../testing/" + example + "_parse_tree.txt", "w")

    file_out.write(out.__str__())
