import json
from os.path import isfile
from re import compile
import socket
from time import time
from zelly.constants import logfile


ipmatch = compile("(%d+%.%d+%.%d+%.%d+)")
playermatch=compile("(\d+) (\d+) \"(.*)\"")
def getIP(d):
    try:
        data = socket.gethostbyname(d)
        ip   = repr(data)
        return ip
    except Exception:
        return None
class ServerData:
    def __init__(self):
        self.Servers = [ ]
        self.fs_homepath = ""
        self.fs_basepath = ""
        self.ETPath      = ""
        self.parameters  = ""
        
    def load_serverfile(self,filename):
        if not filename:
            logfile("load_serverfile: No filepath given")
            return
        if not isfile(filename):
            logfile("load_serverfile: %s is not a file" % filename)
            return
        with open(filename) as jsonfile:
            serversjson = json.load(jsonfile)
        if not serversjson or not "Servers" in serversjson or not serversjson['Servers']:
            logfile("load_serverfile: No servers loaded from file")
            self.Servers = [ ]
            return
        self.Servers = serversjson['Servers']
        for Server in self.Servers:
            Server['map']        = ''
            Server['ping']       = -1
            Server['players']    = '-'
            Server['playerlist'] = []
            Server['cvar']       = {}
            Server['laststatus'] = 0
        self.fs_basepath = serversjson['fs_basepath'] if 'fs_basepath' in serversjson else ''
        self.fs_homepath = serversjson['fs_homepath'] if 'fs_homepath' in serversjson else ''
        self.ETPath      = serversjson['ETPath'] if 'ETPath' in serversjson else ''
        self.parameters  = serversjson['parameters'] if 'parameters' in serversjson else ''
        logfile("load_serverfile: Loaded %d servers" % len(self.Servers))
    def save_serverfile(self,filename):
        if not filename:
            logfile("save_serverfile: No filepath given")
            return
        for Server in self.Servers:
            Server['map']        = None
            Server['ping']       = None
            Server['players']    = None
            Server['playerlist'] = None
            Server['cvar']       = None
            Server['laststatus'] = None
            Server['fs_game']    = None
        jsonfile = open(filename,'w')
        json.dump({'fs_basepath':self.fs_basepath,'fs_homepath':self.fs_homepath,'ETPath':self.ETPath,'parameters':self.parameters,'Servers':self.Servers},jsonfile,skipkeys=True,allow_nan=True, sort_keys=True, indent=4)
        logfile("save_serverfile: Saved %d servers" % len(self.Servers))
        
        
    """
    Servers.json {
        fs_basepath : ''
        fs_homepath : ''
        etpath : ''
        parameters : ''
        Servers : {
            'title'      : 'LESM Test Server',
            'password'   : '',
            'address'    : '108.61.18.109:27950',
            'parameters' : '+set com_hunkMegs 256', 
            'rcon'       : '',
            'fs_basepath': '',
            'fs_homepath': '',
            'ETPath'     : '',
        }
    """
    def add_server(self,Server):
        if not Server:
            logfile("add_server: No serverdata given")
            return
        if not type(Server) is dict:
            logfile("add_server: Serverdata was not valid type")
            return
        if not 'title' in Server:
            logfile("add_server: Server requires title")
            return
        if not 'address' in Server:
            logfile("add_server: Server requires address")
            return
        if not 'password' in Server: Server['password'] = ''
        if not 'fs_homepath' in Server: Server['fs_homepath'] = ''
        if not 'fs_basepath' in Server: Server['fs_basepath'] = ''
        if not 'ETPath' in Server: Server['ETPath'] = ''
        if not 'parameters' in Server: Server['parameters'] = ''
        if not 'rcon' in Server: Server['rcon'] = ''
        Server['map']        = ''
        Server['ping']       = -1
        Server['players']    = '-'
        Server['playerlist'] = []
        Server['cvar']       = {}
        Server['laststatus'] = 0
        Server['fs_game']    = 'etmain'
        if any( s['title'] == Server['title'] for s in self.Servers ):
            logfile("add_server: %s title already exists" % Server['title'])
            return
        if any( s['address'] == Server['address'] for s in self.Servers ):
            logfile("add_server: %s address already exists" % Server['address'])
            return
        self.Servers.append(Server)
        logfile("add_server: %s(%s) server was added" % ( Server['title'],Server['address']) )
    def getstatus(self,serverid=None):
        if serverid == None or not self.Servers[serverid]:
            logfile("getstatus: Invalid server id (%s)" % str(serverid))
            return
        
        Server = self.Servers[serverid]
        current = time()
        if Server['laststatus'] != 0 and (current - Server['laststatus']) < 2:
            logfile("getstatus: Too many status checks in short time")
            return
        Server['laststatus'] = current
        
        IP     = Server['address']
        PORT   = "27960"
        if ":" in IP:
            IP   = Server['address'].split(':')[0].strip()
            PORT = Server['address'].split(':')[1].strip()
        if not ipmatch.match(IP):
            oldhostname=IP
            IP = getIP(IP)
            logfile("getstatus: resolved %s from %s" % (IP ,oldhostname) )
            
        PORT = int(PORT)
        if not IP:
            logfile("getstatus: %s was not a valid ip" % (str(IP)) )
            return
        if not PORT:
            logfile("getstatus: %s was not a valid port" % (str(PORT)) )
            return
        IP=IP.replace('\"',"").replace("'",'')
        logfile("getstatus: %s:%s" % ( str(IP) , str(PORT) ) )
        ADDRESS = (IP,PORT)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
        except OSError as e:
            s.close()
            logfile("getstatus: Error creating socket for %s:%d\n%s" % (ADDRESS[0],ADDRESS[1],str(e)) )
            return
        ping_start = time()
        try:
            logfile(b'getstatus: \xff\xff\xff\xffgetstatus')
            logfile(str(s.sendto(b'\xff\xff\xff\xffgetstatus', ADDRESS)) + " bytes sent")
        except socket.timeout:
            s.close()
            logfile("getstatus: Send connection timed out(500ms) for %s:%d" % ADDRESS )
            return
        except OSError as e:
            s.close()
            logfile("getstatus: Error sending getstatus message to %s:%d\n%s" % (ADDRESS[0],ADDRESS[1],str(e)) )
            return
        while True:
            try:
                buf = s.recvfrom(1024*4)[0]
            except socket.timeout:
                logfile("getstatus: Receive connection timed out(500ms) %s:%d" % ADDRESS )
                s.close()
                return
            except OSError as e:
                logfile("getstatus: Error receiving data %s:%d\n%s" % (ADDRESS[0],ADDRESS[1],str(e)) )
                return
            if buf:
                buf = buf[4:].decode()
            if buf.startswith('statusResponse\n'):
                ping_end = time()
                Server['ping'] = int( (ping_end-ping_start)*1000 )
                logfile("getstatus: Got response from %s:%d in %dms" % (ADDRESS[0],ADDRESS[1],Server['ping']) )
                self.getStatusResponse(buf.replace('statusResponse\n',''),serverid)
                break
            else:
                break
        s.close()
        
    def getStatusResponse(self,buffer=None,serverid=None):
        if not buffer or serverid == None or not self.Servers[serverid]: return
        logfile("Received %d bytes buffer" % len(buffer) )
        gamedata = buffer.split('\\')
        Server = self.Servers[serverid]
        if not gamedata:
            logfile("getstatusresponse: Invalid response from %s" % Server['address'] )
            return
        Server['cvar']       = {}
        Server['playerlist'] = []
        Server['players']    = "-"
        Server['map']        = ""
        Server['fs_game']    = 'etmain'
        isCvarName = True
        cvarName   = ""
        cvarValue  = ""
        for key in gamedata:
            key = key.strip()
            if not key: continue
            if isCvarName:
                cvarName = key.lower()
                isCvarName=False
            else:
                if '\n' in key:
                    players = key.split('\n')
                    Server['cvar'][cvarName] = players[0]
                    del players[0]
                    self.getPlayerData(players,serverid)
                    break
                cvarValue=key
                Server['cvar'][cvarName] = cvarValue
                isCvarName=True
        if "mapname" in Server['cvar']: Server['map'] = Server['cvar']['mapname']
    def getPlayerData(self,players,serverid):
        if not players or serverid == None or not self.Servers[serverid]: return
        Server = self.Servers[serverid]
        for playerstring in players:
            playerstring = playerstring.strip()
            if playerstring == '': continue
            m = playermatch.match(playerstring)
            if not m: continue
            Server['playerlist'].append({ 'name':m.group(3) , 'ping':int(m.group(2)) , 'score':int(m.group(1)) })
            
