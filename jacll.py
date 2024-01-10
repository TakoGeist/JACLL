
if __name__ == '__main__':
    import sys, traceback
    from sys import path, argv
    path.append('src')

    def hook(type, value, tb):
        smalltrace = traceback.format_tb(tb, limit=1)
        smalltrace = smalltrace[0].split("\n")[0]
        exc = traceback.format_exception_only(type, value)[0]
        print(smalltrace + "\n" + exc)

    sys.excepthook = hook

    from os import getcwd
    from jacll_compiler import Jacll

    if len(argv) < 2:
        print("No arguments found.")
        quit()

    if argv[1].endswith('.jacll'):
        stream = open(getcwd() + "\\" + argv[1], 'r').read()
    else:
        raise TypeError("Invalid file type. Expected '.jacll' file.")

    compiler = Jacll()
    assembly = compiler.compile(stream)

    if len(argv) < 3:
        print(assembly)
    else:
        file_out = open(getcwd() + "\\" + argv[2] + ".txt", 'w')
        file_out.write(assembly)
        file_out.close()