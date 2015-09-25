from urllib.request import urlopen, URLError, HTTPError
from socket import timeout
from builtins import isinstance
from zelly.constants import logfile, WOLFSTARTER_VERSION, UPDATE_RAWSRC_URL, UPDATE_RELEASE_URL


def version_to_int(version):
    if isinstance(version, int):
        return version
    elif isinstance(version, str):
        version = version.replace('v', '').replace('.', '')
    else:
        return None

    try:
        version = int(version)
    except ValueError:
        version = None
    return version


class WolfStarterUpdater:
    def __init__(self):
        self.version_path = 'version.txt'
        self.str_version = ''
        self.version = 0

    def check(self):
        logfile("WolfStarterUpdater: Getting version from %s%s" % (UPDATE_RAWSRC_URL, self.version_path))
        try:
            self.str_version = urlopen("%s%s" % (UPDATE_RAWSRC_URL, self.version_path), timeout=0.5).read().decode()
        except (URLError, HTTPError):
            logfile("WolfStarterUpdater: Error contacting update server")
            return False
        except timeout:
            logfile("WolfStarterUpdater: Update server timed out")
            return False
        self.version = version_to_int(self.str_version)
        if not self.version:
            logfile("WolfStarterUpdater: Invalid data received from update server")
            return False

        logfile("WolfStarterUpdater: Found version %s (%d)" % (self.str_version, self.version))

        int_current_version = version_to_int(WOLFSTARTER_VERSION)
        if not int_current_version:
            logfile("WolfStarterUpdater: No version found ?")
            return False  # Do I want to update here?

        # Updater version is old, proceed to update
        if int_current_version < self.version:
            return True

    def get_release_url(self):
        return "%s%s/" % (UPDATE_RELEASE_URL, self.str_version)
