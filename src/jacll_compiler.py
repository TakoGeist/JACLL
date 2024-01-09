from ast import List
from jacll_parser import parser
from utils import *

label_counter = 0;

def compile(stream):
    inter = parser.parse(stream)

    return code_generation(inter)

def get_val(tree, symbol_table, _type= False):
    if type(tree.name()) != str:
        out = 'push' + DataType.inferetype(tree.name()).terminator() + ' ' + str(tree.name()) + '\n'
        ty = DataType.inferetype(tree.name())
    elif tree.type == 'val':
        out = 'pushl ' + str(symbol_table[tree.name()][1]) + '\n'
        ty = symbol_table[tree.name()][0]
    else:
        if symbol_table[tree.name()][1] >= 0:
            out = 'pushfp\n'
        
            if type(tree.index()) == int:
                out += 'pushi ' + str(tree.index()) + '\n'
            else: 
                out += line(tree.index(), symbol_table)
        
            out += 'pushi ' + str(symbol_table[tree.name()][1]) + '\n'
            out += 'add\n'
        
        else:
            out = 'pushl ' + str(symbol_table[tree.name()][1]) + '\n'

            if type(tree.index()) == int:
                out += 'pushi ' + str(tree.index()) + '\n'
            else: 
                out += line(tree.index(), symbol_table)
        
            
        out += 'loadn\n'
        ty = symbol_table[tree.name()][2]

    if _type:
        return [out, ty]
    return out

def get_address(tree, symbol_table, _single= False):
    if tree.type == 'val':
        out = ''
        out += 'pushfp\npushi ' + str(symbol_table[tree.name()][1]) + '\n'
    else:
        out = 'pushfp\n'
        if type(tree.index()) == int:
            out += 'pushi ' + str(tree.index()) + '\n'
        else: 
            out += line(tree.index(), symbol_table)
        out += 'pushi ' + str(symbol_table[tree.name()][1]) + '\n'
        out += 'add\n'
        if _single:
            out += 'padd\n'
    return out

def bin_op(tree, symbol_table):
    if tree.type == 'val':
        return get_val(tree, symbol_table)
    
    if tree.type == 'valList':
        return get_val(tree, symbol_table)

    if tree.type == 'neg':
        op = tree.op()
        return op[0] + bin_op(tree.children[1], symbol_table) + op[1]

    if tree.type == 'not':
        return bin_op(tree.children[1], symbol_table) + tree.op()
    
    return bin_op(tree.left(), symbol_table) + bin_op(tree.right(), symbol_table) + tree.op()


def funcs(tree):
    out = ''
    symbol_table = SymbolTable()
    for func in tree:        
        out += func.name() + ':\n' + args(func.args(), symbol_table) + body(func.code(), symbol_table) + 'return\n'
        symbol_table.empty()
    return out

def args(tree, symbol_table):
    symbol_table.offset(len(tree))
    for var in tree:
        symbol_table.add(var)
    return ''

def line(tree, symbol_table):
    match tree.type:
        case 'init':
            return init(tree, symbol_table)
        case 'atrib':
            return atrib(tree, symbol_table)
        case 'for':
            return parse_for(tree, symbol_table)
        case 'if':
            return parse_if(tree, symbol_table)
        case 'print':
            return parse_print(tree, symbol_table)
        case 'read':
            return parse_read(tree, symbol_table)
        case 'call':
            return call(tree, symbol_table)
        case 'BinOp':
            return bin_op(tree, symbol_table)
        case 'val':
            return get_val(tree, symbol_table)
        case 'valList':
            return get_val(tree, symbol_table)


def body(tree, symbol_table):
    out = ''
    for elem in tree:
        out += line(elem, symbol_table)
    return out

        
def init(tree,symbol_table):
    symbol_table.add(tree)
    
    if type(tree.children[2]) == RoseTree and tree.children[2].type == 'neg':
        return bin_op(tree.children[2],symbol_table)

    match tree.get_elem_type():
        case DataType.FLOAT:
            type_ = 'f'
        case DataType.STR:
            type_ = 's'
        case _:
            type_ = 'i'
    
    if tree.get_type() == DataType.LIST: 
        out = ''
        if len(tree.children) == 4:
            out += 'pushn ' + str(tree.children[3]) + '\n'
        else:
            for elem in tree.children[2]:
                out += 'push' + type_ + ' ' + str(elem.val()) + '\n'
        return out

    if type(tree.children[2]) == RoseTree:
        if tree.children[2].type == 'call':
            return 'pushi 0\n' + line(RoseTree('atrib', tree.children), symbol_table)
        else:
            return line(tree.children[2],symbol_table)
    else:
        return 'push' + type_ + ' ' + str(tree.val()) + '\n'


