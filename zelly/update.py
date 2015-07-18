from urllib.request import urlopen,URLError,HTTPError
from socket import timeout
from builtins import isinstance
from os.path import isfile,isdir,abspath
from os import remove
from shutil import copyfileobj
from zipfile import is_zipfile,ZipFile
from zelly.constants import logfile,WOLFSTARTER_VERSION,UPDATE_RAWSRC_URL,UPDATE_RELEASE_URL,openprocess
from sys import exit

class WolfStarterUpdater:
    def __init__(self,updater=False):
        if updater:
            self.versionpath = 'updater/version.txt'
        else:
            self.versionpath = 'version.txt'
        self.strversion     = ''
        self.version        = 0
        self.updater        = updater
        self.check()
    def check(self):
        logfile("Getting version from %s%s" % ( UPDATE_RAWSRC_URL , self.versionpath ) )
        try:
            self.strversion = urlopen("%s%s" % ( UPDATE_RAWSRC_URL , self.versionpath ),timeout=0.5).read().decode()
        except (URLError,HTTPError):
            logfile("Error contacting update server")
            return False
        except timeout:
            logfile("Update server timed out")
            return False
        self.version = self.versiontoint(self.strversion)
        if not self.version:
            logfile("Invalid data received from update server")
            return False
        
        logfile("Found version %s (%d)" % ( self.strversion , self.version ) )
        
        if self.updater:
            # Missing updater entirely
            # Download updater
            # not found during debugging, could pose problem
            if not isdir('updater') or not isfile('updater/version.txt') or not isfile('updater/WolfStarterUpdater.exe'):
                self.update()
                return True
        
        
        int_current_version = self.versiontoint(WOLFSTARTER_VERSION)
        if not int_current_version:
            logfile("No version found ?")
            return False # Do I want to update here?
        
        # Updater version is old, proceed to update
        if int_current_version < self.version:
            self.update()
            return True
        def update(self):
            if not isfile("ETWolfStarter-%s.zip" % self.strversion) or not is_zipfile("ETWolfStarter-%s.zip" % self.strversion):
                url      = "%s%s/ETWolfStarter-%s.zip" % (UPDATE_RELEASE_URL,self.strversion,self.strversion)
                filename = url.split('/')[-1]
                try:
                    with urlopen(url,timeout=1) as response,open(filename,'wb') as outfile:
                        copyfileobj(response,outfile)
                except (URLError,HTTPError):
                    logfile("Could not get update package")
                    return
                except OSError:
                    logfile("Could not write to %s" % filename)
                    return
                except timeout:
                    logfile("Could not contact update server")
                    return
            self.markfordeletion(abspath(filename))
            logfile("Extracting %s update package" % self.strversion)
            updater_zip=ZipFile("ETWolfStarter-%s.zip" % self.strversion)
            if self.updater:
                extractlist=[ v for v in updater_zip.namelist() if 'updater/' in v or v == 'updater' ]
            else:
                extractlist=[ v for v in updater_zip.namelist() if not 'updater/' in v and v != 'updater' ]
            updater_zip.extractall(members=extractlist)
            updater_zip.close()
            logfile("Finished extracting update package")
            if self.updater:
                openprocess("updater/WolfStarterUpdater.exe")
            else:
                self.deleteziplist()
                openprocess("WolfStarter.exe")
            exit(0)
                
    def versiontoint(self,version):
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
    def markfordeletion(self,filename):
        if filename not in self.deletelist: self.deletelist.append(filename)
    def deleteziplist(self):
        for filetobedeleted in self.deletelist:
            try:
                remove(filetobedeleted)
                logfile("Deleted %s" % filetobedeleted)
            except OSError:
                logfile("Error deleting file %s" % filetobedeleted)