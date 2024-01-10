
if __name__ == '__main__':
    import sys, traceback
    from sys import path, argv
    path.append('src')


    def hook(type, value, tb):
        """Reduce amount of backtrace displayed to be 1 file deep."""
        smalltrace = traceback.format_tb(tb, limit=1)
        smalltrace = smalltrace[0].split("\n")[0]
        exc = traceback.format_exception_only(type, value)[0]
        print(smalltrace + "\n" + exc)

    sys.excepthook = hook

    from os import getcwd
    from jacll_compiler import Jacll

    stream = ''
    if len(argv) < 2:
        while s := sys.stdin.readline():
            stream += s.strip()
    else:
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