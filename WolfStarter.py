from zelly.window import Window
from sys import exc_info
from traceback import format_exception
from urllib.request import urlopen,URLError,HTTPError
from socket import timeout
from builtins import isinstance
from os.path import isfile,isdir,abspath
from os import remove
from shutil import copyfileobj
from zipfile import is_zipfile,ZipFile
from subprocess import call
from sys import exit,argv

WOLFSTARTER_VERSION = "v1.2.2"

DELETEZIPLIST=[]
def markfordeletion(filename):
    DELETEZIPLIST.append(filename)

def deletezips():
    for x in DELETEZIPLIST:
        try:
            remove(x)
            logfile("Deleted %s" % x)
        except OSError:
            logfile("Error deleting file %s" % x)

def logfile(msg):
    print(msg)
    with open("wolfstarter.log","a") as errorlog:
        errorlog.write('%s\n' % msg)

def versiontoint(version):
    if isinstance(version,int):
        return version
    elif isinstance(version,str):
        version = version.replace('v','').replace('.','')
    else:
        return None
    
    try:
        version = int(version)
    except ValueError:
        version = None
    return version

def check_updater_update():
    try:
        version = urlopen('https://raw.githubusercontent.com/Zelly/ETWolfStarter/master/updater/version.txt',timeout=1).read().decode()
    except (URLError,HTTPError):
        logfile("Error contacting update server")
        return False
    except timeout:
        logfile("Update server timed out")
        return False
    int_version = versiontoint(version)
    if not int_version:
        logfile("Invalid data received from update server")
        return False
    
    logfile("Found version %s" % version)
    # Missing updater entirely
    # Download updater
    # not found during debugging, could pose problem
    if not isdir('updater') or not isfile('updater/version.txt') or not isfile('updater/WolfStarterUpdater.exe'):
        update_updater(version)
        return True
    
    try:
        updater_version=open('updater/version.txt','rb').read().decode()
    except IOError:
        logfile("Could not open version file")
        return False # Do I want to update here?
    int_updater_version = versiontoint(updater_version)
    if not int_updater_version:
        logfile("No version found in updater/version.txt")
        return False # Do I want to update here?
    
    # Updater version is old, proceed to update
    if int_updater_version < int_version:
        update_updater(version)
        return True
    
def update_updater(version):
    if not isfile("ETWolfStarter-%s.zip" % version) or not is_zipfile("ETWolfStarter-%s.zip" % version):
        url      = "https://github.com/Zelly/ETWolfStarter/releases/download/%s/ETWolfStarter-%s.zip" % (version,version)
        filename = url.split('/')[-1]
        try:
            with urlopen(url,timeout=1) as response,open(filename,'wb') as outfile:
                copyfileobj(response,outfile)
        except (URLError,HTTPError):
            logfile("Could not get update file")
            return
        except OSError:
            logfile("Could not write to %s" % filename)
            return
        except timeout:
            logfile("Could not contact update server")
            return
    markfordeletion(abspath(filename))
    logfile("Extracting updater")
    updater_zip=ZipFile("ETWolfStarter-%s.zip" % version)
    extractlist=[ v for v in updater_zip.namelist() if 'updater/' in v or v == 'updater' ]
    updater_zip.extractall(members=extractlist)
    updater_zip.close()
    logfile("Finished extracting updater")

def update(version):
    logfile("Calling updater")
    call('updater/WolfStarterUpdater.exe')
    logfile("Closing program to update")
def check_update():
    try:
        version = urlopen('https://raw.githubusercontent.com/Zelly/ETWolfStarter/master/version.txt',timeout=1).read().decode()
    except (URLError,HTTPError):
        logfile("Error contacting update server")
        return False
    except timeout:
        logfile("Update server timed out")
        return False
    int_version = versiontoint(version)
    if not int_version:
        logfile("Invalid data received from update server")
        return False
    
    with open('version.txt','wb') as versionfile:
        versionfile.write(WOLFSTARTER_VERSION.encode())
    
    int_wolfstarter_version = versiontoint(WOLFSTARTER_VERSION)
    if not int_wolfstarter_version:
        logfile("Version missing in wolfstarter")
        return False # Do I want to update here?
    
    # Updater version is old, proceed to update
    if int_wolfstarter_version < int_version:
        update(version)
        return True
    
if __name__ == '__main__':
    logfile(argv)
    if argv and len(argv) > 1 and ( argv[1].lower() == "-n" or argv[1].lower() == "--no-update" ):
        print("Skipping update")
    else:
        check_updater_update()
        if check_update(): exit(0)
        
    
    logfile("Program Start")
    try:
        Window()
    except:
        e1,e2,e3 = exc_info()
        lines = format_exception(e1,e2,e3)
        logfile(''.join(''+line for line in lines))
        raise
    logfile("Program End")
