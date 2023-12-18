import ply.yacc as yacc
from jacll_lexer import tokens

precedence = (
              ('nonassoc','GREATERE', 'GREATER', 'LOWERE', 
                          'LOWER', 'LEQUAL', 'NEQUAL'),
              ('left', 'AND', 'OR'),
              ('right', 'NOT'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'MULT', 'DIV', 'MOD'),
              ('right', 'POW'),
              ('right', 'UMINUS'),
              ('left', 'LPAR', 'RPAR'),
              )

def p_prog(p):
    """prog : func prog
            | func
    """
    if len(p) > 2:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1]

def p_func(p):
    'func : FUNC VARNAME LPAR args RPAR output LCURLY funcCode RCURLY'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5] + " " + p[6] + " " + p[7] + " " + p[8] + " " + p[9]

def p_return(p):
    """output : EQUAL GREATER type
              | 
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""    

def p_args(p):
    """ args : var listarg
             |
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2]
    else: 
        p[0] = ""

def p_listarg(p):
    """listarg : COMMA var listarg
               |
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""

def p_funcCode(p):
    'funcCode : code RETURN retval'
    p[0] = p[1] + " " + p[2] + " " + p[3]

def p_code(p):
    """ code : line ENDLINE code
             | forLoop code
             | ifClause code
             |
    """
    if len(p) == 4:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    elif len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else: 
        p[0] = ""
    
def p_retval(p):
    """ retval : evaluation ENDLINE
               | ENDLINE
    """
    if len(p) == 2:
        p[0] = p[1]
    else:   
        p[0] = p[1] + " " + p[2]

def p_line(p):
    """ line : declaration
             | expr
             | print
             |
    """
    if len(p) > 1:
        p[0] = p[1]
    else: 
        p[0] = ""

def p_print(p):
    'print : PRINT LPAR val RPAR'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_ifClause(p):
    'ifClause : IF evaluation LCURLY code RCURLY elseClause'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5] + " " + p[6]

def p_elseClause(p):
    """elseClause : ELSE LCURLY code RCURLY
                  |                
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else: 
        p[0] = ""

def p_forLoop(p):
    'forLoop : FOR forControl LCURLY code RCURLY'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

def p_forControl(p):
    """forControl : forDec ENDLINE evaluation ENDLINE expr
                  | forDec ENDLINE evaluation ENDLINE
                  | ENDLINE evaluation ENDLINE expr
                  | ENDLINE evaluation ENDLINE
    """
    if len(p) == 6:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]
    elif len(p) == 5:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3]

 
def p_forDec(p):
    'forDec : var EQUAL evaluation'
    p[0] = p[1] + " " + p[2] + " " + p[3]

def p_call(p):
    'call : VARNAME LPAR funcArgs RPAR'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_funcArgs(p):
    """funcArgs : val listfuncArgs
                 | 
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""

def p_listfuncArgs(p):
    """listfuncArgs : COMMA val listfuncArgs
                    |
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""

def p_expr(p):
    """expr : call
            | leftVar EQUAL evaluation
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3]

def p_leftVar(p):
    """leftVar : VARNAME LBRA INT RBRA
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
                   | LET MUT var EQUAL evaluation
                   | LET var EQUAL listInit
                   | LET MUT var EQUAL listInit
                   """
    if len(p) == 5:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

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
    'var : VARNAME typeAtrib'
    p[0] = p[1] + " " + p[2]

def p_typeAtrib(p):
    """typeAtrib : DDOT type
                 | 
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2]
    else: 
        p[0] = ""

def p_val(p):
    """val : INT
           | FLOAT
           | STRING
           | BOOLEAN
           | VARNAME
           | acessList
           | call
    """
    p[0] = p[1]

def p_type(p):
    """type : I32
            | I64
            | F32
            | F64
            | BOOL
            | STR
            | list
    """
    p[0] = p[1]

def p_list(p):
    """list : LBRA type COMMA INT RBRA
            | LBRA list COMMA INT RBRA
    """
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

def p_acessList(p):
    'acessList : VARNAME listLists'
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
              | INT
    """
    p[0] = p[1]

def p_error(p):
    print(p)
    raise SyntaxError()

if __name__ == '__main__':
    parser = yacc.yacc()

    example = "array"

    data = open("../examples/" + example + ".jacll").read()

    out = parser.parse(data)

    file_out = open("../testing/" + example + "_parse_out.txt", "w")

    file_out.write(out)
