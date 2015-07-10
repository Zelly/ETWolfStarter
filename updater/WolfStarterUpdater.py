from os import getcwd,chdir,remove
from os.path import isfile
from urllib.request import urlopen,URLError,HTTPError
from socket import timeout
from subprocess import call
from zipfile import is_zipfile,ZipFile
from shutil import copyfileobj
from sys import argv

WOLFSTARTER_VERSION_U = "v1.2.2"
with open('version.txt','wb') as versionfile: versionfile.write(WOLFSTARTER_VERSION_U.encode())
chdir("/".join( getcwd().replace('\\','/').split('/')[0:-1] ) )
print(getcwd())

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
def update(version):
    url      = "https://github.com/Zelly/ETWolfStarter/releases/download/%s/ETWolfStarter-%s.zip" % (version,version)
    filename = url.split('/')[-1]
    if not isfile(filename) or not is_zipfile(filename):
        logfile("Downloading %s release from %s\nSaving to %s" % ( version , url , filename ) )
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
    else:
        logfile("Found existing %s using that" % filename)
    logfile("Extracting wolfstarter")
    updater_zip=ZipFile(filename)
    extractlist=[ v for v in updater_zip.namelist() if not 'updater/' in v and not v == 'updater' ]
    updater_zip.extractall(members=extractlist)
    updater_zip.close()
    logfile("Finished extracting wolfstarter")
    remove(filename)
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
    if not isfile('version.txt') or not isfile('WolfStarter.exe'):
        update(version)
        return True
    
    try:
        wolfstarter_version=open('version.txt','rb').read().decode()
    except IOError:
        logfile("Could not open version file")
        update(version)
        return True # Do I want to update here?
    int_wolfstarter_version = versiontoint(wolfstarter_version)
    if not int_wolfstarter_version:
        logfile("Version missing in wolfstarter")
        update(version)
        return True # Do I want to update here?
    
    # Updater version is old, proceed to update
    if int_wolfstarter_version < int_version:
        update(version)
        return True
    
if __name__ == "__main__":
    print(argv)
    print(len(argv))
    if argv and len(argv) >= 2 and argv[1].lower() == "--no-update":
        print("Running from script, cannot validate executables")
    else:
        check_update()
        if isfile('WolfStarter.exe'): call("WolfStarter.exe")
