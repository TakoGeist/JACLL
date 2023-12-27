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
    if p[1].name in p.parser.functions:
        raise SyntaxError(f"Previous declaration of function {p[1].name} found.")
    p.parser.functions[p[1].name] = p[1]
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_func(p):
    'func : FUNC VARNAME LPAR args RPAR output LCURLY funcCode RCURLY'
    p.parser.scope.update(dict(p[4]))
    p[0] = RoseTree('func', 
                    Func(p[2], p[4], p[6]),
                    p[8])

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
    if var := p.parser.scope.get(p[1][0]):
        if p[3].type != var.type:
            raise SyntaxError(f"Mismatched types. Expected {p[1].type} but got {p[3].type} instead.")
        var.value = p[3].value
        p[0] = var
        p.parse.scope[p[1][0]] = var
    else:
        if p[1][1] == None:
            p[1][1] = p[3].type
        if p[1][1] not in [DataType.INT, DataType.FLOAT]:
            raise SyntaxError("Illegal type used. Consider switching to integer or float.")
        p[0] = Var(p[1][0], p[1][1], p[3].value,True)

def p_call(p):
    """call : VARNAME LPAR funcArgs RPAR"""
    if func := p.parser.functions.get(p[1]):
        if len(func.args) != len(p[3]):
            raise SyntaxError(f"""Mismatched number of arguments provided at function call. 
Expected {len(func.args)} but got {len(p[3])}.""")
        for idx in range(len(func.args)):
            if func.args[idx].type != p[3][idx].type:
                raise SyntaxError(f"Mismatched type for argument {func.args[idx].name} of function {func.name}.
Expected {func.args[idx].type} but got {p[3][idx].type} instead.")
        p[0] = Call(p[1], p[3], func.output)
    else:
        raise SyntaxError(f"Function call made with an undefined function.
If the function is present consider moving to before the current function.")

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
        p[0] = p[1] + " " + p[2] + " " + p[3]

def p_leftVar(p):
    """leftVar : VARNAME LBRA INTEGER RBRA
               | VARNAME
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_evaluation(p):
    """evaluation : MINUS evaluation %prec UMINUS
                  | LPAR evaluation RPAR
                  | evaluation PLUS evaluation
                  | evaluation MINUS evaluation
                  | evaluation MULT evaluation
                  | evaluation DIV evaluation
                  | evaluation POW evaluation
                  | evaluation MOD evaluation
                  | evaluation AND evaluation
                  | evaluation OR evaluation
                  | evaluation LEQUAL evaluation
                  | evaluation NEQUAL evaluation
                  | NOT evaluation
                  | evaluation GREATER evaluation
                  | evaluation GREATERE evaluation
                  | evaluation LOWER evaluation
                  | evaluation LOWERE evaluation
                  | val
    """
    if len(p) == 4:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    elif len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1]

def p_declaration(p):
    """declaration : LET var EQUAL evaluation
                   | LET var EQUAL listInit
                   """
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_listInit(p):
    """ listInit : LBRA listElems RBRA
                 | LBRA RBRA 
    """
    if len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3]

def p_listElems(p):
    """ listElems : val COMMA listElems
                  | val
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3]
        
def p_var(p):
    """var : VARNAME typeAtrib"""
    p[0] = Var(p[1], DataType.datatype(p[2]), None, False)

def p_typeAtrib(p):
    """typeAtrib : DDOT type
                 | 
    """
    if len(p) > 1:
        p[0] = DataType.datatype(p[2])
    else: 
        p[0] = None

def p_val(p):
    """val : INTEGER
           | FLOATING
           | STRING
           | BOOLEAN
           | VARNAME
           | acessList
           | call
    """
    p[0] = p[1]

def p_type(p):
    """type : INT
            | FLOAT
            | BOOL
            | STR
            | list
            | flist
    """
    p[0] = p[1]

def p_flist(p):
    """flist : LBRA type RBRA flist
             | LBRA type RBRA
    """

    if len(p) == 4:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    

def p_list(p):
    """list : LBRA type COMMA INTEGER RBRA
            | LBRA list COMMA INTEGER RBRA
    """
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

def p_acessList(p):
    """acessList : VARNAME listLists"""
    p[0] = p[1] + " " + p[2]

def p_listLists(p):
    """listLists : LBRA index RBRA listLists
                 | LBRA index RBRA
    """
    if len(p) == 4:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_index(p):
    """ index : VARNAME
              | INTEGER
    """
    p[0] = p[1]

def p_error(p):
    print(p)
    raise SyntaxError()

parser = yacc.yacc()

parser.scope = {}
parser.functions = {}

if __name__ == '__main__':

    example = "function_call"

    data = open("../examples/" + example + ".jacll").read()

    out = parser.parse(data)

    print(out)

    # file_out = open("../testing/" + example + "_parse_out.txt", "w")

    # file_out.write(out)
