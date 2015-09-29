import json
from os.path import isfile
from re import compile
import socket
from zelly.constants import logfile
import threading
from queue import Queue
import time

ip_match = compile("(%d+%.%d+%.%d+%.%d+)")
player_match = compile("(\d+) (\d+) \"(.*)\"")


def get_ip(d):
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except socket.herror:
        return None


def get_ip_port_from_address(address):
    if not address:
        logfile("get_ip_port_from_address: no address given")
        return None
    ip = address
    port = "27960"
    if ":" in ip:
        ip = address.split(':')[0].strip()
        port = address.split(':')[1].strip()
    if not ip_match.match(ip):
        ip = get_ip(ip)
    ip = ip.replace('\"', '').replace('\'', '')  # Idk why i need this
    port = int(port)
    if not ip:
        logfile("get_ip_port_from_address: %s was not a valid ip" % str(ip))
        return None
    if not port:
        logfile("get_ip_port_from_address: %s was not a valid port" % str(port))
        return None

    logfile("get_ip_port_from_address: %s resolved to ( %s , %d )" % (address, ip, port))
    tmp_address = (ip, port)
    return tmp_address


def getstatus_response(server, buffer=""):
    if server is None:
        logfile("getstatus_response: server is missing")
        return
    buffer = buffer.strip().replace("statusResponse\n", '')
    if not buffer:
        logfile("getstatus_response: buffer is empty")
        return

    game_data = buffer.split('\\')
    if not game_data:
        logfile("getstatus_response: invalid response from %s" % server['address'])
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
                get_player_data(server, players)
                break
            cvar_value = key
            server['cvar'][cvar_name] = cvar_value
            is_cvar_name = True
    if "mapname" in server['cvar']:
        server['map'] = server['cvar']['mapname']


def get_player_data(server, players):
    if server is None:
        logfile("get_player_data: server is invalid")
        return
    if not players:
        logfile("get_player_data: players is empty")
        return
    for player_string in players:
        player_string = player_string.strip()
        if not player_string:
            continue
        m = player_match.match(player_string)
        if not m:
            continue
        server['playerlist'].append({'name': m.group(3), 'ping': int(m.group(2)), 'score': int(m.group(1))})


def rcon_response(server, buffer=""):
    if server is None:
        logfile("rcon_response: server is missing")
        return
    buffer = buffer.replace("print\n", '')
    if not buffer:
        logfile("rcon_response: buffer is empty")
        return
    logfile("rcon_response: %s" % buffer.replace('\n', '/'))
    server['rcon_lines'] += buffer

key_list = [
    {'name': 'map', 'default': '', 'tmp': True},
    {'name': 'ping', 'default': -1, 'tmp': True},
    {'name': 'players', 'default': '-', 'tmp': True},
    {'name': 'playerlist', 'default': [], 'tmp': True},
    {'name': 'cvar', 'default': {}, 'tmp': True},
    {'name': 'laststatus', 'default': 0, 'tmp': True},
    {'name': 'rcon_lines', 'default': "", 'tmp': True},
    {'name': 'fs_game', 'default': '', 'tmp': True},
    {'name': 'fs_homepath', 'default': '', 'tmp': False},
    {'name': 'fs_basepath', 'default': '', 'tmp': False},
    {'name': 'ETPath', 'default': '', 'tmp': False},
    {'name': 'parameters', 'default': '', 'tmp': False},
    {'name': 'password', 'default': '', 'tmp': False},
    {'name': 'rcon', 'default': '', 'tmp': False},
    {'name': 'title', 'default': '', 'tmp': False},
]


def create_server_from_data(server):
    for key in key_list:
        if key['name'] not in server:
            server[key['name']] = key['default']


def delete_temp_keys_from_server(server):
    for key in key_list:
        if key['name'] not in server:
            server[key['name']] = key['default']
        if key['tmp'] and key['name'] in server:
            del server[key['name']]


