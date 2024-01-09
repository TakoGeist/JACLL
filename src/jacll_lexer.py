import ply.lex as lex

reserved = {
    'let' : 'LET',
    'for' : 'FOR',
    'if' : 'IF',
    'else' : 'ELSE',
    'func' : 'FUNC',
    'int' : 'INT',
    'float' : 'FLOAT',
    'bool' : 'BOOL',
    'str' : 'STR',
    'return' : 'RETURN',
    'print' : 'PRINT',
    'read' : 'READ',
}

tokens = ['STRING', 'COMMENT', 'ENDLINE', 'EQUAL', 'VARNAME', 'LPAR', 'RPAR', 
          'LBRA', 'RBRA', 'LCURLY', 'RCURLY', 'DDOT', 'COMMA', 'INTEGER','FLOATING', 
          'BOOLEAN', 'PLUS', 'MINUS', 'MULT', 'DIV', 'POW', 'AND', 'OR', 'LEQUAL',
          'NEQUAL', 'NOT', 'GREATER', 'GREATERE', 'LOWER', 'LOWERE', 'MOD'
          ] + list(reserved.values())

t_STRING = r'\"([^"\\]|\\.)*\"' 
t_PLUS = r'\+'
t_MINUS = r'\-'
t_POW = r'\*\*'
t_MULT = r'\*'
t_MOD = r'\%'
t_DIV = r'\/'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_LEQUAL = r'\=\='
t_NEQUAL = r'\!\='
t_NOT = r'\!'
t_GREATERE = r'\>\='
t_GREATER = r'\>'
t_LOWERE = r'\<\='
t_LOWER = r'\<'
t_EQUAL = r'\='
t_ENDLINE = r'\;'
t_DDOT = r'\:'
t_COMMA = r'\,'

def t_BOOLEAN(t):
    r'true|false'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_LPAR(t):
    r'\('
    lexer.stack.append(t)
    return t

def t_LBRA(t):
    r'\['
    lexer.stack.append(t)
    return t

def t_LCURLY(t):
    r'\{'
    lexer.stack.append(t)
    return t

def t_RPAR(t):
    r'\)'
    if (len(lexer.stack) != 0):
        token = lexer.stack.pop(-1)
        if (token.value != '('):
            raise SyntaxError(f'Found \')\' at line {t.lineno} but was never open')
    else:
        raise SyntaxError(f'Found \')\' at line {t.lineno} but was never open')
    return t

def t_RBRA(t):
    r'\]'
    if (len(lexer.stack) != 0):
        token = lexer.stack.pop(-1)
        if (token.value != '['):
            raise SyntaxError(f'Found \']\' at line {t.lineno} but was never open')
    else:
        raise SyntaxError(f'Found \']\' at line {t.lineno} but was never open')
    return t

def t_RCURLY(t):
    r'\}'
    if (len(lexer.stack) != 0):
        token = lexer.stack.pop(-1)
        if (token.value != '{'):
            raise SyntaxError(f'Found \'}}\' at line {t.lineno} but was never open')
    else:
        raise SyntaxError(f'Found \'}}\' at line {t.lineno} but was never open')
    return t

def t_FLOATING(t):
    r'(\d+\.\d*|\d*\.\d+)'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_VARNAME(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'VARNAME')
    return t

def t_COMMENT(t):
    r'((\/\/.*)|(\/\*([^\*]*|\*|[^\/])*\*\/))'
    t.lexer.lineno += t.value.count('\n') 
    pass

def t_eof(t):
    if (len(t.lexer.stack) != 0):
        raise SyntaxError(f'\'{t.lexer.stack[0].value}\' at line {t.lexer.stack[0].lineno} was never closed')
    return None


def t_error(t):
    raise SyntaxError(f"Illegal character \'{t.value[0]}\' at position {t.lexpos}.")
    

t_ignore = ' \t'

lexer = lex.lex()

lexer.stack = []

if __name__ == '__main__':

    example = 'function_call'

    data = open('../examples/' + example + '.jacll').read()

    out = ""

    lexer.input(data)

    while tok := lexer.token():
        out += str(tok.value) + ' '
        if (tok.value in [';','{','}']):
            out += '\n'


    file_out = open("../testing/" + example + "_lexer_out.txt", "w")

    file_out.write(out)
