from jacll_parser import parser
from utils import *

class Jacll():
        
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.label_counter = 0;

    def compile(self, stream):
        """Function to use externally in order to compile a '.jacll' file

        Args:
            stream (str): File to compile

        Returns:
            str: Assembly code
        """
        inter = parser.parse(stream)

        return self.code_generation(inter)

    def get_val(self, tree, _type= False):
        """Returns instructions to get variable's value based on it's declaration.

        Args:
            tree (RoseTree): Node where the value is stored
            _type (bool, optional): Variable to determine if the type of
            the value should be returned with it as a list [val, type]. Defaults to False.

        Returns:
            str | [str, DataType]: Instructions to get variable's value / value and type
        """
        if type(tree.name()) != str:
            out = 'push' + DataType.inferetype(tree.name()).terminator() + ' ' + str(tree.name()) + '\n'
            ty = DataType.inferetype(tree.name())
        elif tree.type == 'val':
            out = 'pushl ' + str(self.symbol_table[tree.name()][1]) + '\n'
            ty = self.symbol_table[tree.name()][0]
        else:
            if self.symbol_table[tree.name()][1] >= 0:
                out = 'pushfp\n'
            
                if type(tree.index()) == int:
                    out += 'pushi ' + str(tree.index()) + '\n'
                else: 
                    out += self.line(tree.index())
            
                out += 'pushi ' + str(self.symbol_table[tree.name()][1]) + '\n'
                out += 'add\n'
            
            else:
                out = 'pushl ' + str(self.symbol_table[tree.name()][1]) + '\n'

                if type(tree.index()) == int:
                    out += 'pushi ' + str(tree.index()) + '\n'
                else: 
                    out += self.line(tree.index())
            
                
            out += 'loadn\n'
            ty = self.symbol_table[tree.name()][2]

        if _type:
            return [out, ty]
        return out

    def get_address(self, tree, _single= False):
        """Returns variable's stack address based on the programs symbol_table.

        Args:
            tree (RoseTree): Node where the variable's name is stored

        Returns:
            str : Variable's stack address
        """
        if type(tree) == str:
            return 'pushfp\npush' + self.symbol_table[tree][0].terminator() + ' ' + str(self.symbol_table[tree][1]) + '\n'
        if tree.type == 'val':
            out = 'pushfp\npushi ' + str(self.symbol_table[tree.name()][1]) + '\n'
        elif tree.type == 'var':
            out = 'pushfp\npushi ' + str(self.symbol_table[tree.name()][1]) + '\n'
        else:
            if self.symbol_table[tree.name()][1] >= 0:
                out = 'pushfp\n'
                if type(tree.index()) == int:
                    out += 'pushi ' + str(tree.index()) + '\n'
                else: 
                    out += self.line(tree.index())
                out += 'pushi ' + str(self.symbol_table[tree.name()][1]) + '\n'
                out += 'add\n'
                if _single:
                    out += 'padd\n'
            else:
                out = 'pushl ' + str(self.symbol_table[tree.name()][1]) + '\n'
        return out

    def bin_op(self, tree):
        """Decodes 'BinOp' nodes 

        Args:
            tree (RoseTree): Node where the 'BinOP' is declared

        Returns:
            str: Instructions of a decoded 'BinOp'
        """
        if tree.type == 'val':
            return self.get_val(tree)
        
        if tree.type == 'valList':
            return self.get_val(tree)
        
        if tree.type == 'call':
            return self.line(tree)

        if tree.type == 'neg':
            op = tree.op()
            return op[0] + self.bin_op(tree.children[1]) + op[1]

        if tree.type == 'not':
            return self.bin_op(tree.children[1]) + tree.op()
        
        return self.bin_op(tree.left()) + self.bin_op(tree.right()) + tree.op()


    def funcs(self, tree):
        """Decodes the program's structure by function headers and function bodies
        so that the assembly correctly manages the stack

        Args:
            tree ([RoseTree]): List of RoseTree objects where the functions are stored

        Returns:
            str: Decoded functions(final program without the initialization gives incorrect 
            behaviour on the virtual machine for programs with more functions than main)
        """
        out = ''
        
        for func in tree:        
            argus = func.args()
            code = func.code()
            out += func.name() + ':\n' + self.args(argus) + self.body(code[:len(code) - 1])
            [bod, re] = self.ret(code[-1])
            if bod:
                out += bod

            if len(argus) != 0:
                out += 'storel ' + str(self.symbol_table[argus[0].name()][1]) + '\n'

            if bod:
                if len(self.symbol_table.table) - len(argus) > 0:
                    out += 'pop ' + str(len(self.symbol_table.table) - len(argus)) + '\n'
            else:
                if len(self.symbol_table.table) - len(argus) > 1:
                    out += 'pop ' + str(len(self.symbol_table.table) - len(argus) - 1) + '\n'
                
            out += re
            out += '\n\n'
            self.symbol_table.empty()
        return out

    def args(self, tree):
        """Decodes functions arguments in order for the stack to be properly managed.
        Functions arguments sit bellow said function frame pointer in order of the declaration.
        !This functions only manages the internal symbol table. It doesn't produce assembly code!

        Args:
            tree ([RoseTree]): List of RoseTree objects where the function's arguments are stored

        Returns:
            str: Empty string
        """
        self.symbol_table.offset(len(tree))
        for var in tree:
            self.symbol_table.add(var)
        return ''

    def line(self, tree):
        """Node type decoder

        Args:
            tree (RoseTree): Node

        Returns:
            Any: Correct funtion call based on Node type
        """
        match tree.type:
            case 'init':
                return self.init(tree)
            case 'atrib':
                return self.atrib(tree)
            case 'for':
                return self.parse_for(tree)
            case 'if':
                return self.parse_if(tree)
            case 'print':
                return self.parse_print(tree)
            case 'read':
                return self.parse_read(tree)
            case 'call':
                return self.call(tree)
            case 'BinOp':
                return self.bin_op(tree)
            case 'val':
                return self.get_val(tree)
            case 'valList':
                return self.get_val(tree)
            case 'ret':
                return self.ret(tree)

    def ret(self, tree):
        """Decodes 'return' instruction

        Args:
            tree (RoseTree):  RoseTree object where the return is stored

        Returns:
            [str, str]: First string constitutes adjustments needed for non-empty 'return'. Second string is just 'return'.
        """
        out = ''
        if len(tree.children) != 0:
            if tree.children[0].type != 'val':
                out += self.line(tree.children[0])
            else:
                out = False
        return [out, 'return\n']


    def body(self, tree):
        """Decodes function body

        Args:
            tree ([RoseTree]):  List of RoseTree objects which store every line of code inside function

        Returns:
            str: Function Body in assembly
        """
        out = ''
        for elem in tree:
            out += self.line(elem)
        return out

            
    def init(self, tree):
        """Variable initialization. In charge of adding to the internal symbol table and to the Virtual Machine stack

        Args:
            tree (RoseTree):  RoseTree object where the initialization is stored

        Returns:
            str: Stack push in assembly
        """
        self.symbol_table.add(tree)

        if type(tree.children[2]) == RoseTree and tree.children[2].type == 'neg':
            return self.bin_op(tree.children[2])

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
                if len(tree.children[2]) != tree.children[3]:
                    out += 'pushn ' + str(tree.children[3]) + '\n'
                else:
                    for elem in tree.children[2]:
                        out += 'push' + type_ + ' ' + str(elem.val()) + '\n'
            return out

        if type(tree.children[2]) == RoseTree:
            if tree.children[2].type == 'call':
                return 'pushi 0\n' + self.line(RoseTree('atrib', tree.children))
            else:
                return self.line(tree.children[2])
        else:
            return 'push' + type_ + ' ' + str(tree.val()) + '\n'


    def atrib(self, tree):
        """Decodes attributions. In charge of evaluating and storing an attribution.

        Args:
            tree (RoseTree):  RoseTree object where the attribution is stored

        Returns:
            str: Assembly code for fetching, evaluation and storing (3 steps for attribution)
        """

        if tree.children[2].type == 'call':
            out = self.call(tree.children[2])
        else:
            out = self.bin_op(tree.children[2])

        address = self.get_address(tree.children[1])

        return address + out + 'storen\n'
        
    def parse_for(self, tree):
        """Decodes 'for' Loops

        Args:
            tree (RoseTree):  RoseTree object where the for-loop is stored

        Returns:
            str: for-loop assembly code
        """
        out = ''
        label1 = str(self.label_counter) + 'L'
        self.label_counter += 1
        label2 = str(self.label_counter) + 'L'
        self.label_counter += 1

        if tree.children[0] != None:
            if tree.children[0].type == 'init':
                out += self.init(tree.children[0])
            else:
                out += self.atrib(tree.children[0])
        
        out += label1 + ':\n'
        out += self.bin_op(tree.children[1])
        out += 'jz ' + label2 + '\n'
        out += self.line(tree.children[3][0])
        
        if tree.children[2] != None:
            if tree.children[2].type == 'call':
                out += self.call(tree.children[2])
            else:
                out += self.atrib(tree.children[2])
            
        out += 'jump ' + label1 + '\n' + label2 + ':\npop 1\n' 
        
        if tree.children[0] != None:
            self.symbol_table.remove(tree.children[0])

        return out

    def parse_if(self, tree):
        """Decodes 'for' Loops

        Args:
            tree (RoseTree):  RoseTree object where the for-loop is stored

        Returns:
            str: for-loop assembly code
        """
        out = ''

        if len(tree.children) == 3:
            label1 = str(self.label_counter) + 'L'
            self.label_counter += 1
            label2 = str(self.label_counter) + 'L'
            self.label_counter += 1
            out += self.bin_op(tree.children[0])
            out += 'jz ' + label1 + '\n'
            out += self.line(tree.children[1][0])
            out += 'jump ' + label2 + '\n'
            out += label1 + ':\n'
            out += self.line(tree.children[2][0])
            out += label2 + ':\n'
        else:
            label1 = str(self.label_counter) + 'L'
            self.label_counter += 1
            out += self.bin_op(tree.children[0])
            out += 'jz ' + label1 + '\n'
            out += self.line(tree.children[1][0])
            out += label1 + ':\n'
        return out

    def parse_print(self, tree):
        """Decodes 'print' functions. Manages stdout requests.

        Args:
            tree (RoseTree): RoseTree object where 'print' calls are stored

        Returns:
            str: Data fetch and print call in assembly
        """
        out = ''
        if tree.children[0].type == 'val':

            if tree.children[0].get_type() == DataType.STR:
                out += 'pushs ' + tree.children[0].children[1] + '\n'
                out += 'writes\n'
                out += 'writeln\n'
                
            else:
                [val, type] = self.get_val(tree.children[0], True)
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

        elif tree.children[0].type == 'valList':
            val = self.get_val(tree.children[0])
            out += val
            match tree.children[0].get_elem_type():
                case DataType.STR:
                    type = 's'
                case DataType.FLOAT:
                    type = 'f'
                case _:
                    type = 'i'
            out += 'write' + type + '\n'
            out += 'writeln\n'
        else:
            out += self.line(tree.children[0])
            match tree.children[0].get_type():
                case DataType.FLOAT:
                    type = 'f'
                case DataType.STR:
                    type = 's'
                case _:
                    type = 'i'
            out += 'write' + type + '\n'
            out += 'writeln\n'
        
        return out
        
    def parse_read(self, tree):
        """Decodes 'read' functions. Manages stdin requests.

        Args:
            tree (RoseTree): RoseTree object where 'read' calls are stored

        Returns:
            str: read call and data storage in assembly
        """
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
                

        out += self.get_address(tree.children[0])
        out += 'read\n'
        out += conversion
        out += 'storen\n'
            
        return out

    def call(self, tree):
        """Decodes non internal 'function' calls.

        Args:
            tree (RoseTree): RoseTree object where calls are stored with arguments

        Returns:
            str: Assembly stack management to guarantee correct argument passing between functions
        """
        out = ''
        for arg in tree.args():
            if arg.type == 'BinOp':
                out += self.bin_op(arg)
            elif arg.get_type() == DataType.LIST:
                out += self.get_address(arg, _single= True)
            else:
                out += self.get_val(arg)
        out += 'pusha ' + tree.name() + '\n'
        out += 'call\n'
        if len(tree.args()) > 1:
            out += 'pop ' + str(len(tree.args()) - 1) + '\n'
        return out

    def code_generation(self, inter):
        """Creates initial code section to ensure main as first function executed

        Args:
            inter (RoseTree): RoseTree object containing whole program (Initial Node)

        Returns:
            str: Whole program in assembly
        """
        out = 'start\npusha main\ncall\nstop\n\n'
        
        prog = inter.children
        out += self.funcs(prog)
            
        return out
