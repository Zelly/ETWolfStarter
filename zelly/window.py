import json
from os import getcwd
from os.path import isfile, join, isdir
from re import compile
from subprocess import call
from tkinter import *  # @UnusedWildImport
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.simpledialog

from zelly.serverdata import ServerData

WINDOW_BACKGROUND        = "#FFFFFF"  # "#F8F8F8"
WINDOW_BORDER            = "#000008"
ENTRY_BACKGROUND         = "#FFFFF9"
ENTRY_FOREGROUND         = "#000000"
LIST_SELECT_FORE         = "#FFFFFF"
LIST_SELECT_BACK         = "#00001F"
BUTTON_BACKGROUND        = "#B280B2"  # 0099F0
BUTTON_FOREGROUND        = "#FFFFFF"
A_BUTTON_BACKGROUND      = "#660066"  # 0000FF
A_BUTTON_FOREGROUND      = "#FFFFFF"
BROWSE_BUTTON_BACKGROUND   = "#B280B2"  # 0099F0
BROWSE_BUTTON_FOREGROUND   = "#FFFFFF"
BROWSE_A_BUTTON_BACKGROUND = "#660066"  # 0000FF
BROWSE_A_BUTTON_FOREGROUND = "#FFFFFF"
NAVBAR_BACKGROUND        = "#B280B2"
HEADER_BACKGROUND        = "#FFFFFF"
SERVERLIST_BACKGROUND    = "#FFFFFF"
SERVERDATA_BACKGROUND    = "#FFFFFF"
SERVERSTATUS_BACKGROUND  = "#FFFFFF"
PLAYER_NAME_LENGTH       = 32
PLAYER_PING_LENGTH       = 8
PLAYER_SCORE_LENGTH      = 12
SERVERSTATUS_TEXT_LENGTH = 54
clean_pattern = compile("(\^[\d\.\w=\-]?)")

def cleanstr(s):
    return clean_pattern.sub("", s)
def logfile(msg): # Probably bad way of doing this oh well
    print(msg)
    with open("wolfstarter.log","a") as errorlog:
        errorlog.write('%s\n' % msg)

