import json
from os import getcwd
from os.path import isfile, join, isdir
from re import compile
from subprocess import Popen
from tkinter import *  # @UnusedWildImport
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.simpledialog

from zelly.serverdata import ServerData

def openprocess(command):
    Popen(command,shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
    
FONT       = None
BLACK      = "#000000"
DARK_GREY  = "#282828"
GREY       = "#484848"
LIGHT_GREY = "#E0E0E0"
WHITE      = "#FFFFFF"
Config = {
          # WINDOW AND FRAME
          'WINDOW_BACKGROUND'          : WHITE,
          'WINDOW_BORDER'              : BLACK,
          'NAVBAR_BACKGROUND'          : DARK_GREY,
          'HEADER_BACKGROUND'          : WHITE,
          'SERVERLIST_BACKGROUND'      : WHITE,
          'SERVERDATA_BACKGROUND'      : WHITE,
          'SERVERSTATUS_BACKGROUND'    : WHITE,
          'ENTRY_BACKGROUND'           : LIGHT_GREY,
          'ENTRY_FOREGROUND'           : BLACK,
          'LIST_SELECT_FORE'           : WHITE,
          'LIST_SELECT_BACK'           : DARK_GREY,
          'BUTTON_BACKGROUND'          : DARK_GREY,
          'BUTTON_FOREGROUND'          : WHITE,
          'A_BUTTON_BACKGROUND'        : LIGHT_GREY,
          'A_BUTTON_FOREGROUND'        : BLACK,
          'BROWSE_BUTTON_BACKGROUND'   : DARK_GREY,
          'BROWSE_BUTTON_FOREGROUND'   : WHITE,
          'BROWSE_A_BUTTON_BACKGROUND' : LIGHT_GREY,
          'BROWSE_A_BUTTON_FOREGROUND' : BLACK,
          'servers'                    : join(getcwd(), 'servers.json'),
          'launchmod'                  : True,
          }

PLAYER_NAME_LENGTH       = 32
PLAYER_PING_LENGTH       = 8
PLAYER_SCORE_LENGTH      = 12
SERVERSTATUS_TEXT_LENGTH = 54
HALFLEN = int((SERVERSTATUS_TEXT_LENGTH - 3) / 2)
HEADERLENGTH = SERVERSTATUS_TEXT_LENGTH - 14

clean_pattern = compile("(\^.)") #(\^[\d\.\w=\-]?)
def cleanstr(s):
    """Cleans color codes from an W:ET String"""
    return clean_pattern.sub("", s)

def logfile(msg):
    """Prints message and logs to log file"""
    print(msg)
    with open("wolfstarter.log","a") as log_file:
        log_file.write('%s\n' % msg)

class MenuButton(Button):
    """Flat styled button to be placed on navbar
    parent -- Should be Navbar
    column -- Placement from left to right
    row    -- Should probably always be 0 but added just incase"""
    def __init__(self, parent=None, column=0, row=0, cnf={}, **kw):
        Button.__init__(self, parent, cnf, **kw)
        self.parent = parent
        logfile("Making button with background %s" % Config['BUTTON_BACKGROUND'])
        self.config(
                    background=Config['BUTTON_BACKGROUND'],
                    foreground=Config['BUTTON_FOREGROUND'],
                    activebackground=Config['A_BUTTON_BACKGROUND'],
                    activeforeground=Config['A_BUTTON_FOREGROUND'],
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
        """Adds it self to the navbar grid"""
        self.grid(row=self.row, column=self.column, sticky=W)
    def hide(self):
        """Hides itself from the grid"""
        self.grid_forget()
class BrowseButton(Button):
    """File browse button share similar style to MenuButtons""" 
    def __init__(self, master=None, dir_var=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        self.parent = master
        self.config(background=Config['BROWSE_BUTTON_BACKGROUND'],
                    foreground=Config['BROWSE_BUTTON_FOREGROUND'],
                    activebackground=Config['BROWSE_A_BUTTON_BACKGROUND'],
                    activeforeground=Config['BROWSE_A_BUTTON_FOREGROUND'],
                    borderwidth=0,
                    # width           = 5,
                    # height          = 2,
                    relief="flat",
                    padx=5,
                    cursor="hand2")

class NavBar(Frame):
    """Flat styled menu bar should contain only MenuButtons"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(background=Config['NAVBAR_BACKGROUND'] , cursor="hand1")
        # Open 1
        # Save 2
        # Minimize 9
        # Quit 10
        self.button_open     = MenuButton(self , 0 , text="Open..."    , command=parent.openfile)
        self.button_saveas   = MenuButton(self , 1 , text="Save..."  , command=parent.saveasfile)
        self.button_minimize = MenuButton(self , 9 , text="Minimize"  , command=self.minimize)
        self.button_quit     = MenuButton(self , 10 , text="Quit"       , command=parent.quit)
        try:
            with open('version.txt','rb') as versionfile: version=versionfile.read().decode()
        except OSError:
            print("Couldn't get version")
        if not version: version = "vX.X.X"
        self.versionlabel    = Label(self,
                                     background=Config['BUTTON_BACKGROUND'],
                                     foreground=Config['BUTTON_FOREGROUND'],
                                     relief="flat",
                                     borderwidth=0,
                                     width=5,
                                     height=2,
                                     padx=12,
                                     text=version
                                     )
        self.versionlabel.grid(column=11,row=0,sticky=E)
        self.button_open.show()
        self.button_saveas.show()
        self.button_minimize.show()
        self.button_quit.show()
        
        self.grid(column=0, row=0, sticky=N + W + E + S)
        self.columnconfigure(11,weight=1)
    def minimize(self):
        self.parent.minimized = True
        self.parent.parent.overrideredirect(False)
        self.parent.parent.iconify()

class HeaderFrame(Frame):
    """Frame containing global parameters to be applied to all servers by default"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent
        
        self.config(background=Config['HEADER_BACKGROUND'])
        
        # Global ETPath
        self.etpath_var    = StringVar()
        self.etpath_label  = Label(self, text="ET: ", font=FONT, background=Config['HEADER_BACKGROUND'])
        self.etpath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.etpath_var)
        self.etpath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getfilepath(self.etpath_var, self.updateconfig))
        
        self.etpath_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.etpath_label.grid(  row=0 , column=0 , sticky=N + W)
        self.etpath_entry.grid(  row=0 , column=1 , sticky=N + W + E)
        self.etpath_browse.grid( row=0 , column=2 , sticky=N + E)
        
        # Global fs_basepath
        self.fs_basepath_var    = StringVar()
        self.fs_basepath_label  = Label(self, text="fs_basepath: ", font=FONT, background=Config['HEADER_BACKGROUND'])
        self.fs_basepath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.fs_basepath_var)
        self.fs_basepath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getpath(self.fs_basepath_var, self.updateconfig))
        
        self.fs_basepath_entry.bind(  sequence='<KeyRelease>', func=self.updateconfig)
        self.fs_basepath_label.grid(  row=1 , column=0 , sticky=N + W)
        self.fs_basepath_entry.grid(  row=1 , column=1 , sticky=N + W + E)
        self.fs_basepath_browse.grid( row=1 , column=2 , sticky=N + E)
        
        # Global fs_homepath
        self.fs_homepath_var    = StringVar()
        self.fs_homepath_label  = Label(self, text="fs_homepath: ", font=FONT, background=Config['HEADER_BACKGROUND'])
        self.fs_homepath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.fs_homepath_var)
        self.fs_homepath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getpath(self.fs_homepath_var, self.updateconfig))
        
        self.fs_homepath_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.fs_homepath_label.grid(  row=2 , column=0 , sticky=N + W)
        self.fs_homepath_entry.grid(  row=2 , column=1 , sticky=N + W + E)
        self.fs_homepath_browse.grid( row=2 , column=2 , sticky=N + E)
        
        # Global Parameters
        self.parameters_var = StringVar()
        self.parameters_label = Label(self, text="Parameters: ", font=FONT, background=Config['HEADER_BACKGROUND'])
        self.parameters_entry = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.parameters_var)
        
        self.parameters_entry.bind(sequence='<KeyRelease>', func=self.updateconfig)
        self.parameters_label.grid(row=3, column=0, sticky=N + W)
        self.parameters_entry.grid(row=3, column=1, sticky=N + W + E)
        
        if self.ServerFrame.parent.serverdata.fs_basepath: self.fs_basepath_var.set(self.ServerFrame.parent.serverdata.fs_basepath)
        if self.ServerFrame.parent.serverdata.fs_homepath: self.fs_homepath_var.set(self.ServerFrame.parent.serverdata.fs_homepath)
        if self.ServerFrame.parent.serverdata.parameters: self.parameters_var.set(self.ServerFrame.parent.serverdata.parameters)
        if self.ServerFrame.parent.serverdata.ETPath: self.etpath_var.set(self.ServerFrame.parent.serverdata.ETPath)
        
        self.grid_columnconfigure(1, minsize=400)
    def show(self):
        self.grid(row=0, column=0, sticky=N + W + E)
    def hide(self):
        self.grid_forget()
    def updateconfig(self, e):
        if self.fs_basepath_var.get() and isdir(self.fs_basepath_var.get()): self.ServerFrame.parent.serverdata.fs_basepath = self.fs_basepath_var.get()
        if self.fs_homepath_var.get() and isdir(self.fs_homepath_var.get()): self.ServerFrame.parent.serverdata.fs_homepath = self.fs_homepath_var.get()
        if self.etpath_var.get() and isfile(self.etpath_var.get()): self.ServerFrame.parent.serverdata.ETPath = self.etpath_var.get()
        if self.parameters_var.get(): self.ServerFrame.parent.serverdata.parameters = self.parameters_var.get()

