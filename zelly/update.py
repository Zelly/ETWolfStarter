from urllib.request import urlopen,URLError,HTTPError
from socket import timeout
from builtins import isinstance
from zelly.constants import logfile,WOLFSTARTER_VERSION,UPDATE_RAWSRC_URL,UPDATE_RELEASE_URL

class WolfStarterUpdater:
    def __init__(self):
        self.versionpath = 'version.txt'
        self.strversion     = ''
        self.version        = 0
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
        
        int_current_version = self.versiontoint(WOLFSTARTER_VERSION)
        if not int_current_version:
            logfile("No version found ?")
            return False # Do I want to update here?
        
        # Updater version is old, proceed to update
        if int_current_version < self.version:
            return True
    
    def getreleaseurl(self):
        return "%s%s/" % ( UPDATE_RELEASE_URL , self.strversion )
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