class MenuButton(Button):
    def __init__(self, master=None, column=0, row=0, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        self.master = master
        self.config(
                    background=BUTTON_BACKGROUND,
                    foreground=BUTTON_FOREGROUND,
                    activebackground=A_BUTTON_BACKGROUND,
                    activeforeground=A_BUTTON_FOREGROUND,
                    borderwidth=0,
                    width=5,
                    height=2,
                    relief="flat",
                    padx=12,
                    cursor="hand2",
                )
        self.row = row
        self.column = column
        self.hide()
    def show(self):
        self.grid(row=self.row, column=self.column, sticky=W)
    def hide(self):
        self.grid_forget()

class NavBar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(
                   background=NAVBAR_BACKGROUND , cursor="hand1"
                   )
        self.button_open = MenuButton(self , 0 , text="Open..."    , command=parent.openfile)
        self.button_saveas = MenuButton(self , 1 , text="Save..."  , command=parent.saveasfile)
        self.button_minimize = MenuButton(self , 6 , text="Minimize"  , command=self.minimize)
        self.button_quit = MenuButton(self , 7 , text="Quit"       , command=parent.quit)
        
        self.button_open.show()
        self.button_saveas.show()
        self.button_minimize.show()
        self.button_quit.show()
        
        self.grid(column=0, row=0, sticky=N + W + E + S)
        # self.columnconfigure(10,weight=1)
    def minimize(self):
        # I guess tkinter does not have the ability to go to system tray
        self.parent.parent.overrideredirect(False)
        self.parent.parent.iconify()
class BrowseButton(Button):
    def __init__(self, master=None, dir_var=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        self.parent = master
        self.config(background=BROWSE_BUTTON_BACKGROUND,
                    foreground=BROWSE_BUTTON_FOREGROUND,
                    activebackground=BROWSE_A_BUTTON_BACKGROUND,
                    activeforeground=BROWSE_A_BUTTON_FOREGROUND,
                    borderwidth=0,
                    # width           = 5,
                    # height          = 2,
                    relief="flat",
                    padx=5,
                    cursor="hand2")
class ServerFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.config(background=WINDOW_BACKGROUND, padx=5, pady=5)
        
        font = tkinter.font.Font(family="Courier New", size=10)
        self.currentline = 1
        self.header_frame = Frame(self, background=HEADER_BACKGROUND)
        
        # Global ETPath
        self.etpath_var = StringVar()
        self.etpath_label = Label(self.header_frame, text="ET: ", font=font, background=HEADER_BACKGROUND)
        self.etpath_entry = Entry(self.header_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.etpath_var)
        self.etpath_browse = BrowseButton(self.header_frame, text="Browse...", command=lambda :self.getfilepath(self.etpath_var, self.updateconfig))
        self.etpath_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.etpath_label.grid(row=0, column=0, sticky=N + W)
        self.etpath_entry.grid(row=0, column=1, sticky=N + W + E)
        self.etpath_browse.grid(row=0, column=2, sticky=N + E)
        
        # Global fs_basepath
        self.fs_basepath_var = StringVar()
        self.fs_basepath_label = Label(self.header_frame, text="fs_basepath: ", font=font, background=HEADER_BACKGROUND)
        self.fs_basepath_entry = Entry(self.header_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.fs_basepath_var)
        self.fs_basepath_browse = BrowseButton(self.header_frame, text="Browse...", command=lambda :self.getpath(self.fs_basepath_var, self.updateconfig))
        self.fs_basepath_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.fs_basepath_label.grid(row=1, column=0, sticky=N + W)
        self.fs_basepath_entry.grid(row=1, column=1, sticky=N + W + E)
        self.fs_basepath_browse.grid(row=1, column=2, sticky=N + E)
        
        # Global fs_homepath
        self.fs_homepath_var = StringVar()
        self.fs_homepath_label = Label(self.header_frame, text="fs_homepath: ", font=font, background=HEADER_BACKGROUND)
        self.fs_homepath_entry = Entry(self.header_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.fs_homepath_var)
        self.fs_homepath_browse = BrowseButton(self.header_frame, text="Browse...", command=lambda :self.getpath(self.fs_homepath_var, self.updateconfig))
        self.fs_homepath_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.fs_homepath_label.grid(row=2, column=0, sticky=N + W)
        self.fs_homepath_entry.grid(row=2, column=1, sticky=N + W + E)
        self.fs_homepath_browse.grid(row=2, column=2, sticky=N + E)
        
        # Global Parameters
        self.parameters_var = StringVar()
        self.parameters_label = Label(self.header_frame, text="Parameters: ", font=font, background=HEADER_BACKGROUND)
        self.parameters_entry = Entry(self.header_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.parameters_var)
        self.parameters_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.parameters_label.grid(row=3, column=0, sticky=N + W)
        self.parameters_entry.grid(row=3, column=1, sticky=N + W + E)
        
        if self.parent.serverdata.fs_basepath: self.fs_basepath_var.set(self.parent.serverdata.fs_basepath)
        if self.parent.serverdata.fs_homepath: self.fs_homepath_var.set(self.parent.serverdata.fs_homepath)
        if self.parent.serverdata.parameters: self.parameters_var.set(self.parent.serverdata.parameters)
        if self.parent.serverdata.ETPath: self.etpath_var.set(self.parent.serverdata.ETPath)
        
        # Server List Frame
        self.serverlist_frame = Frame(self, background=SERVERLIST_BACKGROUND)
        
        # Server List Titles
        self.servers_label = Label(self.serverlist_frame, text="Title", font=font, background=SERVERLIST_BACKGROUND)
        self.servers = Listbox(self.serverlist_frame, width=25, relief="flat",
                               borderwidth=0,
                               font=font,
                               selectbackground=LIST_SELECT_BACK,
                               selectborderwidth=0,
                               selectforeground=LIST_SELECT_FORE,
                               exportselection=0,
                               activestyle="none")
        self.servers.bind("<<ListboxSelect>>", self.selectserver)
        self.servers.bind("<Double-Button-1>", self.joinserver)
        self.servers.bind("<MouseWheel>", self.OnMouseWheel)
        self.servers_label.grid(row=0, column=0, sticky=N + W + E)
        self.servers.grid(row=1, column=0, sticky=N + W + E)
        
        # Server Map
        self.servermap_label = Label(self.serverlist_frame, text="Map", font=font, background=SERVERLIST_BACKGROUND)
        self.servermap = Listbox(self.serverlist_frame, width=10, relief="flat",
                               borderwidth=0,
                               font=font,
                               selectbackground=LIST_SELECT_BACK,
                               selectborderwidth=0,
                               selectforeground=LIST_SELECT_FORE,
                               exportselection=0,
                               activestyle="none")
        self.servermap.bind("<<ListboxSelect>>", self.selectserver)
        self.servermap.bind("<Double-Button-1>", self.joinserver)
        self.servermap.bind("<MouseWheel>", self.OnMouseWheel)
        self.servermap_label.grid(row=0, column=1, sticky=N + W + E)
        self.servermap.grid(row=1, column=1, sticky=N + W + E)
        
        # Server Players
        self.serverplayers_label = Label(self.serverlist_frame, text="Players", font=font, background=SERVERLIST_BACKGROUND)
        self.serverplayers = Listbox(self.serverlist_frame, width=10, relief="flat",
                               borderwidth=0,
                               font=font,
                               selectbackground=LIST_SELECT_BACK,
                               selectborderwidth=0,
                               selectforeground=LIST_SELECT_FORE,
                               exportselection=0,
                               activestyle="none")
        self.serverplayers.bind("<<ListboxSelect>>", self.selectserver)
        self.serverplayers.bind("<Double-Button-1>", self.joinserver)
        self.serverplayers.bind("<MouseWheel>", self.OnMouseWheel)
        self.serverplayers_label.grid(row=0, column=2, sticky=N + W + E)
        self.serverplayers.grid(row=1, column=2, sticky=N + W + E)
        
        # Server Ping
        self.serverping_label = Label(self.serverlist_frame, text="Ping", font=font, background=SERVERLIST_BACKGROUND)
        self.serverping = Listbox(self.serverlist_frame, width=10, relief="flat",
                               borderwidth=0,
                               font=font,
                               selectbackground=LIST_SELECT_BACK,
                               selectborderwidth=0,
                               selectforeground=LIST_SELECT_FORE,
                               exportselection=0,
                               activestyle="none")
        self.serverping.bind("<<ListboxSelect>>", self.selectserver)
        self.serverping.bind("<Double-Button-1>", self.joinserver)
        self.serverping.bind("<MouseWheel>", self.OnMouseWheel)
        self.serverping_label.grid(row=0, column=3, sticky=N + W + E)
        self.serverping.grid(row=1, column=3, sticky=N + W + E)
        
        # Server Data Frame
        self.serverdata_frame = Frame(self, background=SERVERDATA_BACKGROUND)
        
        # Server title
        self.servertitle_var = StringVar()
        self.servertitle_label = Label(self.serverdata_frame, text="Title: ", font=font, background=SERVERDATA_BACKGROUND)
        self.servertitle_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.servertitle_var)
        self.servertitle_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.servertitle_label.grid(row=0, column=0, sticky=N + W)
        self.servertitle_entry.grid(row=0, column=1, sticky=N + W + E)
        
        # Server Password
        self.serverpassword_var = StringVar()
        self.serverpassword_label = Label(self.serverdata_frame, text="Password: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serverpassword_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serverpassword_var)
        self.serverpassword_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        
        # Server address
        self.serveraddress_var = StringVar()
        self.serveraddress_label = Label(self.serverdata_frame, text="Address: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serveraddress_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serveraddress_var)
        self.serveraddress_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.serveraddress_label.grid(row=2, column=0, sticky=N + W)
        self.serveraddress_entry.grid(row=2, column=1, sticky=N + W + E)
        
        # Server ETPath
        self.serveretpath_var = StringVar()
        self.serveretpath_label = Label(self.serverdata_frame, text="ET: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serveretpath_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serveretpath_var)
        self.serveretpath_browse = BrowseButton(self.serverdata_frame, text="Browse...", command=lambda :self.getfilepath(self.serveretpath_var, self.updateserver))
        self.serveretpath_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.serveretpath_label.grid(row=3, column=0, sticky=N + W)
        self.serveretpath_entry.grid(row=3, column=1, sticky=N + W + E)
        self.serveretpath_browse.grid(row=3, column=2, sticky=N + E)
        
        # Server fs_basepath
        self.serverfs_basepath_var = StringVar()
        self.serverfs_basepath_label = Label(self.serverdata_frame, text="fs_basepath: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serverfs_basepath_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serverfs_basepath_var)
        self.serverfs_basepath_browse = BrowseButton(self.serverdata_frame, text="Browse...", command=lambda :self.getpath(self.serverfs_basepath_var, self.updateserver))
        self.serverfs_basepath_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.serverfs_basepath_label.grid(row=4, column=0, sticky=N + W)
        self.serverfs_basepath_entry.grid(row=4, column=1, sticky=N + W + E)
        self.serverfs_basepath_browse.grid(row=4, column=2, sticky=N + E)
        
        # Server fs_homepath
        self.serverfs_homepath_var = StringVar()
        self.serverfs_homepath_label = Label(self.serverdata_frame, text="fs_homepath: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serverfs_homepath_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serverfs_homepath_var)
        self.serverfs_homepath_browse = BrowseButton(self.serverdata_frame, text="Browse...", command=lambda :self.getpath(self.serverfs_homepath_var, self.updateserver))
        self.serverfs_homepath_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.serverfs_homepath_label.grid(row=5, column=0, sticky=N + W)
        self.serverfs_homepath_entry.grid(row=5, column=1, sticky=N + W + E)
        self.serverfs_homepath_browse.grid(row=5, column=2, sticky=N + E)
        
        # Server extra parameters
        self.serverparams_var = StringVar()
        self.serverparams_label = Label(self.serverdata_frame, text="Parameters: ", font=font, background=SERVERDATA_BACKGROUND)
        self.serverparams_entry = Entry(self.serverdata_frame, font=font, background=ENTRY_BACKGROUND, foreground=ENTRY_FOREGROUND, textvariable=self.serverparams_var)
        self.serverparams_entry.bind(sequence='<KeyRelease>', func=self.updateserver)
        self.serverparams_label.grid(row=6, column=0, sticky=N + W)
        self.serverparams_entry.grid(row=6, column=1, sticky=N + W + E)
        
        # Server Status Frame #
        self.serverstatus_frame = Frame(self, background=WINDOW_BACKGROUND)
        
        self.text = Text(
                         self.serverstatus_frame,
                         background=WINDOW_BACKGROUND,
                         font=font,
                         relief="flat",
                         wrap="none",
                         width=54,
                         height=29,
                         )

        self.text.tag_config("headerLine", foreground=BUTTON_FOREGROUND, background=BUTTON_BACKGROUND, underline=1)
        
        self.text.grid(sticky=W + N)
        
        self.text_scroll = Scrollbar(self.serverstatus_frame, command=self.text.yview, background=BUTTON_BACKGROUND)
        self.text.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.grid(row=0, column=1, sticky="ns")
        # End Server Status Frame #
        
        self.button_addserver = MenuButton(self.parent.navbar , 3 , text="Add"        , command=self.addserver)
        self.button_removeserver = MenuButton(self.parent.navbar , 4 , text="Remove"     , command=self.removeserver)
        # self.button_rcon         = MenuButton( self.parent.navbar , 5 , text="Rcon"       , command=parent.rcon)
        self.button_joinserver = MenuButton(self.parent.navbar , 6 , text="Join"       , command=self.joinserver)
        self.button_addserver.show()
        
        # Bring it all together
        self.create_server_list()
        self.header_frame.grid_columnconfigure(1, minsize=400)
        self.header_frame.grid(row=0, column=0, sticky=N + W + E)
        self.serverlist_frame.grid_columnconfigure(0, weight=1)
        self.serverlist_frame.grid(row=1, column=0, sticky=N + W)
        self.serverdata_frame.grid_columnconfigure(1, minsize=400)
        # self.serverstatus_frame.grid(row=0,column=1,sticky=N+W,rowspan=2)
        
        self.notice_var = StringVar()
        self.notice_var.set("FS_Basepath and FS_Homepath are not required.\nThey will be set to the folder of you ET.exe if not specfied.")
        self.notice_label = Label(self,font=font,background=WINDOW_BACKGROUND,textvariable=self.notice_var)
        self.notice_label.grid(row=4, column=0, sticky=N + W,rowspan=2)
        
        
        self.grid(sticky=W + S + N + E)
    def refresh_list(self, selectid=None):
        self.servers.selection_clear(0, END)
        self.servers.delete(0, END)
        self.servermap.selection_clear(0, END)
        self.servermap.delete(0, END)
        self.serverplayers.selection_clear(0, END)
        self.serverplayers.delete(0, END)
        self.serverping.selection_clear(0, END)
        self.serverping.delete(0, END)
        for Server in self.parent.serverdata.Servers:
            self.servers.insert(END, Server['title'])
            self.servermap.insert(END, Server['map'])
            self.serverplayers.insert(END, Server['players'])
            self.serverping.insert(END, Server['ping'])
        if selectid:
            self.servers.select_set(selectid)
            self.servermap.select_set(selectid)
            self.serverplayers.select_set(selectid)
            self.serverping.select_set(selectid)
    def create_server_list(self):
        self.serverstatus_frame.grid_forget()
        self.serverdata_frame.grid_forget()
        self.servertitle_var.set('')
        self.serveraddress_var.set('')
        self.serverpassword_var.set('')
        self.serverparams_var.set('')
        self.serverfs_basepath_var.set('')
        self.serverfs_homepath_var.set('')
        self.serveretpath_var.set('')
        self.button_joinserver.hide()
        self.button_removeserver.hide()
        for x in range(0, len(self.parent.serverdata.Servers)):
            self.serverstatus(x)
        self.refresh_list(None)
    # Buttons
    def addserver(self):  # Leaving error checking up to the join command
        servertitle = tkinter.simpledialog.askstring("New Server Title", "Please insert a unique server title")
        if not servertitle or any(s['title'] == servertitle for s in self.parent.serverdata.Servers):
            logfile("Invalid server title")
            return
        serveraddress = tkinter.simpledialog.askstring("New Server Address", "Please insert full server address.(unique)\nExample: 127.0.0.1:27960\nIf it is a hostname make sure you have the port at the end")
        if not serveraddress or any(s['address'] == serveraddress for s in self.parent.serverdata.Servers):
            logfile("Invalid server address")
            return
        self.parent.serverdata.add_server({'address':serveraddress, 'title':servertitle})
        self.create_server_list()
        # Select latest server
        self.servers.select_set(END)
        self.servermap.select_set(END)
        self.serverplayers.select_set(END)
        self.serverping.select_set(END)
        self.selectserver(None)
    def getselection(self):
        if self.servers.curselection(): return self.servers.curselection()
        if self.servermap.curselection(): return self.servermap.curselection()
        if self.serverping.curselection(): return self.serverping.curselection()
        if self.serverplayers.curselection(): return self.serverplayers.curselection()
        return None
    def removeserver(self):
        if not self.getselection(): return
        if not self.parent.serverdata.Servers[self.getselection()[0]]:
            logfile("Error updating server %d" % self.getselection()[0])
            return
        del self.parent.serverdata.Servers[self.getselection()[0]]
        self.create_server_list()
    def getcommandline(self):
        if not self.getselection(): return
        Server = self.parent.serverdata.Servers[self.getselection()[0]]
        if not Server:
            logfile("Error updating server %d" % self.getselection()[0])
            return
        logfile("Joining server %s" % Server['title'])
        # Generate Startup Line #
        etpath      = ''
        fs_basepath = ''
        fs_homepath = ''
        fs_game     = 'etmain'
        parameters  = ''
        address     = Server['address']
        password    = Server['password']
        if Server['ETPath']:
            etpath = Server['ETPath']
        else:
            etpath = self.parent.serverdata.ETPath
        if Server['fs_basepath']:
            fs_basepath = Server['fs_basepath']
        else:
            fs_basepath = self.parent.serverdata.fs_basepath
        if Server['fs_homepath']:
            fs_homepath = Server['fs_homepath']
        else:
            fs_homepath = self.parent.serverdata.fs_homepath
        
        if self.parent.serverdata.parameters:
            parameters = self.parent.serverdata.parameters
        if Server['parameters']:
            if parameters:
                parameters += ' '
            parameters += Server['parameters']
        
        if not fs_basepath:
            fs_basepath = "/".join(etpath.replace('\\', '/').split("/")[0:-1])
        if not fs_homepath:
            fs_homepath = fs_basepath
            
        if self.parent.Config['launchmod']:
            if "gamename" in Server['cvar']:
                fs_game = Server['cvar']['gamename']
            if not isdir(join(fs_basepath,fs_game)):
                logfile("Mod path doesn't exist")
                fs_game='etmain'
                
        if not address:
            logfile("Address not valid")
            return
        if not isfile(etpath):
            logfile("ET Executable is not valid")
            return
        if not isdir(fs_basepath):
            logfile("fs_basepath is not valid")
            return
        if not isdir(fs_homepath):
            logfile("fs_homepath is not valid")
            return
        
        command_line = "\"%s\" +set fs_basepath \"%s\" +set fs_homepath \"%s\" +set fs_game %s" % (etpath , fs_basepath , fs_homepath , fs_game)
        if parameters:
            command_line += ' ' + parameters
        if password and "g_needpass" in Server['cvar'] and int(Server['cvar']['g_needpass']) == 1:
            command_line += ' +set password ' + password
        command_line += ' +connect ' + address
        # End command line generate #
        logfile(command_line)
        return command_line
    def joinserver(self):
        command_line = self.getcommandline()
        if not command_line: return
        call(command_line)
    def getcolortags(self, textstr):
        pass
    def getlinenum(self):
        self.currentline += 1
        data = "%d.%d" % (self.currentline , 0)
        # logfile("Line data = %s right?" % data )
        return data
    def insertline(self, text, tag=None):
        self.text.config(state=NORMAL)
        if not tag:
            self.text.insert(self.getlinenum(), text + '\n')
        else:
            self.text.insert(self.getlinenum(), text + '\n', tag)
        self.text.config(state=DISABLED)
    def serverstatus(self, specificserver=None):
        if specificserver != None:
            selectid = (specificserver,)
        else:
            selectid = self.getselection()
        if not selectid: return
        Server = self.parent.serverdata.Servers[selectid[0]]
        if not Server:
            logfile("Error getting server playerlist %d" % selectid[0])
            return
        logfile("Getting serverstatus for %d (%s)" % (selectid[0], Server['title']))
        self.currentline = 0
        
        self.parent.serverdata.getstatus(selectid[0])
        if Server['ping'] <= 0:
            logfile("Could not ping server")
            return
        halflen = int((SERVERSTATUS_TEXT_LENGTH - 3) / 2)
        if specificserver == None:
            headerlength = SERVERSTATUS_TEXT_LENGTH - 14
            self.text.config(state=NORMAL)
            self.text.delete(1.0, END)
            self.text.config(state=DISABLED)
            if "sv_hostname" in Server['cvar']: self.insertline("%s : %s" % ( "Server Name".ljust(11) , cleanstr(Server['cvar']['sv_hostname']).ljust(headerlength) ) )
            if "mapname" in Server['cvar']: self.insertline("%s : %s" % ( "Map".ljust(11) , Server['cvar']['mapname'].ljust(headerlength)) )
            if "gamename" in Server['cvar']: self.insertline("%s : %s" % ( "Mod".ljust(11), Server['cvar']['gamename'].ljust(headerlength)) )
            self.insertline("%s : %s" % ( "Ping".ljust(11) , (str(Server['ping']) + 'ms').ljust(headerlength)) )
            self.insertline('')
            self.insertline("%s %s %s" % ("Name".ljust(PLAYER_NAME_LENGTH) , "Ping".ljust(PLAYER_PING_LENGTH) , "Score".ljust(PLAYER_SCORE_LENGTH)), "headerLine")
        
        currentplayers = 0
        currentbots = 0
        for Player in Server['playerlist']:
            if Player['ping'] == 0:
                currentbots += 1
            else:
                currentplayers += 1
            if specificserver == None:
                name = cleanstr(Player['name'][:PLAYER_NAME_LENGTH]) if len(cleanstr(Player['name'])) > PLAYER_NAME_LENGTH else cleanstr(Player['name'])
                self.insertline("%s %s %s" % (name.ljust(PLAYER_NAME_LENGTH) , str(Player['ping']).ljust(PLAYER_PING_LENGTH) , str(Player['score']).ljust(PLAYER_SCORE_LENGTH)))
        Server['players'] = "%d/%d (%d)" % (currentplayers , int(Server['cvar']['sv_maxclients']) , currentbots)
        if specificserver == None:
            self.insertline('')
            self.insertline('')
            self.insertline("%s | %s" % ("Cvar".ljust(halflen) , "Value".ljust(halflen)) , "headerLine")
            for Cvar in Server['cvar']:
                self.insertline("%s = %s" % (Cvar.ljust(halflen) , Server['cvar'][Cvar].ljust(halflen)))
            
        self.refresh_list(selectid)
        if specificserver == None:
            if 'g_needpass' in Server['cvar'] and int(Server['cvar']['g_needpass']) == 1:
                self.serverpassword_label.grid(row=1, column=0, sticky=N + W)
                self.serverpassword_entry.grid(row=1, column=1, sticky=N + W + E)
            else:
                self.serverpassword_label.grid_forget()
                self.serverpassword_entry.grid_forget()
            self.serverstatus_frame.grid(row=0, column=1, sticky=N + W, rowspan=3)
    # Events
    def OnMouseWheel(self, event):
        self.servers.yview("scroll", event.delta,"units")
        self.servermap.yview("scroll", event.delta,"units")
        self.serverping.yview("scroll", event.delta,"units")
        self.serverplayers.yview("scroll", event.delta,"units")
        return "break"
    def selectserver(self, e):
        selectid = self.getselection()
        if not selectid: return
        self.servers.select_set(selectid)
        Server = self.parent.serverdata.Servers[selectid[0]]
        if not Server:
            logfile("Error updating server %d" % selectid[0])
            return
        logfile("Selecting server %s" % Server['title'])
        self.servertitle_var.set(Server['title'])
        self.serveraddress_var.set(Server['address'])
        self.serverpassword_var.set(Server['password'])
        self.serverparams_var.set(Server['parameters'])
        self.serverfs_basepath_var.set(Server['fs_basepath'])
        self.serverfs_homepath_var.set(Server['fs_homepath'])
        self.serveretpath_var.set(Server['ETPath'])
        self.button_joinserver.show()
        self.button_removeserver.show()
        self.serverstatus()
        self.serverdata_frame.grid(row=2, column=0, sticky=N)
        command_line = self.getcommandline()
        if command_line: self.notice_var.set(command_line.replace('+','\n+'))
    def updateserver(self, e):
        selectid = self.getselection()
        if not selectid: return
        Server = self.parent.serverdata.Servers[selectid[0]]
        if not Server:
            logfile("Error updating server %d" % selectid[0])
            return
        logfile("Updating %s" % Server['title'])
        logfile(selectid)
        if self.servertitle_var.get():
            Server['title'] = self.servertitle_var.get()
            self.refresh_list(selectid)
        if self.serveraddress_var.get(): Server['address'] = self.serveraddress_var.get()
        if self.serverpassword_var.get(): Server['password'] = self.serverpassword_var.get()
        if self.serverparams_var.get(): Server['parameters'] = self.serverparams_var.get()
        if self.serverfs_basepath_var.get() and isdir(self.serverfs_basepath_var.get()): Server['fs_basepath'] = self.serverfs_basepath_var.get()
        if self.serverfs_homepath_var.get() and isdir(self.serverfs_homepath_var.get()): Server['fs_homepath'] = self.serverfs_homepath_var.get()
        if self.serveretpath_var.get() and isfile(self.serveretpath_var.get()): Server['ETPath'] = self.serveretpath_var.get()
        
    def updateconfig(self, e):
        if self.fs_basepath_var.get() and isdir(self.fs_basepath_var.get()): self.parent.serverdata.fs_basepath = self.fs_basepath_var.get()
        if self.fs_homepath_var.get() and isdir(self.fs_homepath_var.get()): self.parent.serverdata.fs_homepath = self.fs_homepath_var.get()
        if self.etpath_var.get() and isfile(self.etpath_var.get()): self.parent.serverdata.ETPath = self.etpath_var.get()
        if self.parameters_var.get(): self.parent.serverdata.parameters = self.parameters_var.get()
    # Methods
    def getpath(self, browse_var=None, updatemethod=None):
        if not browse_var: return
        if not updatemethod: return
        currentdir = browse_var.get()
        if not currentdir or not isdir(currentdir):
            currentdir = getcwd()
        self.parent.focus_ignore = True
        dir_path = tkinter.filedialog.askdirectory(parent=self, initialdir=currentdir, title="Navigate to your path")
        self.parent.focus_ignore = False
        
        if dir_path and isdir(dir_path):
            browse_var.set(dir_path)
            updatemethod(self)
        else:
            logfile("Could not find directory path")
    def getfilepath(self, browse_var=None, updatemethod=None):
        if not browse_var: return
        if not updatemethod: return
        currentdir = browse_var.get()
        if not currentdir or not isdir(currentdir):
            currentdir = getcwd()
        self.parent.focus_ignore = True
        file_path = tkinter.filedialog.askopenfilename(parent=self, initialdir=currentdir, title="Navigate to your your exe", filetypes=(("exe files", "*.exe"), ("All files", "*")),)
        self.parent.focus_ignore = False
        
        if file_path and isfile(file_path):
            browse_var.set(file_path)
            updatemethod(self)
        else:
            logfile("Could not find filepath")
class Window(Frame):
    def __init__(self, *args, **kwargs):
        self.focus_ignore = False
        self.parent       = Tk()
        self.serverdata   = ServerData()
        self.Config       = {}
        self.serversframe = None
        
        Frame.__init__(self, self.parent, *args, **kwargs)
        
        self.config(background=WINDOW_BACKGROUND)
        
        self.navbar = NavBar(self)
        self.grid()
        
        # Bind the move window function
        self.navbar.bind("<ButtonPress-1>"   , self.StartMove)
        self.navbar.bind("<ButtonRelease-1>" , self.StopMove)
        self.navbar.bind("<B1-Motion>"       , self.OnMotion)
        # self.parent.bind("<FocusIn>"         , self.OnFocus)
        # self.parent.bind("<FocusOut>"        , self.OnLostFocus)
        
        self.parent.overrideredirect(True)
        self.parent.config(background=WINDOW_BORDER, padx=5, pady=5)  # Set padding and background color
        self.parent.title("WolfStarter by Zelly")
        self.parent.bind("<FocusIn>"         , self.OnFocus)
        self.parent.bind("<FocusOut>"        , self.OnLostFocus)
        
        self.load_config()
        
        self.parent.mainloop()
        # Handle Errors
        # Check if window already exists before creating new one
    def load_config(self):
        global WINDOW_BACKGROUND, WINDOW_BORDER, ENTRY_BACKGROUND, ENTRY_FOREGROUND, LIST_SELECT_FORE, LIST_SELECT_BACK, BUTTON_BACKGROUND, BUTTON_FOREGROUND, A_BUTTON_BACKGROUND, A_BUTTON_FOREGROUND,BROWSE_BUTTON_BACKGROUND,BROWSE_BUTTON_FOREGROUND,BROWSE_A_BUTTON_BACKGROUND,BROWSE_A_BUTTON_FOREGROUND,NAVBAR_BACKGROUND,HEADER_BACKGROUND,SERVERLIST_BACKGROUND,SERVERDATA_BACKGROUND,SERVERSTATUS_BACKGROUND
        self.Config = {
                       'servers'             : join(getcwd(), 'servers.json'),
                       'launchmod'           : True,
                       'WINDOW_BACKGROUND'   : "#FFFFFF",  # "#F8F8F8"
                       'WINDOW_BORDER'       : "#000008",
                       'ENTRY_BACKGROUND'    : "#FFFFF9",
                       'ENTRY_FOREGROUND'    : "#000000",
                       'LIST_SELECT_FORE'    : "#FFFFFF",
                       'LIST_SELECT_BACK'    : "#00001F",
                       'BUTTON_BACKGROUND'   : "#B280B2",  # 0099F0
                       'BUTTON_FOREGROUND'   : "#FFFFFF",
                       'A_BUTTON_BACKGROUND' : "#660066",  # 0000FF
                       'A_BUTTON_FOREGROUND' : "#FFFFFF",
                       'BROWSE_BUTTON_BACKGROUND'   : "#B280B2",
                       'BROWSE_BUTTON_FOREGROUND'   : "#FFFFFF",
                       'BROWSE_A_BUTTON_BACKGROUND' : "#660066",
                       'BROWSE_A_BUTTON_FOREGROUND' : "#FFFFFF",
                       'NAVBAR_BACKGROUND'          : "#B280B2",
                       'HEADER_BACKGROUND'          : "#FFFFFF",
                       'SERVERLIST_BACKGROUND'      : "#FFFFFF",
                       'SERVERDATA_BACKGROUND'      : "#FFFFFF",
                       'SERVERSTATUS_BACKGROUND'    : "#FFFFFF",
                       }
        
        if not isfile(join(getcwd() , 'wolfstarter.json')):
            logfile("Config not found using default")
        else:
            with open(join(getcwd() , 'wolfstarter.json')) as configfile:
                jsondata = json.load(configfile)
            if jsondata:
                for key in jsondata:
                    self.Config[key] = jsondata[key]
            for key in ['servers', 'WINDOW_BACKGROUND', 'WINDOW_BORDER', 'ENTRY_BACKGROUND', 'ENTRY_FOREGROUND',
                        'LIST_SELECT_FORE', 'LIST_SELECT_BACK', 'BUTTON_BACKGROUND', 'BUTTON_FOREGROUND',
                        'A_BUTTON_BACKGROUND', 'A_BUTTON_FOREGROUND','BROWSE_BUTTON_BACKGROUND',
                        'BROWSE_BUTTON_FOREGROUND','BROWSE_A_BUTTON_BACKGROUND','BROWSE_A_BUTTON_FOREGROUND','NAVBAR_BACKGROUND','HEADER_BACKGROUND','SERVERLIST_BACKGROUND','SERVERDATA_BACKGROUND','SERVERSTATUS_BACKGROUND'
                        ]:
                if key in jsondata: self.Config[key] = jsondata[key]
                
        WINDOW_BACKGROUND   = self.Config['WINDOW_BACKGROUND']
        WINDOW_BORDER       = self.Config['WINDOW_BORDER']
        ENTRY_BACKGROUND    = self.Config['ENTRY_BACKGROUND']
        ENTRY_FOREGROUND    = self.Config['ENTRY_FOREGROUND']
        LIST_SELECT_FORE    = self.Config['LIST_SELECT_FORE']
        LIST_SELECT_BACK    = self.Config['LIST_SELECT_BACK']
        BUTTON_BACKGROUND   = self.Config['BUTTON_BACKGROUND']
        BUTTON_FOREGROUND   = self.Config['BUTTON_FOREGROUND']
        A_BUTTON_BACKGROUND = self.Config['A_BUTTON_BACKGROUND']
        A_BUTTON_FOREGROUND = self.Config['A_BUTTON_FOREGROUND']
        BROWSE_BUTTON_BACKGROUND   = self.Config['BROWSE_BUTTON_BACKGROUND']
        BROWSE_BUTTON_FOREGROUND   = self.Config['BROWSE_BUTTON_FOREGROUND']
        BROWSE_A_BUTTON_BACKGROUND = self.Config['BROWSE_A_BUTTON_BACKGROUND']
        BROWSE_A_BUTTON_FOREGROUND = self.Config['BROWSE_A_BUTTON_FOREGROUND']
        NAVBAR_BACKGROUND          = self.Config['NAVBAR_BACKGROUND']
        HEADER_BACKGROUND          = self.Config['HEADER_BACKGROUND']
        SERVERLIST_BACKGROUND      = self.Config['SERVERLIST_BACKGROUND']
        SERVERDATA_BACKGROUND      = self.Config['SERVERDATA_BACKGROUND']
        SERVERSTATUS_BACKGROUND    = self.Config['SERVERSTATUS_BACKGROUND']
        
        self.serverdata   = ServerData()
        self.serverdata.load_serverfile(self.Config['servers'])
        
        self.serversframe = ServerFrame(self)
    def save_config(self):
        # If changes then ask to save
        self.serverdata.save_serverfile(self.Config['servers'])
        jsonfile = open(join(getcwd() , 'wolfstarter.json'), 'w')
        json.dump(self.Config, jsonfile, skipkeys=True, allow_nan=True, sort_keys=True, indent=4)
    def destroy_sub_windows(self):
        pass
    # Opening and closing files and application
    def openfile(self):
        self.focus_ignore = True
        fname = tkinter.filedialog.askopenfilename(
                                                parent=self,
                                                initialdir=getcwd(),
                                                title="Select servers file",
                                                filetypes=(("json file", "*.json"), ("All files", "*")),
                                                )
        if not fname or not isfile(fname):
            tkinter.messagebox.showinfo(title="Invalid servers file", message="Servers file was not found", parent=self)
            self.focus_ignore = False
            # self.parent.focus_force()
            logfile("Invalid Servers file was not found %s" % fname)
            # self.Config['servers'] = join( )
            return
        self.focus_ignore = False
        self.Config['servers'] = fname
        self.serverdata        = ServerData()
        self.serverdata.load_serverfile(self.Config['servers'])
        logfile("Loaded Servers file: %s" % self.Config['servers'])
        if self.serversframe:
            self.serversframe.destroy()
        self.serversframe = ServerFrame(self)
    def saveasfile(self):
        self.focus_ignore = True
        fname = tkinter.filedialog.asksaveasfilename(
                                                parent=self,
                                                initialdir=getcwd(),
                                                title="Select servers file",
                                                filetypes=(("json file", "*.json"), ("All files", "*")),
                                                )
        if not fname:
            tkinter.messagebox.showinfo(title="Invalid servers file", message="Servers file was not found", parent=self)
            self.focus_ignore = False
            # self.parent.focus_force()
            logfile("Invalid Servers file was not found %s" % fname)
            return
        self.focus_ignore      = False
        self.Config['servers'] = fname
        self.serverdata.save_serverfile(self.Config['servers'])
        logfile("Saved servers file %s" % self.Config['servers'])
    def quit(self):
        self.save_config()
        self.parent.destroy()
        
    # Moving application on screen
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y
    def StopMove(self, event):
        self.x = None
        self.y = None
    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.parent.winfo_x() + deltax
        y = self.parent.winfo_y() + deltay
        self.parent.geometry("+%s+%s" % (x, y))
    def OnFocus(self, event):
        if self.focus_ignore: return
        w=self.parent.focus_get()
        if w:
            self.parent.overrideredirect(True)
            w.focus_force()
    def OnLostFocus(self, event):
        if self.focus_ignore: return
        if not self.parent.focus_get():
            self.parent.overrideredirect(False)
        