# noinspection PyTypeChecker
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
        for server in self.Servers:
            create_server_from_data(server)
        self.fs_basepath = serversjson['fs_basepath'] if 'fs_basepath' in serversjson else ''
        self.fs_homepath = serversjson['fs_homepath'] if 'fs_homepath' in serversjson else ''
        self.ETPath = serversjson['ETPath'] if 'ETPath' in serversjson else ''
        self.parameters = serversjson['parameters'] if 'parameters' in serversjson else ''
        logfile("load_server_file: Loaded %d servers" % len(self.Servers))

    def save_server_file(self, filename):
        if not filename:
            logfile("save_server_file: No filepath given")
            return

        for server in self.Servers:
            delete_temp_keys_from_server(server)

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

        create_server_from_data(server)

        self.Servers.append(server)
        logfile("add_server: %s(%s) server was added" % (server['title'], server['address']))

    def get_server(self, server):
        if server is None:
            return None
        if type(server) is int:
            if self.Servers[server]:
                return self.Servers[server]
            else:
                return None
        return server

    def send_message(self, server, message, receive_callback, buff_length=4096, timeout_length=1.0,
                     wait_for_multiple=False):
        server = self.get_server(server)
        if server is None:
            logfile("send_message: server is not valid")
            return
        if not message:
            logfile("send_message: message empty")
            return
        try:
            message = b'\xff\xff\xff\xff' + message.encode()
        except UnicodeError:
            logfile("send_message: error converting message to bytes")
            return

        address = get_ip_port_from_address(server['address'])

        if address is None:
            return None

        # Create socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout_length)
        except OSError as e:
            logfile("send_message: Error creating socket for %s:%d\n\t%s" % (address[0], address[1], str(e)))
            return
        # Send the message
        if not wait_for_multiple:
            current_time_msec = time.time()  # Get time of response
            server['laststatus'] = current_time_msec
        logfile("send_message: sending message %s" % message.decode(errors="ignore"))  # Display message somehow
        try:
            bytes_sent = s.sendto(message, address)
        except socket.timeout:
            s.close()
            logfile("send_message: send connection to %s:%d timed out(500ms)" % (address[0], address[1]))
            return
        except OSError as e:
            s.close()
            logfile("send_message: error sending message to %s:%d\n\t%s" % (address[0], address[1], str(e)))
            return

        logfile("send_message: %d bytes sent to %s:%d" % (bytes_sent, address[0], address[1]))
        total_buf = ""

        # Just a little confused if I have done this correctly
        # On very large messages (Example switching maps, where it displays all the map loading information)
        # It will only show 1 message
        while True:
            try:
                recv = s.recvfrom(buff_length)
            except socket.timeout:
                logfile("send_message: Receive connection timed out(%dms) %s:%d" % (timeout_length*1000, address[0],
                                                                                    address[1]))
                s.close()
                if total_buf:
                    break
                else:
                    return
            except OSError as e:
                logfile("send_message: Error receiving data %s:%d\n\t%s" % (address[0], address[1], str(e)))
                return
            if recv:
                try:
                    tmp_buf = recv[0][4:].decode()
                    total_buf += tmp_buf  # truncate the first 4 bytes
                except UnicodeError as uni_error:
                    logfile("send_message: can not decode buffer response\n\t%s" % uni_error)
                    return
                logfile("send_message: received %d bytes from %s:%d" % (len(recv[0]), recv[1][0], recv[1][1]))
                receive_callback(server, tmp_buf)
                if not wait_for_multiple:
                    break
            else:
                break  # Did not receive
        s.close()
        if not wait_for_multiple:
            # noinspection PyUnboundLocalVariable
            server['ping'] = int((time.time() - current_time_msec) * 1000)
            logfile("send_message: received %d total bytes buffer" % len(total_buf))
            receive_callback(server, total_buf)

    def getstatus(self, server):
        self.send_message(server, "getstatus", getstatus_response)

    def rcon_message(self, server, command=""):
        if not server['rcon']:
            logfile("rcon_message: no rcon password is set")
            return
        command = command.strip()
        if not command:
            logfile("rcon_message: command is empty")
            return
        logfile("rcon_message_send: %s" % command)

        # noinspection PyUnusedLocal
        lock = threading.Lock()

        def tmp_task_worker():
            self.send_message(server, "rcon %s %s" % (server['rcon'], command), rcon_response, 256, 2.0, True)

        t = threading.Thread(target=tmp_task_worker)
        t.daemon = True
        t.start()

    def getstatus_all(self):
        logfile("getstatus_all: creating thread dispatcher")
        dispatcher = ThreadDispatcher()
        dispatcher.sd = self
        logfile("getstatus_all: adding getstatus requests to dispatcher")
        for server in self.Servers:
            dispatcher.add_task(server)

        logfile("getstatus_all: starting thread dispatcher")
        dispatcher.start()
        logfile("getstatus_all: completed thread dispatcher")


class ThreadDispatcher:
    def __init__(self):
        self.lock = threading.Lock()  # Lock to serialize console output
        self.queue = Queue()
        self.sd = None
        for i in range(4):  # 4 threads
            t = threading.Thread(target=self.task_worker)
            t.daemon = True
            t.start()

    def task_worker(self):
        while True:
            server = self.queue.get()
            self.sd.getstatus(server)
            self.queue.task_done()

    def add_task(self, server):
        self.queue.put(server)

    def start(self):
        start = time.perf_counter()
        self.queue.join()
        print('thread_total_time: ', time.perf_counter() - start)