class ServerListFrame(Frame):
    """Contains the server list"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent
        
        self.config(background=Config['SERVERLIST_BACKGROUND'], padx=5, pady=5)
        
        # Server List Titles
        self.servers_label = Label(self, text="Title", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.servers       = Listbox(self, width=25, relief="flat",
                                     borderwidth=0,
                                     font=FONT,
                                     selectbackground=Config['LIST_SELECT_BACK'],
                                     selectborderwidth=0,
                                     selectforeground=Config['LIST_SELECT_FORE'],
                                     exportselection=0,
                                     activestyle="none")
        
        self.servers.bind("<<ListboxSelect>>", self.selectserver)
        self.servers.bind("<Double-Button-1>", self.joinserver)
        self.servers.bind("<MouseWheel>", self.OnMouseWheel)
        self.servers_label.grid(row=0, column=0, sticky=N + W + E)
        self.servers.grid(row=1, column=0, sticky=N + W + E)
        
        # Server Map
        self.servermap_label = Label(self, text="Map", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.servermap       = Listbox(self, width=10, relief="flat",
                                       borderwidth=0,
                                       font=FONT,
                                       selectbackground=Config['LIST_SELECT_BACK'],
                                       selectborderwidth=0,
                                       selectforeground=Config['LIST_SELECT_FORE'],
                                       exportselection=0,
                                       activestyle="none")
        
        self.servermap.bind("<<ListboxSelect>>", self.selectserver)
        self.servermap.bind("<Double-Button-1>", self.joinserver)
        self.servermap.bind("<MouseWheel>", self.OnMouseWheel)
        self.servermap_label.grid(row=0, column=1, sticky=N + W + E)
        self.servermap.grid(row=1, column=1, sticky=N + W + E)
        
        # Server Players
        self.serverplayers_label = Label(self, text="Players", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.serverplayers       = Listbox(self, width=10, relief="flat",
                                           borderwidth=0,
                                           font=FONT,
                                           selectbackground=Config['LIST_SELECT_BACK'],
                                           selectborderwidth=0,
                                           selectforeground=Config['LIST_SELECT_FORE'],
                                           exportselection=0,
                                           activestyle="none")
        
        self.serverplayers.bind("<<ListboxSelect>>", self.selectserver)
        self.serverplayers.bind("<Double-Button-1>", self.joinserver)
        self.serverplayers.bind("<MouseWheel>", self.OnMouseWheel)
        self.serverplayers_label.grid(row=0, column=2, sticky=N + W + E)
        self.serverplayers.grid(row=1, column=2, sticky=N + W + E)
        
        # Server Ping
        self.serverping_label = Label(self, text="Ping", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.serverping       = Listbox(self, width=10, relief="flat",
                                        borderwidth=0,
                                        font=FONT,
                                        selectbackground=Config['LIST_SELECT_BACK'],
                                        selectborderwidth=0,
                                        selectforeground=Config['LIST_SELECT_FORE'],
                                        exportselection=0,
                                        activestyle="none")
        
        self.serverping.bind("<<ListboxSelect>>", self.selectserver)
        self.serverping.bind("<Double-Button-1>", self.joinserver)
        self.serverping.bind("<MouseWheel>", self.OnMouseWheel)
        self.serverping_label.grid(row=0, column=3, sticky=N + W + E)
        self.serverping.grid(row=1, column=3, sticky=N + W + E)
        
        self.grid_columnconfigure(0, weight=1)
    def show(self):
        self.grid(row=1, column=0, sticky=N + W)
    def hide(self):
        self.grid_forget()
    def clear(self):
        self.servers.selection_clear(0, END)
        self.servers.delete(0, END)
        self.servermap.selection_clear(0, END)
        self.servermap.delete(0, END)
        self.serverplayers.selection_clear(0, END)
        self.serverplayers.delete(0, END)
        self.serverping.selection_clear(0, END)
        self.serverping.delete(0, END)
    def add(self,Server=None):
        if not Server: return
        self.servers.insert(END       , Server['title'])
        self.servermap.insert(END     , Server['map'])
        self.serverplayers.insert(END , Server['players'])
        self.serverping.insert(END    , Server['ping'])
    def select(self,selectid=None):
        if not selectid: return
        self.servers.select_set(selectid)
        self.servermap.select_set(selectid)
        self.serverplayers.select_set(selectid)
        self.serverping.select_set(selectid)
    def get(self):
        if self.servers.curselection(): return self.servers.curselection()[0]
        if self.servermap.curselection(): return self.servermap.curselection()[0]
        if self.serverping.curselection(): return self.serverping.curselection()[0]
        if self.serverplayers.curselection(): return self.serverplayers.curselection()[0]
        return None
    def getfull(self):
        if self.servers.curselection(): return self.servers.curselection()
        if self.servermap.curselection(): return self.servermap.curselection()
        if self.serverping.curselection(): return self.serverping.curselection()
        if self.serverplayers.curselection(): return self.serverplayers.curselection()
        return None
    def OnMouseWheel(self, event):
        #print(event.delta)
        delta = event.delta*-1
        #print(delta)
        self.servers.yview("scroll", delta,"units")
        self.servermap.yview("scroll", delta,"units")
        self.serverping.yview("scroll", delta,"units")
        self.serverplayers.yview("scroll", delta,"units")
        return "break"
    def selectserver(self, e):
        selectid = self.get()
        if not selectid: return
        
        Server = self.ServerFrame.parent.serverdata.Servers[selectid]
        if not Server:
            logfile("Error updating server %d" % selectid)
            return
        
        logfile("Selecting server %s" % Server['title'])
        
        self.select(self.getfull())
        self.ServerFrame.ServerDataFrame.set(Server)
        
        self.ServerFrame.button_joinserver.show()
        self.ServerFrame.button_removeserver.show()
        self.ServerFrame.serverstatus()

        command_line = self.ServerFrame.getcommandline(selectid)
        if command_line: self.ServerFrame.NoticeLabel.set(command_line.replace('+','\n+'))

class ServerDataFrame(Frame):
    """Frame contains all server related frames"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent
        
        self.config(background=Config['SERVERDATA_BACKGROUND'])
        
        # Server title
        self.servertitle_var   = StringVar()
        self.servertitle_label = Label(self, text="Title: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.servertitle_entry = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.servertitle_var)
        
        self.servertitle_entry.bind( sequence='<KeyRelease>', func=self.updateserver)
        self.servertitle_label.grid( row=0, column=0, sticky=N + W)
        self.servertitle_entry.grid( row=0, column=1, sticky=N + W + E)
        
        # Server Password
        self.serverpassword_var   = StringVar()
        self.serverpassword_label = Label(self, text="Password: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serverpassword_entry = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serverpassword_var)
        
        self.serverpassword_entry.bind( sequence='<KeyRelease>', func=self.updateserver)
        
        # Server address
        self.serveraddress_var   = StringVar()
        self.serveraddress_label = Label(self, text="Address: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serveraddress_entry = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serveraddress_var)
        
        self.serveraddress_entry.bind( sequence='<KeyRelease>', func=self.updateserver)
        self.serveraddress_label.grid( row=2, column=0, sticky=N + W)
        self.serveraddress_entry.grid( row=2, column=1, sticky=N + W + E)
        
        # Server ETPath
        self.serveretpath_var    = StringVar()
        self.serveretpath_label  = Label(self, text="ET: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serveretpath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serveretpath_var)
        self.serveretpath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getfilepath(self.serveretpath_var, self.updateserver))
        
        self.serveretpath_entry.bind(  sequence='<KeyRelease>', func=self.updateserver)
        self.serveretpath_label.grid(  row=3, column=0, sticky=N + W)
        self.serveretpath_entry.grid(  row=3, column=1, sticky=N + W + E)
        self.serveretpath_browse.grid( row=3, column=2, sticky=N + E)
        
        # Server fs_basepath
        self.serverfs_basepath_var    = StringVar()
        self.serverfs_basepath_label  = Label(self, text="fs_basepath: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serverfs_basepath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serverfs_basepath_var)
        self.serverfs_basepath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getpath(self.serverfs_basepath_var, self.updateserver))
        
        self.serverfs_basepath_entry.bind(  sequence='<KeyRelease>', func=self.updateserver)
        self.serverfs_basepath_label.grid(  row=4, column=0, sticky=N + W)
        self.serverfs_basepath_entry.grid(  row=4, column=1, sticky=N + W + E)
        self.serverfs_basepath_browse.grid( row=4, column=2, sticky=N + E)
        
        # Server fs_homepath
        self.serverfs_homepath_var    = StringVar()
        self.serverfs_homepath_label  = Label(self, text="fs_homepath: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serverfs_homepath_entry  = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serverfs_homepath_var)
        self.serverfs_homepath_browse = BrowseButton(self, text="Browse...", command=lambda :self.ServerFrame.getpath(self.serverfs_homepath_var, self.updateserver))
        
        self.serverfs_homepath_entry.bind(  sequence='<KeyRelease>', func=self.updateserver)
        self.serverfs_homepath_label.grid(  row=5, column=0, sticky=N + W)
        self.serverfs_homepath_entry.grid(  row=5, column=1, sticky=N + W + E)
        self.serverfs_homepath_browse.grid( row=5, column=2, sticky=N + E)
        
        # Server extra parameters
        self.serverparams_var   = StringVar()
        self.serverparams_label = Label(self, text="Parameters: ", font=FONT, background=Config['SERVERDATA_BACKGROUND'])
        self.serverparams_entry = Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'], foreground=Config['ENTRY_FOREGROUND'], textvariable=self.serverparams_var)
        
        self.serverparams_entry.bind( sequence='<KeyRelease>', func=self.updateserver)
        self.serverparams_label.grid( row=6, column=0, sticky=N + W)
        self.serverparams_entry.grid( row=6, column=1, sticky=N + W + E)
        self.grid_columnconfigure(1, minsize=400)
    def show(self):
        self.grid(row=2, column=0, sticky=N)
    def hide(self):
        self.grid_forget()
    def showpassword(self):
        self.serverpassword_label.grid(row=1, column=0, sticky=N + W)
        self.serverpassword_entry.grid(row=1, column=1, sticky=N + W + E)
    def hidepassword(self):
        self.serverpassword_label.grid_forget()
        self.serverpassword_entry.grid_forget()
    def set(self,Server=None):
        if not Server: return
        self.servertitle_var.set(Server['title'])
        self.serveraddress_var.set(Server['address'])
        self.serverpassword_var.set(Server['password'])
        self.serverparams_var.set(Server['parameters'])
        self.serverfs_basepath_var.set(Server['fs_basepath'])
        self.serverfs_homepath_var.set(Server['fs_homepath'])
        self.serveretpath_var.set(Server['ETPath'])
    def updateserver(self,Server=None):
        if not Server: return
        if self.servertitle_var.get(): Server['title'] = self.servertitle_var.get()
        if self.serveraddress_var.get(): Server['address'] = self.serveraddress_var.get()
        if self.serverpassword_var.get(): Server['password'] = self.serverpassword_var.get()
        if self.serverparams_var.get(): Server['parameters'] = self.serverparams_var.get()
        if self.serverfs_basepath_var.get() and isdir(self.serverfs_basepath_var.get()): Server['fs_basepath'] = self.serverfs_basepath_var.get()
        if self.serverfs_homepath_var.get() and isdir(self.serverfs_homepath_var.get()): Server['fs_homepath'] = self.serverfs_homepath_var.get()
        if self.serveretpath_var.get() and isfile(self.serveretpath_var.get()): Server['ETPath'] = self.serveretpath_var.get()
    def clear(self):
        self.servertitle_var.set('')
        self.serveraddress_var.set('')
        self.serverpassword_var.set('')
        self.serverparams_var.set('')
        self.serverfs_basepath_var.set('')
        self.serverfs_homepath_var.set('')
        self.serveretpath_var.set('')
class ServerStatusFrame(Frame):
    """Contains actual serverdata information such as players and cvars"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.config(background=Config['SERVERSTATUS_BACKGROUND'])
        
        self.currentline = 1
        
        self.text = Text(
                         self,
                         background=Config['SERVERSTATUS_BACKGROUND'],
                         font=FONT,
                         relief="flat",
                         wrap="none",
                         width=54,
                         height=29,
                         )

        self.text.tag_config("headerLine", foreground=Config['BUTTON_FOREGROUND'], background=Config['BUTTON_BACKGROUND'], underline=1)
        
        self.text.grid(sticky=W + N)
        
        self.text_scroll = Scrollbar(self, command=self.text.yview, background=Config['BUTTON_BACKGROUND'])
        self.text.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.grid(row=0, column=1, sticky="ns")
    def show(self):
        self.grid(row=0, column=1, sticky=N + W, rowspan=3)
    def hide(self):
        self.grid_forget()
    def getlinenum(self):
        self.currentline += 1
        data = "%d.%d" % (self.currentline , 0)
        # logfile("Line data = %s right?" % data )
        return data
    def insertline(self, text, tag=None):
        self.text.config(state=NORMAL)
        if tag == None:
            self.text.insert(self.getlinenum(), text + '\n')
        else:
            self.text.insert(self.getlinenum(), text + '\n', tag)
        self.text.config(state=DISABLED)
    def clear(self):
        self.currentline = 0
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=DISABLED)
class NoticeLabel(Label):
    def __init__(self, parent=None, cnf={}, **kw):
        Label.__init__(self, parent, cnf, **kw)
        self.ServerFrame = parent
        self.textvar     = StringVar(value="FS_Basepath and FS_Homepath are not required.\nThey will be set to the folder of you ET.exe if not specfied.")
        
        self.config(font=FONT,background=Config['WINDOW_BACKGROUND'],textvariable=self.textvar)
        
        self.show()
    def set(self,message=""):
        self.textvar.set(message)
    def show(self):
        self.grid(row=4, column=0, sticky=N + W,rowspan=2)
    def hide(self):
        self.grid_forget()
class ServerFrame(Frame):
    """Frame contains all server related frames"""
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.config(background=Config['WINDOW_BACKGROUND'], padx=5, pady=5)
        
        self.HeaderFrame       = HeaderFrame(self)
        self.ServerListFrame   = ServerListFrame(self)
        self.ServerDataFrame   = ServerDataFrame(self)
        self.ServerStatusFrame = ServerStatusFrame(self)
        
        self.button_addserver    = MenuButton(self.parent.navbar , 3 , text="Add"        , command=self.addserver)
        self.button_removeserver = MenuButton(self.parent.navbar , 4 , text="Remove"     , command=self.removeserver)
        #self.button_rcon         = MenuButton( self.parent.navbar , 5 , text="Rcon"       , command=parent.rcon)
        self.button_joinserver   = MenuButton(self.parent.navbar , 6 , text="Join"       , command=self.joinserver)
        self.button_addserver.show()
        
        # Bring it all together
        self.create_server_list()
        
        self.HeaderFrame.show()
        self.ServerListFrame.show()
        self.NoticeLabel = NoticeLabel(self)
        
        self.grid(sticky=W + S + N + E)
    def create_server_list(self):
        self.ServerStatusFrame.hide()
        self.ServerDataFrame.hide()
        self.ServerDataFrame.clear()
        self.button_joinserver.hide()
        self.button_removeserver.hide()
        for x in range(0, len(self.parent.serverdata.Servers)): self.serverstatus(x)
        self.refresh_list(None)
    def refresh_list(self, selectid=None):
        self.ServerListFrame.clear()
        for Server in self.parent.serverdata.Servers: self.ServerListFrame.add(Server)
        if selectid: self.ServerListFrame.select(selectid)
    # Buttons
    def addserver(self): # Leaving error checking up to the join command
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
        self.ServerListFrame.select(END) # Select added server
        self.selectserver(None) # Get Server Data
    def removeserver(self):
        selectid = self.ServerListFrame.get()
        if selectid == None: return
        if not self.parent.serverdata.Servers[selectid]:
            logfile("Error updating server %d" % selectid)
            return
        del self.parent.serverdata.Servers[selectid]
        self.create_server_list()
    def getcommandline(self,selectid=None):
        # TODO Move this to serverdata
        #selectid = self.ServerListFrame.get()
        if selectid == None: return
        Server = self.parent.serverdata.Servers[selectid]
        if not Server:
            logfile("Error getting command line for server %d" % selectid)
            return
        # Generate Startup Line #
        etpath      = ''
        fs_basepath = ''
        fs_homepath = ''
        fs_game     = 'etmain' # Etmain by default if mod does not exist
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
            
        if Config['launchmod']:
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
    def joinserver(self,e=None):
        selectid = self.ServerListFrame.get()
        if selectid == None: return
        command_line = self.getcommandline(selectid)
        if not command_line: return
        logfile("Joining server %s" % selectid)
        openprocess(command_line)
    def serverstatus(self, selectid=None):
        specificserver = False
        if selectid == None:
            selectid = self.ServerListFrame.get()
        else:
            specificserver = True
        if selectid == None: return
        
        Server = self.parent.serverdata.Servers[selectid]
        
        if not Server:
            logfile("Error getting server playerlist %d" % selectid)
            return
        
        logfile("Getting serverstatus for %d (%s)" % (selectid, Server['title']))
        
        self.parent.serverdata.getstatus(selectid)
        
        if Server['ping'] <= 0:
            logfile("Could not ping server")
            return
        
        if not specificserver:
            self.ServerStatusFrame.clear()
            if "sv_hostname" in Server['cvar']:
                self.ServerStatusFrame.insertline("%s : %s" % ( "Server Name".ljust(11) , cleanstr(Server['cvar']['sv_hostname']).ljust(HEADERLENGTH) ) )
            if "mapname" in Server['cvar']:
                self.ServerStatusFrame.insertline("%s : %s" % ( "Map".ljust(11) , Server['cvar']['mapname'].ljust(HEADERLENGTH)) )
            if "gamename" in Server['cvar']:
                self.ServerStatusFrame.insertline("%s : %s" % ( "Mod".ljust(11), Server['cvar']['gamename'].ljust(HEADERLENGTH)) )
            self.ServerStatusFrame.insertline("%s : %s" % ( "Ping".ljust(11) , (str(Server['ping']) + 'ms').ljust(HEADERLENGTH)) )
            self.ServerStatusFrame.insertline('')
            self.ServerStatusFrame.insertline("%s %s %s" % ("Name".ljust(PLAYER_NAME_LENGTH) , "Ping".ljust(PLAYER_PING_LENGTH) , "Score".ljust(PLAYER_SCORE_LENGTH)), "headerLine")
        
        currentplayers = 0
        currentbots    = 0
        for Player in Server['playerlist']:
            if Player['ping'] == 0:
                currentbots += 1
            else:
                currentplayers += 1
            if not specificserver:
                name = cleanstr(Player['name'][:PLAYER_NAME_LENGTH]) if len(cleanstr(Player['name'])) > PLAYER_NAME_LENGTH else cleanstr(Player['name'])
                self.ServerStatusFrame.insertline("%s %s %s" % (name.ljust(PLAYER_NAME_LENGTH) , str(Player['ping']).ljust(PLAYER_PING_LENGTH) , str(Player['score']).ljust(PLAYER_SCORE_LENGTH)))
        Server['players'] = "%d/%d (%d)" % (currentplayers , int(Server['cvar']['sv_maxclients']) , currentbots)
        
        if not specificserver:
            self.ServerStatusFrame.insertline('')
            self.ServerStatusFrame.insertline('')
            self.ServerStatusFrame.insertline("%s | %s" % ("Cvar".ljust(HALFLEN) , "Value".ljust(HALFLEN)) , "headerLine")
            for Cvar in Server['cvar']:
                self.ServerStatusFrame.insertline("%s = %s" % (Cvar.ljust(HALFLEN) , Server['cvar'][Cvar].ljust(HALFLEN)))
            
        self.refresh_list(selectid)
        if specificserver == None:
            if 'g_needpass' in Server['cvar'] and int(Server['cvar']['g_needpass']) == 1:
                self.ServerDataFrame.showpassword()
            else:
                self.ServerDataFrame.hidepassword()
            self.ServerStatusFrame.show()
    # Events
    def updateserver(self, e):
        selectid = self.ServerListFrame.get()
        if not selectid: return
        Server = self.parent.serverdata.Servers[selectid]
        if not Server:
            logfile("Error updating server %d" % selectid)
            return
        logfile("Updating %s at %d" % ( Server['title'] , selectid ) )
        
        self.ServerDataFrame.updateserver(Server)
        self.refresh_list(selectid)
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
        global FONT
        self.focus_ignore = False
        self.minimized    = False
        self.parent       = Tk()
        self.serverdata   = ServerData()
        self.serversframe = None
        FONT              = tkinter.font.Font(family="Courier New", size=10)
        
        Frame.__init__(self, self.parent, *args, **kwargs)
        
        self.load_config()
        
        self.config(background=Config['WINDOW_BACKGROUND'])
        
        self.navbar = NavBar(self)
        self.grid()
        
        # Bind the move window function
        self.navbar.bind("<ButtonPress-1>"   , self.StartMove)
        self.navbar.bind("<ButtonRelease-1>" , self.StopMove)
        self.navbar.bind("<B1-Motion>"       , self.OnMotion)
        # self.parent.bind("<FocusIn>"         , self.OnFocus)
        # self.parent.bind("<FocusOut>"        , self.OnLostFocus)
        
        self.parent.overrideredirect(True)
        self.parent.config(background=Config['WINDOW_BORDER'], padx=5, pady=5)  # Set padding and background color
        self.parent.title("WolfStarter by Zelly")
        self.parent.bind("<FocusIn>"         , self.OnFocus)
        self.parent.bind("<FocusOut>"        , self.OnLostFocus)
        self.parent.bind("<Configure>"       , self.OnConfigure)
        self.parent.iconbitmap('WolfStarterLogo.ico')
        
        self.serverdata   = ServerData()
        self.serverdata.load_serverfile(Config['servers'])
        self.serversframe = ServerFrame(self)
        
        self.parent.mainloop()
        # Handle Errors
        # Check if window already exists before creating new one
    def load_config(self):
        #global Config
        
        if not isfile(join(getcwd() , 'wolfstarter.json')):
            logfile("Config not found using default")
        else:
            with open(join(getcwd() , 'wolfstarter.json')) as configfile:
                jsondata = json.load(configfile)
            if jsondata:
                for key in jsondata:
                    if key in Config:
                        Config[key] = jsondata[key]
                        logfile(key.ljust(32) + " = " + str(jsondata[key]))
                    # Make sure to only do keys that exist.
    def save_config(self):
        # If changes then ask to save
        self.serverdata.save_serverfile(Config['servers'])
        jsonfile = open(join(getcwd() , 'wolfstarter.json'), 'w')
        json.dump(Config, jsonfile, skipkeys=True, allow_nan=True, sort_keys=True, indent=4)
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
            logfile("Invalid Servers file was not found %s" % fname)
            return
        self.focus_ignore      = False
        Config['servers']      = fname
        self.serverdata        = ServerData()
        self.serverdata.load_serverfile(Config['servers'])
        logfile("Loaded Servers file: %s" % Config['servers'])
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
        Config['servers']      = fname
        self.serverdata.save_serverfile(Config['servers'])
        logfile("Saved servers file %s" % Config['servers'])
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
        if self.minimized or self.focus_ignore: return
        w=self.parent.focus_get()
        if w:
            self.parent.overrideredirect(True)
            w.focus_force()
    def OnLostFocus(self, event):
        if self.minimized or self.focus_ignore: return
        if not self.parent.focus_get():
            self.parent.overrideredirect(False)
        
    def OnConfigure(self,event):
        if self.minimized and not self.parent.focus_get(): # If minimized, and window does not have focus and there is a new event.
            # Is most likely that the event is a maximize event, however the window isn't maximized until after this event.
            def task():
                if self.minimized and self.parent.focus_get():
                    self.minimized = False
                    self.parent.overrideredirect(True)
            self.parent.after(50,task) # Do task after 50 ms (Basically after the window is maximized)
            