def atrib(line,symbol_table):

    if line.children[2].type == 'call':
        out = call(line.children[2], symbol_table)
    else:
        out = bin_op(line.children[2], symbol_table)

    return out + 'storel ' + str(symbol_table[line.children[1]][1]) + '\n'
    
def parse_for(tree, symbol_table):
    global label_counter
    out = ''
    label1 = str(label_counter) + 'L'
    label_counter += 1
    label2 = str(label_counter) + 'L'
    label_counter += 1

    if tree.children[0] != None:
        if tree.children[0].type == 'init':
            out += init(tree.children[0], symbol_table)
        else:
            out += atrib(tree.children[0], symbol_table)
    
    out += label1 + ':\n'
    out += bin_op(tree.children[1], symbol_table)
    out += 'jz ' + label2 + '\n'
    out += line(tree.children[3][0], symbol_table)
    
    if tree.children[2] != None:
        if tree.children[2].type == 'call':
            out += call(tree.children[2],symbol_table)
        else:
            out += atrib(tree.children[2],symbol_table)
        
    out += 'jump ' + label1 + '\n' + label2 + ':\npop 1\n' 
    
    return out

def parse_if(tree, symbol_table):
    global label_counter
    out = ''
    if len(tree.children) == 3:
        label1 = str(label_counter) + 'L'
        label_counter += 1
        label2 = str(label_counter) + 'L'
        label_counter += 1
        out += bin_op(tree.children[0],symbol_table)
        out += 'jz ' + label2 + '\n'
        out += line(tree.children[1][0], symbol_table)
        out += 'jump ' + label2 + '\n'
        out += label1 + ':\n'
        out += line(tree.children[2][0], symbol_table)
        out += label2 + ':\n'
    else:
        label1 = str(label_counter) + 'L'
        label_counter += 1
        out += bin_op(tree.children[0],symbol_table)
        out += 'jz ' + label1 + '\n'
        out += line(tree.children[1][0], symbol_table)
        out += label1 + ':\n'
    return out

def parse_print(line, symbol_table):
    out = ''
    if line.children[0].type == 'val':

        if line.children[0].get_type() == DataType.STR:
            out += 'pushs ' + line.children[0].children[1] + '\n'
            out += 'writes\n'
            out += 'writeln\n'
            
        else:
            [val, type] = get_val(line.children[0], symbol_table, True)
            out += val

            match type:
                case DataType.STR:
                    type = 's'
                case DataType.FLOAT:
                    type = 'f'
                case _:
                    type = 'i'
            out += 'write' + type + '\n'
            out += 'writeln\n'

    elif line.children[0].type == 'valList':
        val = get_val(line.children[0], symbol_table)
        out += val
        match line.children[0].get_elem_type():
            case DataType.STR:
                type = 's'
            case DataType.FLOAT:
                type = 'f'
            case _:
                type = 'i'
        out += 'write' + type + '\n'
        out += 'writeln\n'
    else:
        out += line(line.children[0], symbol_table)
        match line.children[0].get_type():
            case DataType.FLOAT:
                type = 'f'
            case DataType.STR:
                type = 's'
            case _:
                type = 'i'
        out += 'write' + type + '\n'
        out += 'writeln\n'
    
    return out
    
def parse_read(tree, symbol_table):
    out = ''

    match tree.children[0].get_elem_type():
        case DataType.INT:
            conversion = 'atoi\n'
        case DataType.BOOL:
            conversion = 'atoi\n'
        case DataType.FLOAT:
            conversion = 'atof\n'
        case _:
            conversion = ''
            

    out += get_address(tree.children[0], symbol_table)
    out += 'read\n'
    out += conversion
    out += 'storen\n'
        
    return out

def call(tree, symbol_table):
    out = ''
    for arg in tree.args():
        if arg.get_type() == DataType.LIST:
            out += get_address(arg, symbol_table, _single= True)
        else:
            out += get_val(arg, symbol_table)
    out += 'pusha ' + tree.name() + '\n'
    out += 'call\n'
    return out

def code_generation(inter):
    out = 'start\npusha main\ncall\nstop\n\n'
    
    prog = inter.children
    out += funcs(prog)
        
    return out
