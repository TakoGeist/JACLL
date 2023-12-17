import ply.yacc as yacc
from jacll_lexer import tokens

def p_prog(p):
    """prog : func prog
            | func
            """
    if len(p) > 2:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1]

def p_func(p):
    'func : FUNC VARNAME LPAR args RPAR LCURLY func_code return RCURLY'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5] + " " + p[6] + " " + p[7] + " " + p[8] + " " + p[9]

def p_return(p):
    """return : EQUAL LOGCODE type
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

def p_func_code(p):
    'func_code : code RETURN retval ENDLINE'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_code(p):
    """ code : line ENDLINE code
             |
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""
    
def p_retval(p):
    """ retval : VARNAME
               |
    """
    if len(p) > 1:
        p[0] = p[1]
    else: 
        p[0] = ""

def p_line(p):
    """ line : declaration
             | expr
             | if_clause
             | for_loop
             | print
             |
    """
    if len(p) > 1:
        p[0] = p[1]
    else: 
        p[0] = ""

def p_print(p):
    "print : PRINT LPAR val RPAR"
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_if_clause(p):
    'if_clause : IF eval LCURLY code RCURLY else_clause'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5] + " " + p[6]

def p_else_clause(p):
    """else_clause : ELSE LCURLY code RCURLY
                   |                
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else: 
        p[0] = ""

def p_for_loop(p):
    'for_loop : FOR for_control LCURLY code RCURLY'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

def p_for_control(p):
    """for_control : for_dec ENDLINE eval ENDLINE expr
                   | for_dec ENDLINE eval ENDLINE
                   | ENDLINE eval ENDLINE expr
                   | ENDLINE eval ENDLINE
    """
    if len(p) == 6:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]
    elif len(p) == 5:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3]
        
def p_for_dec(p):
    'for_dec : var EQUAL val'
    p[0] = p[1] + " " + p[2] + " " + p[3]

def p_eval(p):
    """eval : val LOGCODE val
            | LOGCODE BOOL
            | call
    """
    if len(p) == 4:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    elif len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1]

def p_call(p):
    'call : VARNAME LPAR func_args RPAR'
    p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]

def p_func_args(p):
    """func_args : val listfunc_args
                 | 
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""

def p_listfunc_args(p):
    """listfunc_args : COMMA val listfunc_args
                     |
    """
    if len(p) > 1:
        p[0] = p[1] + " " + p[2] + " " + p[3]
    else: 
        p[0] = ""

def p_expr(p):
    """expr : call
            | leftVar EQUAL val 
            | leftVar EQUAL algebra 
            | leftVar EQUAL eval
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

def p_algebra(p):
    'algebra : val ALGCODE val'
    p[0] = p[1] + " " + p[2] + " " + p[3]

def p_declaration(p):
    """declaration : LET var EQUAL val
                   | LET MUT var EQUAL val"""
    #for i in range(1,len(p)):
    #    p[0] + " " += p[i]
    if len(p) == 5:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + p[4] + " " + p[5]

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

if __name__ == '__main__':
    parser = yacc.yacc()

    example = "array"

    data = open("../examples/" + example + ".jacll").read()

    out = parser.parse(data)

    file_out = open("../testing/" + example + "_parse_out.txt", "w")

    file_out.write(out)


