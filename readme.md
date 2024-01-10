# JACLL - Just another C Like language

Simple compiled language designed to work with the instruction set of [EWVM virtual machine](https://ewvm.epl.di.uminho.pt/).

Constructed with the use of PLY python module.

The language is processed by a tokenizer made with PLY's lex module, the parsing is done with the use of PLY's yacc module which gives the programs AST. Finally the AST is processed and transformed in [EWVM Virtual Machine](https://ewvm.epl.di.uminho.pt/) assembly.

## Utilization
To compile a file simply run *'jacll.py'* script with a file to compile and a file to output, alternatively it can be used without an output file to write to *stdout* or without any to use redirected input and output (read from *stdin* and write to *stdout*). Any path provided should be relative to current work directory.

ie. >$ py jacll.py < input_file.jacll > output_file.txt

## Grammar Rules - BNF
```
NT = { BOOL, LEQUAL, VARNAME, INTEGER, FOR, DIV, GREATER, READ, IF, GREATERE,
       ENDLINE, PRINT, NEQUAL, STR, LOWER, EQUAL, INT, OR, LOWERE, FUNC, MOD, 
       RPAR, COMMA, LBRA, DDOT, MINUS, ELSE, NOT, PLUS, RCURLY, BOOLEAN, FLOAT,
       LPAR, AND, LET, MULT, RBRA, RETURN, STRING, LCURLY, FLOATING }


T = { prog, listFuncs, funcHeader, funcBody, output, args, listarg, funcCode,
      code, retval, line, print, read, ifClause, elseClause, forLoop, forControl, 
      forDec, call, funcArgs, listfuncArgs, expr, leftVar, evaluation, declaration, 
      listInit, listList, list2Deep, listElems, var, typeAtrib, val, type, flist,
      list, accessList, listIndex }


p1: prog : listFuncs
p2: listFuncs : funcHeader funcBody listFuncs
p3:           | funcHeader funcBody
p4: funcHeader : FUNC VARNAME LPAR args RPAR output
p5: funcBody : LCURLY funcCode RCURLY
p6: output : EQUAL GREATER type
p7:        | ε
p8: args : var listarg
p9:      | ε
p10: listarg : COMMA var listarg
p11:         | ε
p12: funcCode : code RETURN retval
p13: code : line ENDLINE code
p14:      | forLoop code
p15:      | ifClause code
p16:      | ε
p17: retval : evaluation ENDLINE
p18:        | ENDLINE
p19: line : declaration
p20:      | expr
p21:      | print
p22:      | read
p23:      | ε
p24: print : PRINT LPAR val RPAR
p25: read : READ LPAR val RPAR
p26: ifClause : IF evaluation LCURLY code RCURLY elseClause
p27: elseClause : ELSE LCURLY code RCURLY
p28:            | ε
p29: forLoop : FOR forControl LCURLY code RCURLY
p30: forControl : forDec ENDLINE evaluation ENDLINE expr
p31:            | forDec ENDLINE evaluation ENDLINE
p32:            | ENDLINE evaluation ENDLINE expr
p33:            | ENDLINE evaluation ENDLINE
p34: forDec : var EQUAL evaluation
p35: call : VARNAME LPAR funcArgs RPAR
p36: funcArgs : evaluation listfuncArgs
p37:          | ε
p38: listfuncArgs : COMMA evaluation listfuncArgs
p39:              | ε
p40: expr : call
p41:      | leftVar EQUAL evaluation
p42: leftVar : accessList
p43:         | VARNAME
p44: evaluation : MINUS evaluation 
p45:            | NOT evaluation
p46:            | LPAR evaluation RPAR
p47:            | val
p48:            | evaluation PLUS evaluation
p49:            | evaluation MINUS evaluation
p50:            | evaluation MULT evaluation
p51:            | evaluation DIV evaluation
p52:            | evaluation MOD evaluation
p53:            | evaluation AND evaluation
p54:            | evaluation OR evaluation
p55:            | evaluation LEQUAL evaluation
p56:            | evaluation NEQUAL evaluation
p57:            | evaluation GREATER evaluation
p58:            | evaluation GREATERE evaluation
p59:            | evaluation LOWER evaluation
p60:            | evaluation LOWERE evaluation
p61: declaration : LET var EQUAL listInit
p62:             | LET var EQUAL evaluation
p63:             | LET var
p64: listInit : listList
p65:          | LBRA RBRA
p66: listList : LBRA list2Deep RBRA
p67:          | LBRA listElems RBRA
p68: list2Deep : list2Deep COMMA LBRA listElems RBRA
p69:           | LBRA listElems RBRA
p70: listElems : listElems COMMA val
p71:           | val
p72: var : VARNAME typeAtrib
p73: typeAtrib : DDOT type
p74:           | ε
p75: val : VARNAME
p76:     | accessList
p77:     | call
p78:     | INTEGER
p79:     | FLOATING
p80:     | STRING
p81:     | BOOLEAN
p82: type : INT
p83:      | FLOAT
p84:      | BOOL
p85:      | STR
p86:      | flist
p87:      | list
p88: flist : LBRA type RBRA
p89: list : LBRA type COMMA INTEGER RBRA
p90: accessList : VARNAME listIndex listIndex
p91:            | VARNAME listIndex
p92: listIndex : LBRA evaluation RBRA
```
