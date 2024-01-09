
if __name__ == '__main__':
    from sys import argv
    from os import getcwd
    from jacll_compiler import compile

    if len(argv) < 2:
        print("No arguments foound.")
        quit()

    stream = open(getcwd() + "\\" + argv[1] + ".jacll", 'r').read()

    print(compile(stream))