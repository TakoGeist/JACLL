
if __name__ == '__main__':
    from sys import argv
    from os import getcwd
    from jacll_compiler import compile

    if len(argv) < 2:
        print("No arguments foound.")
        quit()

    if argv[1].endswith('.jacll'):
        stream = open(getcwd() + "\\" + argv[1], 'r').read()
    else:
        raise TypeError("Invalid file type. Expected '.jacll' file.")

    assembly = compile(stream)

    if len(argv) < 3:
        print(assembly)
    else:
        file_out = open(getcwd() + "\\" + argv[2] + ".txt", 'w')
        file_out.write(assembly)
        file_out.close()