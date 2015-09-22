import json
from os.path import isfile
from re import compile
import socket
from time import time
from zelly.constants import logfile

ip_match = compile("(%d+%.%d+%.%d+%.%d+)")
player_match = compile("(\d+) (\d+) \"(.*)\"")


def get_ip(d):
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except socket.herror:
        return None


class ServerData:
    def __init__(self):
        self.Servers = []
        self.fs_homepath = ""
        self.fs_basepath = ""
        self.ETPath = ""
        self.parameters = ""

    def load_server_file(self, filename):
        if not filename:
            logfile("load_server_file: No filepath given")
            return
        if not isfile(filename):
            logfile("load_server_file: %s is not a file" % filename)
            return
        with open(filename) as jsonfile:
            serversjson = json.load(jsonfile)
        if not serversjson or "Servers" not in serversjson or not serversjson['Servers']:
            logfile("load_server_file: No servers loaded from file")
            self.Servers = []
            return
        self.Servers = serversjson['Servers']
        for Server in self.Servers:
            Server['map'] = ''
            Server['ping'] = -1
            Server['players'] = '-'
            Server['playerlist'] = []
            Server['cvar'] = {}
            Server['laststatus'] = 0
        self.fs_basepath = serversjson['fs_basepath'] if 'fs_basepath' in serversjson else ''
        self.fs_homepath = serversjson['fs_homepath'] if 'fs_homepath' in serversjson else ''
        self.ETPath = serversjson['ETPath'] if 'ETPath' in serversjson else ''
        self.parameters = serversjson['parameters'] if 'parameters' in serversjson else ''
        logfile("load_server_file: Loaded %d servers" % len(self.Servers))

    def save_server_file(self, filename):
        if not filename:
            logfile("save_server_file: No filepath given")
            return
        delete_list = ["map", "ping", "players", "playerlist", "cvar", "laststatus", "fs_game"]
        for Server in self.Servers:
            for delete_list_item in delete_list:
                if delete_list_item in Server:
                    del Server[delete_list_item]

        json_file = open(filename, 'w')
        json.dump({'fs_basepath': self.fs_basepath, 'fs_homepath': self.fs_homepath, 'ETPath': self.ETPath,
                   'parameters': self.parameters, 'Servers': self.Servers}, json_file, skipkeys=False, allow_nan=False,
                  sort_keys=True, indent=4)
        logfile("save_server_file: Saved %d servers" % len(self.Servers))

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

    def add_server(self, server):
        if not server:
            logfile("add_server: No serverdata given")
            return
        if not type(server) is dict:
            logfile("add_server: Serverdata was not valid type")
            return
        if 'title' not in server:
            logfile("add_server: Server requires title")
            return
        if 'address' not in server:
            logfile("add_server: Server requires address")
            return
        if any(s['title'] == server['title'] for s in self.Servers):
            logfile("add_server: %s title already exists" % server['title'])
            return
        if any(s['address'] == server['address'] for s in self.Servers):
            logfile("add_server: %s address already exists" % server['address'])
            return

        # TODO Add rcon
        # map is a temp variable
        for set_empty in ["password", "fs_homepath", "fs_basepath", "ETPath", "parameters", "map"]:
            if set_empty not in server:
                server[set_empty] = ""

        # Set other temp variables
        server['map'] = ''
        server['ping'] = -1
        server['players'] = '-'
        server['playerlist'] = []
        server['cvar'] = {}
        server['laststatus'] = 0
        server['fs_game'] = 'etmain'

        self.Servers.append(server)
        logfile("add_server: %s(%s) server was added" % (server['title'], server['address']))

    def getstatus(self, server_id=None):
        if server_id is None or not self.Servers[server_id]:
            logfile("getstatus: Invalid server id (%s)" % str(server_id))
            return

        server = self.Servers[server_id]
        current = time()
        if server['laststatus'] != 0 and (current - server['laststatus']) < 2:
            logfile("getstatus: Too many status checks in short time")
            return
        server['laststatus'] = current

        ip = server['address']
        port = "27960"
        if ":" in ip:
            ip = server['address'].split(':')[0].strip()
            port = server['address'].split(':')[1].strip()
        if not ip_match.match(ip):
            old_hostname = ip
            ip = get_ip(ip)
            logfile("getstatus: resolved %s from %s" % (ip, old_hostname))

        port = int(port)
        if not ip:
            logfile("getstatus: %s was not a valid ip" % (str(ip)))
            return
        if not port:
            logfile("getstatus: %s was not a valid port" % (str(port)))
            return
        ip = ip.replace('\"', "").replace("'", '')
        logfile("getstatus: %s:%s" % (str(ip), str(port)))
        address = (ip, port)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
        except OSError as e:
            logfile("getstatus: Error creating socket for %s:%d\n%s" % (address[0], address[1], str(e)))
            return
        ping_start = time()
        try:
            logfile(b'getstatus: \xff\xff\xff\xffgetstatus')
            logfile(str(s.sendto(b'\xff\xff\xff\xffgetstatus', address)) + " bytes sent")
        except socket.timeout:
            s.close()
            logfile("getstatus: Send connection timed out(500ms) for %s:%d" % address)
            return
        except OSError as e:
            s.close()
            logfile("getstatus: Error sending getstatus message to %s:%d\n%s" % (address[0], address[1], str(e)))
            return
        while True:
            try:
                buf = s.recvfrom(1024 * 4)[0]
            except socket.timeout:
                logfile("getstatus: Receive connection timed out(500ms) %s:%d" % address)
                s.close()
                return
            except OSError as e:
                logfile("getstatus: Error receiving data %s:%d\n%s" % (address[0], address[1], str(e)))
                return
            if buf:
                buf = buf[4:].decode()
            if buf.startswith('statusResponse\n'):
                ping_end = time()
                server['ping'] = int((ping_end - ping_start) * 1000)
                logfile("getstatus: Got response from %s:%d in %dms" % (address[0], address[1], server['ping']))
                self.getstatus_response(buf.replace('statusResponse\n', ''), server_id)
                break
            else:
                break
        s.close()

    def getstatus_response(self, buffer=None, server_id=None):
        if not buffer or server_id is None or not self.Servers[server_id]:
            return
        logfile("Received %d bytes buffer" % len(buffer))
        game_data = buffer.split('\\')
        server = self.Servers[server_id]
        if not game_data:
            logfile("getstatus_response: Invalid response from %s" % server['address'])
            return
        server['cvar'] = {}
        server['playerlist'] = []
        server['players'] = "-"
        server['map'] = ""
        server['fs_game'] = 'etmain'
        is_cvar_name = True
        cvar_name = ""
        # noinspection PyUnusedLocal
        cvar_value = ""
        for key in game_data:
            key = key.strip()
            if not key:
                continue
            if is_cvar_name:
                cvar_name = key.lower()
                is_cvar_name = False
            else:
                if '\n' in key:
                    players = key.split('\n')
                    server['cvar'][cvar_name] = players[0]
                    del players[0]
                    self.get_player_data(players, server_id)
                    break
                cvar_value = key
                server['cvar'][cvar_name] = cvar_value
                is_cvar_name = True
        if "mapname" in server['cvar']:
            server['map'] = server['cvar']['mapname']

    def get_player_data(self, players, server_id):
        if not players or server_id is None or not self.Servers[server_id]:
            return
        server = self.Servers[server_id]
        for player_string in players:
            player_string = player_string.strip()
            if not player_string:
                continue
            m = player_match.match(player_string)
            if not m:
                continue
            server['playerlist'].append({'name': m.group(3), 'ping': int(m.group(2)), 'score': int(m.group(1))})
