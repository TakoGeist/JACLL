import ply.lex as lex

reserved = {
    'let' : 'LET',
    'for' : 'FOR',
    'if' : 'IF',
    'else' : 'ELSE',
    'func' : 'FUNC',
    'mut' : 'MUT',
    'i32' : 'I32',
    'i64' : 'I64',
    'f32' : 'F32',
    'f64' : 'F64',
    'bool' : 'BOOL',
    'return' : 'RETURN',
    'print' : 'PRINT',
}

tokens = ['STRING', 'COMMENT', 'ENDLINE', 'EQUAL', 'ALGCODE', 'LOGCODE', 'VARNAME', 'LPAR',
          'RPAR', 'LBRA', 'RBRA', 'LCURLY', 'RCURLY', 'DDOT', 'COMMA', 'INT', 'FLOAT'] + list(reserved.values())

t_STRING = r'\"([^"\\]|\\.)*\"' 
t_ALGCODE = r'(\+|\-|\*\*|\*|\/)'
t_LOGCODE = r'(!|~|\&\&|\&|\^|(\|\|)|(\|)|(<=)|(>=)|<|>)'
t_ENDLINE = r';'
t_LPAR = r'\('
t_RPAR = r'\)'
t_LBRA = r'\['
t_RBRA = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_DDOT = r'\:'
t_COMMA = r'\,'
t_INT = r'\d+'

def t_FLOAT(t):
    r'(\d+\.\d*|\d*\.\d+)'
    return t

def t_VARNAME(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'VARNAME')
    return t

def t_EQUAL(t):
    r'='
    return t

def t_COMMENT(_):
    r'((\/\/.*)|(\/\*([^\*]*|\*|[^\/])*\*\/))'
    pass

def t_error(t):
    raise SyntaxError(f"Illegal character \'{t.value[0]}\' at position {t.lexpos}.")
    

t_ignore = ' \t\n'

lexer = lex.lex()




