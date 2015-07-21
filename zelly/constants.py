from subprocess import Popen

WOLFSTARTER_VERSION = "v1.3.1"
UPDATE_RAWSRC_URL  = r"https://raw.githubusercontent.com/Zelly/ETWolfStarter/master/"
UPDATE_RELEASE_URL = r"https://github.com/Zelly/ETWolfStarter/releases/download/"

BLACK      = "#000000"
DARK_GREY  = "#282828"
GREY       = "#484848"
LIGHT_GREY = "#E0E0E0"
WHITE      = "#FFFFFF"

PLAYER_NAME_LENGTH       = 32
PLAYER_PING_LENGTH       = 8
PLAYER_SCORE_LENGTH      = 12
SERVERSTATUS_TEXT_LENGTH = 54
HALFLEN = int((SERVERSTATUS_TEXT_LENGTH - 3) / 2)
HEADERLENGTH = SERVERSTATUS_TEXT_LENGTH - 14

# BUTTON ORDERING
BUTTON_OPEN     = 0
BUTTON_SAVE     = 1
BUTTON_ADD      = 2
BUTTON_REMOVE   = 3
BUTTON_JOIN     = 4
BUTTON_ISSUE    = 5
BUTTON_DONATE   = 6
BUTTON_MINIMIZE = 7
BUTTON_QUIT     = 8
BUTTON_UPDATE   = 9
LABEL_VERSION   = 10

# FRAME ORDER
# FRAME_WINDOW None - Is entire window
# FRAME_SERVER None - Is entire window(with padding)
FRAME_NAVBAR = (0,0)
FRAME_HEADER = (0,0)
FRAME_SERVERLIST = (1,0)
FRAME_SERVERDATA = (2,0)
FRAME_SERVERSTATUS = (0,1)
LABEL_NOTICE = (3,0)

def logfile(msg):
    print(msg)
    with open("wolfstarter.log","a") as errorlog:
        errorlog.write('%s\n' % msg)

def openprocess(command):
    """Opens process without making current application hang"""
    Popen(command,shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)