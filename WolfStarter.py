from zelly.window import Window
from sys import exc_info
from traceback import format_exception
    
def logfile(msg):
    print(msg)
    with open("wolfstarter.log","a") as errorlog:
        errorlog.write('%s\n' % msg)
def main(args=None):
    try:
        Window()
    except:
        e1,e2,e3 = exc_info()
        lines = format_exception(e1,e2,e3)
        logfile(''.join(''+line for line in lines))
        raise
if __name__ == '__main__':
    logfile("Program Start")
    main()
    logfile("Program End")