from zelly.window import Window
from zelly.constants import logfile
from sys import exc_info
from traceback import format_exception
from sys import argv

if __name__ == '__main__':
    logfile(argv)

    logfile("Program Start")
    try:
        Window()
    except:
        e1, e2, e3 = exc_info()
        lines = format_exception(e1, e2, e3)
        logfile(''.join('' + line for line in lines))
        raise
    logfile("Program End")
