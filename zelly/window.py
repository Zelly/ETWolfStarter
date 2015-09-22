import json
from os import startfile, getcwd, chdir
from os.path import isfile, join, isdir
from re import compile
import tkinter
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.simpledialog

from tkinter import END, W, E, N, S, NORMAL, DISABLED
from zelly.serverdata import ServerData
from zelly.constants import *

FONT = None
Config = {
    # WINDOW AND FRAME
    'WINDOW_BACKGROUND': WHITE,
    'WINDOW_BORDER': BLACK,
    'NAVBAR_BACKGROUND': DARK_GREY,
    'HEADER_BACKGROUND': WHITE,
    'SERVERLIST_BACKGROUND': WHITE,
    'SERVERDATA_BACKGROUND': WHITE,
    'SERVERSTATUS_BACKGROUND': WHITE,
    'ENTRY_BACKGROUND': LIGHT_GREY,
    'ENTRY_FOREGROUND': BLACK,
    'LIST_SELECT_FORE': WHITE,
    'LIST_SELECT_BACK': DARK_GREY,
    'BUTTON_BACKGROUND': DARK_GREY,
    'BUTTON_FOREGROUND': WHITE,
    'A_BUTTON_BACKGROUND': LIGHT_GREY,
    'A_BUTTON_FOREGROUND': BLACK,
    'BROWSE_BUTTON_BACKGROUND': DARK_GREY,
    'BROWSE_BUTTON_FOREGROUND': WHITE,
    'BROWSE_A_BUTTON_BACKGROUND': LIGHT_GREY,
    'BROWSE_A_BUTTON_FOREGROUND': BLACK,
    'servers': join(getcwd(), 'servers.json'),
    'launchmod': True,
    'showbasepath': False,
    'showhomepath': False,
    'showcommandline': False,
    'windowborder': False,
    'checkupdate': True,
}

clean_pattern = compile("(\^.)")  # (\^[\d\.\w=\-]?)


def clean_str(s):
    """Cleans color codes from an W:ET String"""
    return clean_pattern.sub("", s)


class MenuButton(tkinter.Button):
    """Flat styled button to be placed on navbar
    parent -- Should be Navbar
    column -- Placement from left to right
    row    -- Should probably always be 0 but added just incase"""

    def __init__(self, parent=None, column=0, row=0, sticky=W, cnf=None, **kw):
        if not cnf:
            cnf = {}

        tkinter.Button.__init__(self, parent, cnf, **kw)
        self.parent = parent
        self.config(
            background=Config['BUTTON_BACKGROUND'],
            foreground=Config['BUTTON_FOREGROUND'],
            activebackground=Config['A_BUTTON_BACKGROUND'],
            activeforeground=Config['A_BUTTON_FOREGROUND'],
            borderwidth=0,
            width=5,
            height=1,
            relief="flat",
            padx=12,
            cursor="hand2",
        )
        self.sticky = sticky
        self.row = row
        self.column = column
        self.hide()

    def show(self):
        """Adds it self to the navbar grid"""
        self.grid(row=self.row, column=self.column, sticky=self.sticky)

    def hide(self):
        """Hides itself from the grid"""
        self.grid_forget()


class BrowseButton(tkinter.Button):
    """File browse button share similar style to MenuButtons"""

    def __init__(self, master=None, dir_var=None, cnf=None, **kw):
        if not cnf:
            cnf = {}
        if not dir_var:
            logfile("Browse button created without dir var")
        tkinter.Button.__init__(self, master, cnf, **kw)
        self.parent = master
        self.config(background=Config['BROWSE_BUTTON_BACKGROUND'],
                    foreground=Config['BROWSE_BUTTON_FOREGROUND'],
                    activebackground=Config['BROWSE_A_BUTTON_BACKGROUND'],
                    activeforeground=Config['BROWSE_A_BUTTON_FOREGROUND'],
                    borderwidth=0,
                    relief="flat",
                    padx=5,
                    cursor="hand2")


class NavBar(tkinter.Frame):
    """Flat styled menu bar should contain only MenuButtons"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.MainWindow = parent
        self.updater = None
        logfile("LOADING...    NAVBAR")
        self.config(background=Config['NAVBAR_BACKGROUND'], cursor="hand1")

        self.button_open = MenuButton(self, BUTTON_OPEN, text="Open...", command=self.MainWindow.open_servers_file)
        self.button_saveas = MenuButton(self, BUTTON_SAVE, text="Save...", command=self.MainWindow.save_as_file)
        self.button_issues = MenuButton(self, BUTTON_ISSUE, 0, E, text="Issue...", command=self.issue)
        self.button_donate = MenuButton(self, BUTTON_DONATE, 0, E, text="Donate...", command=self.donate)
        self.button_minimize = MenuButton(self, BUTTON_MINIMIZE, 0, E, text="Minimize", command=self.minimize)
        self.button_quit = MenuButton(self, BUTTON_QUIT, 0, E, text="Quit", command=self.MainWindow.quit)
        self.button_update = MenuButton(self, BUTTON_UPDATE, 0, E, text="Update", command=self.update_link)
        self.button_settings = MenuButton(self, BUTTON_SETTINGS, 0, E, text="Settings", command=self.settings)
        self.button_log_window = MenuButton(self, BUTTON_TEST, 0, E, text="LogWindow", command=self.log_window)
        self.label_version = tkinter.Label(self, background=Config['BUTTON_BACKGROUND'],
                                           foreground=Config['BUTTON_FOREGROUND'], relief="flat", borderwidth=0,
                                           width=5, height=1, padx=12, text=WOLFSTARTER_VERSION)
        self.label_version.grid(column=LABEL_VERSION, row=0, sticky=E)
        self.columnconfigure(BUTTON_SETTINGS, weight=1)

        self.button_open.show()
        self.button_saveas.show()
        self.button_settings.show()
        self.button_issues.show()
        self.button_donate.show()
        if not Config['windowborder']:
            self.button_minimize.show()
            self.button_quit.show()
        self.button_log_window.show()

        if Config['checkupdate']:
            def check_update():
                self.updater = WolfStarterUpdater()
                if self.updater.check():
                    self.button_update.show()
                else:
                    self.update = None

            self.after(500, check_update)

        self.grid(column=FRAME_NAVBAR[0], row=FRAME_NAVBAR[0], sticky=N + W + E + S)

    def log_window(self):
        LogWindow(self.MainWindow)

    def minimize(self):
        self.MainWindow.minimized = True
        self.MainWindow.overrideredirect(False)
        self.MainWindow.iconify()

    def issue(self):
        self.MainWindow.overrideredirect(False)
        self.MainWindow.focus_ignore = True
        ok = tkinter.messagebox.askyesno("Open issues page", "Would you like to go to the github issues page?",
                                         parent=self.MainWindow)
        self.MainWindow.focus_ignore = False
        self.MainWindow.overrideredirect(True)
        if ok:
            startfile(r"https://github.com/Zelly/ETWolfStarter/issues/new")

    def donate(self):
        print("Opening donate dialog")
        self.MainWindow.overrideredirect(False)
        self.MainWindow.focus_ignore = True
        ok = tkinter.messagebox.askyesno(title="Open donate page",
                                         message="Would you like to go to the paypal donate page?",
                                         parent=self.MainWindow)
        self.MainWindow.focus_ignore = False
        self.MainWindow.overrideredirect(True)
        if ok:
            startfile(
                r"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=45BP8LRVZW7JC&lc=US&item_" +
                "name=Zelly%20Github%20Donate&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted")

    def update_link(self):
        print("Opening update dialog")
        self.MainWindow.overrideredirect(False)
        self.MainWindow.focus_ignore = True
        ok = tkinter.messagebox.askyesno(title="Open update download page",
                                         message="Would you like to go to the update download page?",
                                         parent=self.MainWindow)
        self.MainWindow.focus_ignore = False
        self.MainWindow.overrideredirect(True)
        if ok:
            startfile(self.updater.getreleaseurl())
            exit(0)  # Close because they can't update with it open

    def settings(self):
        self.MainWindow.ServerFrame.close_window()
        Settings(self.MainWindow)  # Mainframe here?


class HeaderFrame(tkinter.Frame):
    """Frame containing global parameters to be applied to all servers by default"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent

        self.config(background=Config['HEADER_BACKGROUND'])

        # Global ETPath
        self.etpath_var = tkinter.StringVar()
        self.etpath_label = tkinter.Label(self, text="ET: ", font=FONT, background=Config['HEADER_BACKGROUND'])
        self.etpath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                          foreground=Config['ENTRY_FOREGROUND'], textvariable=self.etpath_var)
        self.etpath_browse = BrowseButton(self, text="Browse...", command=lambda: self.ServerFrame.get_file_path(
            self.etpath_var, self.update_config))

        self.etpath_entry.bind(sequence='<KeyRelease>', func=self.update_config)
        self.etpath_label.grid(row=0, column=0, sticky=N + W)
        self.etpath_entry.grid(row=0, column=1, sticky=N + W + E)
        self.etpath_browse.grid(row=0, column=2, sticky=N + E)

        # Global fs_basepath
        self.fs_basepath_var = tkinter.StringVar()
        self.fs_basepath_label = tkinter.Label(self, text="fs_basepath: ", font=FONT,
                                               background=Config['HEADER_BACKGROUND'])
        self.fs_basepath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                               foreground=Config['ENTRY_FOREGROUND'], textvariable=self.fs_basepath_var)
        self.fs_basepath_browse = BrowseButton(self, text="Browse...",
                                               command=lambda: self.ServerFrame.get_path(self.fs_basepath_var,
                                                                                         self.update_config))

        if Config['showbasepath']:
            self.fs_basepath_entry.bind(sequence='<KeyRelease>', func=self.update_config)
            self.fs_basepath_label.grid(row=1, column=0, sticky=N + W)
            self.fs_basepath_entry.grid(row=1, column=1, sticky=N + W + E)
            self.fs_basepath_browse.grid(row=1, column=2, sticky=N + E)

        # Global fs_homepath
        self.fs_homepath_var = tkinter.StringVar()
        self.fs_homepath_label = tkinter.Label(self, text="fs_homepath: ", font=FONT,
                                               background=Config['HEADER_BACKGROUND'])
        self.fs_homepath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                               foreground=Config['ENTRY_FOREGROUND'], textvariable=self.fs_homepath_var)
        self.fs_homepath_browse = BrowseButton(self, text="Browse...",
                                               command=lambda: self.ServerFrame.get_path(self.fs_homepath_var,
                                                                                         self.update_config))

        if Config['showhomepath']:
            self.fs_homepath_entry.bind(sequence='<KeyRelease>', func=self.update_config)
            self.fs_homepath_label.grid(row=2, column=0, sticky=N + W)
            self.fs_homepath_entry.grid(row=2, column=1, sticky=N + W + E)
            self.fs_homepath_browse.grid(row=2, column=2, sticky=N + E)

        # Global Parameters
        self.parameters_var = tkinter.StringVar()
        self.parameters_label = tkinter.Label(self, text="Parameters: ", font=FONT,
                                              background=Config['HEADER_BACKGROUND'])
        self.parameters_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                              foreground=Config['ENTRY_FOREGROUND'], textvariable=self.parameters_var)

        self.parameters_entry.bind(sequence='<KeyRelease>', func=self.update_config)
        self.parameters_label.grid(row=3, column=0, sticky=N + W)
        self.parameters_entry.grid(row=3, column=1, sticky=N + W + E)

        if self.ServerFrame.MainWindow.ServerData.fs_basepath is not None:
            self.fs_basepath_var.set(self.ServerFrame.MainWindow.ServerData.fs_basepath)
        if self.ServerFrame.MainWindow.ServerData.fs_homepath is not None:
            self.fs_homepath_var.set(self.ServerFrame.MainWindow.ServerData.fs_homepath)
        if self.ServerFrame.MainWindow.ServerData.parameters is not None:
            self.parameters_var.set(self.ServerFrame.MainWindow.ServerData.parameters)
        if self.ServerFrame.MainWindow.ServerData.ETPath is not None:
            self.etpath_var.set(self.ServerFrame.MainWindow.ServerData.ETPath)

        self.grid_columnconfigure(1, minsize=400)

    def show(self):
        self.grid(row=FRAME_HEADER[0], column=FRAME_HEADER[1], sticky=N + W + E)

    def hide(self):
        self.grid_forget()

    # noinspection PyUnusedLocal
    def update_config(self, e):
        if self.fs_basepath_var.get() is not None:
            self.ServerFrame.MainWindow.ServerData.fs_basepath = self.fs_basepath_var.get()
        if self.fs_homepath_var.get() is not None:
            self.ServerFrame.MainWindow.ServerData.fs_homepath = self.fs_homepath_var.get()
        if self.etpath_var.get() is not None:
            self.ServerFrame.MainWindow.ServerData.ETPath = self.etpath_var.get()
        if self.parameters_var.get() is not None:
            self.ServerFrame.MainWindow.ServerData.parameters = self.parameters_var.get()


class ServerListFrame(tkinter.Frame):
    """Contains the server list"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent

        self.config(background=Config['SERVERLIST_BACKGROUND'], padx=5, pady=5)

        # Server List Titles
        self.servers_label = tkinter.Label(self, text="Title", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.servers = tkinter.Listbox(self, width=20, relief="flat",
                                       borderwidth=0,
                                       font=FONT,
                                       selectbackground=Config['LIST_SELECT_BACK'],
                                       selectborderwidth=0,
                                       selectforeground=Config['LIST_SELECT_FORE'],
                                       exportselection=0,
                                       activestyle="none")

        self.servers.bind("<<ListboxSelect>>", self.select_server)
        self.servers.bind("<Double-Button-1>", self.ServerFrame.join_server)
        self.servers.bind("<MouseWheel>", self.event_mouse_wheel)
        self.servers_label.grid(row=0, column=0, sticky=N + W + E)
        self.servers.grid(row=1, column=0, sticky=N + W + E)

        # Server Map
        self.servermap_label = tkinter.Label(self, text="Map", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.servermap = tkinter.Listbox(self, width=20, relief="flat",
                                         borderwidth=0,
                                         font=FONT,
                                         selectbackground=Config['LIST_SELECT_BACK'],
                                         selectborderwidth=0,
                                         selectforeground=Config['LIST_SELECT_FORE'],
                                         exportselection=0,
                                         activestyle="none")

        self.servermap.bind("<<ListboxSelect>>", self.select_server)
        self.servermap.bind("<Double-Button-1>", self.ServerFrame.join_server)
        self.servermap.bind("<MouseWheel>", self.event_mouse_wheel)
        self.servermap_label.grid(row=0, column=1, sticky=N + W + E)
        self.servermap.grid(row=1, column=1, sticky=N + W + E)

        # Server Players
        self.serverplayers_label = tkinter.Label(self, text="Players", font=FONT,
                                                 background=Config['SERVERLIST_BACKGROUND'])
        self.serverplayers = tkinter.Listbox(self, width=10, relief="flat",
                                             borderwidth=0,
                                             font=FONT,
                                             selectbackground=Config['LIST_SELECT_BACK'],
                                             selectborderwidth=0,
                                             selectforeground=Config['LIST_SELECT_FORE'],
                                             exportselection=0,
                                             activestyle="none")

        self.serverplayers.bind("<<ListboxSelect>>", self.select_server)
        self.serverplayers.bind("<Double-Button-1>", self.ServerFrame.join_server)
        self.serverplayers.bind("<MouseWheel>", self.event_mouse_wheel)
        self.serverplayers_label.grid(row=0, column=2, sticky=N + W + E)
        self.serverplayers.grid(row=1, column=2, sticky=N + W + E)

        # Server Ping
        self.serverping_label = tkinter.Label(self, text="Ping", font=FONT, background=Config['SERVERLIST_BACKGROUND'])
        self.serverping = tkinter.Listbox(self, width=5, relief="flat",
                                          borderwidth=0,
                                          font=FONT,
                                          selectbackground=Config['LIST_SELECT_BACK'],
                                          selectborderwidth=0,
                                          selectforeground=Config['LIST_SELECT_FORE'],
                                          exportselection=0,
                                          activestyle="none")

        self.serverping.bind("<<ListboxSelect>>", self.select_server)
        self.serverping.bind("<Double-Button-1>", self.ServerFrame.join_server)
        self.serverping.bind("<MouseWheel>", self.event_mouse_wheel)
        self.serverping_label.grid(row=0, column=3, sticky=N + W + E)
        self.serverping.grid(row=1, column=3, sticky=N + W + E)

        self.grid_columnconfigure(0, weight=1)

    def show(self):
        self.grid(row=FRAME_SERVERLIST[0], column=FRAME_SERVERLIST[1], sticky=N + W)

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

    def add(self, server=None):
        if not server:
            return
        self.servers.insert(END, server['title'])
        self.servermap.insert(END, server['map'])
        self.serverplayers.insert(END, server['players'])
        self.serverping.insert(END, server['ping'])

    def select(self, select_id=None):
        if select_id is None:
            return
        self.servers.select_clear(0, END)
        self.servermap.select_clear(0, END)
        self.serverplayers.select_clear(0, END)
        self.serverping.select_clear(0, END)

        self.servers.select_set(select_id)
        self.servermap.select_set(select_id)
        self.serverplayers.select_set(select_id)
        self.serverping.select_set(select_id)

    def get(self):
        if self.servers.curselection():
            return self.servers.curselection()[0]
        if self.servermap.curselection():
            return self.servermap.curselection()[0]
        if self.serverping.curselection():
            return self.serverping.curselection()[0]
        if self.serverplayers.curselection():
            return self.serverplayers.curselection()[0]
        return None

    def get_full(self):
        if self.servers.curselection():
            return self.servers.curselection()
        if self.servermap.curselection():
            return self.servermap.curselection()
        if self.serverping.curselection():
            return self.serverping.curselection()
        if self.serverplayers.curselection():
            return self.serverplayers.curselection()
        return None

    def event_mouse_wheel(self, event):
        delta = event.delta * -1
        self.servers.yview("scroll", delta, "units")
        self.servermap.yview("scroll", delta, "units")
        self.serverping.yview("scroll", delta, "units")
        self.serverplayers.yview("scroll", delta, "units")
        return "break"

    # noinspection PyUnusedLocal
    def select_server(self, e):
        select_id = self.get()
        if select_id is None:
            return

        server = self.ServerFrame.MainWindow.ServerData.Servers[select_id]
        if not server:
            logfile("select_server: Error selecting server %d" % select_id)
            return

        logfile("select_server: Selecting server %s" % server['title'])

        self.select((select_id,))
        self.ServerFrame.ServerDataFrame.set(server)

        self.ServerFrame.button_joinserver.show()
        self.ServerFrame.button_removeserver.show()
        self.ServerFrame.server_status()

        command_info = self.ServerFrame.get_command_line(select_id)
        if command_info and command_info[0]:
            self.ServerFrame.NoticeLabel.set(command_info[0].replace('+', '\n+'))
            if Config['showcommandline']:
                self.ServerFrame.NoticeLabel.show()
            else:
                self.ServerFrame.NoticeLabel.hide()


class ServerDataFrame(tkinter.Frame):
    """Frame contains all server related frames"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent

        self.config(background=Config['SERVERDATA_BACKGROUND'])

        # Server title
        self.servertitle_var = tkinter.StringVar()
        self.servertitle_label = tkinter.Label(self, text="Title: ", font=FONT,
                                               background=Config['SERVERDATA_BACKGROUND'])
        self.servertitle_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                               foreground=Config['ENTRY_FOREGROUND'], textvariable=self.servertitle_var)

        self.servertitle_entry.bind(sequence='<KeyRelease>', func=self.update_server)
        self.servertitle_label.grid(row=0, column=0, sticky=N + W)
        self.servertitle_entry.grid(row=0, column=1, sticky=N + W + E)

        # Server Password
        self.serverpassword_var = tkinter.StringVar()
        self.serverpassword_label = tkinter.Label(self, text="Password: ", font=FONT,
                                                  background=Config['SERVERDATA_BACKGROUND'])
        self.serverpassword_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                  foreground=Config['ENTRY_FOREGROUND'],
                                                  textvariable=self.serverpassword_var)

        self.serverpassword_entry.bind(sequence='<KeyRelease>', func=self.update_server)

        # Server address
        self.serveraddress_var = tkinter.StringVar()
        self.serveraddress_label = tkinter.Label(self, text="Address: ", font=FONT,
                                                 background=Config['SERVERDATA_BACKGROUND'])
        self.serveraddress_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                 foreground=Config['ENTRY_FOREGROUND'],
                                                 textvariable=self.serveraddress_var)

        self.serveraddress_entry.bind(sequence='<KeyRelease>', func=self.update_server)
        self.serveraddress_label.grid(row=2, column=0, sticky=N + W)
        self.serveraddress_entry.grid(row=2, column=1, sticky=N + W + E)

        # Server ETPath
        self.serveretpath_var = tkinter.StringVar()
        self.serveretpath_label = tkinter.Label(self, text="ET: ", font=FONT,
                                                background=Config['SERVERDATA_BACKGROUND'])
        self.serveretpath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                foreground=Config['ENTRY_FOREGROUND'],
                                                textvariable=self.serveretpath_var)
        self.serveretpath_browse = BrowseButton(self, text="Browse...",
                                                command=lambda: self.ServerFrame.get_file_path(self.serveretpath_var,
                                                                                               self.update_server))

        self.serveretpath_entry.bind(sequence='<KeyRelease>', func=self.update_server)
        self.serveretpath_label.grid(row=3, column=0, sticky=N + W)
        self.serveretpath_entry.grid(row=3, column=1, sticky=N + W + E)
        self.serveretpath_browse.grid(row=3, column=2, sticky=N + E)

        # Server fs_basepath
        self.serverfs_basepath_var = tkinter.StringVar()
        self.serverfs_basepath_label = tkinter.Label(self, text="fs_basepath: ", font=FONT,
                                                     background=Config['SERVERDATA_BACKGROUND'])
        self.serverfs_basepath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                     foreground=Config['ENTRY_FOREGROUND'],
                                                     textvariable=self.serverfs_basepath_var)
        self.serverfs_basepath_browse = BrowseButton(self, text="Browse...", command=lambda: self.ServerFrame.get_path(
            self.serverfs_basepath_var, self.update_server))

        if Config['showbasepath']:
            self.serverfs_basepath_entry.bind(sequence='<KeyRelease>', func=self.update_server)
            self.serverfs_basepath_label.grid(row=4, column=0, sticky=N + W)
            self.serverfs_basepath_entry.grid(row=4, column=1, sticky=N + W + E)
            self.serverfs_basepath_browse.grid(row=4, column=2, sticky=N + E)

        # Server fs_homepath
        self.serverfs_homepath_var = tkinter.StringVar()
        self.serverfs_homepath_label = tkinter.Label(self, text="fs_homepath: ", font=FONT,
                                                     background=Config['SERVERDATA_BACKGROUND'])
        self.serverfs_homepath_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                     foreground=Config['ENTRY_FOREGROUND'],
                                                     textvariable=self.serverfs_homepath_var)
        self.serverfs_homepath_browse = BrowseButton(self, text="Browse...", command=lambda: self.ServerFrame.get_path(
            self.serverfs_homepath_var, self.update_server))

        if Config['showhomepath']:
            self.serverfs_homepath_entry.bind(sequence='<KeyRelease>', func=self.update_server)
            self.serverfs_homepath_label.grid(row=5, column=0, sticky=N + W)
            self.serverfs_homepath_entry.grid(row=5, column=1, sticky=N + W + E)
            self.serverfs_homepath_browse.grid(row=5, column=2, sticky=N + E)

        # Server extra parameters
        self.serverparams_var = tkinter.StringVar()
        self.serverparams_label = tkinter.Label(self, text="Parameters: ", font=FONT,
                                                background=Config['SERVERDATA_BACKGROUND'])
        self.serverparams_entry = tkinter.Entry(self, font=FONT, background=Config['ENTRY_BACKGROUND'],
                                                foreground=Config['ENTRY_FOREGROUND'],
                                                textvariable=self.serverparams_var)

        self.serverparams_entry.bind(sequence='<KeyRelease>', func=self.update_server)
        self.serverparams_label.grid(row=6, column=0, sticky=N + W)
        self.serverparams_entry.grid(row=6, column=1, sticky=N + W + E)
        self.grid_columnconfigure(1, minsize=400)

    def show(self):
        self.grid(row=FRAME_SERVERDATA[0], column=FRAME_SERVERDATA[1], sticky=N)

    def hide(self):
        self.grid_forget()

    def show_password(self):
        self.serverpassword_label.grid(row=1, column=0, sticky=N + W)
        self.serverpassword_entry.grid(row=1, column=1, sticky=N + W + E)

    def hide_password(self):
        self.serverpassword_label.grid_forget()
        self.serverpassword_entry.grid_forget()

    def set(self, server=None):
        if not server:
            return
        self.servertitle_var.set(server['title'])
        self.serveraddress_var.set(server['address'])
        self.serverpassword_var.set(server['password'])
        self.serverparams_var.set(server['parameters'])
        self.serverfs_basepath_var.set(server['fs_basepath'])
        self.serverfs_homepath_var.set(server['fs_homepath'])
        self.serveretpath_var.set(server['ETPath'])
        self.show()

    # noinspection PyUnusedLocal
    def update_server(self, e):
        select_id = self.ServerFrame.ServerListFrame.get()
        if select_id is None:
            return
        server = self.ServerFrame.MainWindow.ServerData.Servers[select_id]
        if not server:
            logfile("update_server: Error updating server status %d" % select_id)
            return
        logfile("update_server: Updating %s at %d" % (server['title'], select_id))

        if self.servertitle_var.get() is None:
            server['title'] = self.servertitle_var.get()
        if self.serveraddress_var.get() is None:
            server['address'] = self.serveraddress_var.get()
        if self.serverpassword_var.get() is None:
            server['password'] = self.serverpassword_var.get()
        if self.serverparams_var.get() is None:
            server['parameters'] = self.serverparams_var.get()
        if self.serverfs_basepath_var.get() is None:
            server['fs_basepath'] = self.serverfs_basepath_var.get()
        if self.serverfs_homepath_var.get() is None:
            server['fs_homepath'] = self.serverfs_homepath_var.get()
        if self.serveretpath_var.get() is None:
            server['ETPath'] = self.serveretpath_var.get()
        self.ServerFrame.refresh_list(select_id)

    def clear(self):
        self.servertitle_var.set('')
        self.serveraddress_var.set('')
        self.serverpassword_var.set('')
        self.serverparams_var.set('')
        self.serverfs_basepath_var.set('')
        self.serverfs_homepath_var.set('')
        self.serveretpath_var.set('')


class ServerStatusFrame(tkinter.Frame):
    """Contains actual serverdata information such as players and cvars"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.ServerFrame = parent

        self.config(background=Config['SERVERSTATUS_BACKGROUND'])

        self.current_line = 1

        self.text = tkinter.Text(
            self,
            background=Config['SERVERSTATUS_BACKGROUND'],
            font=FONT,
            relief="flat",
            wrap="none",
            width=54,
            height=35,
        )

        self.text.tag_config("headerLine", foreground=Config['BUTTON_FOREGROUND'],
                             background=Config['BUTTON_BACKGROUND'], underline=1)

        self.text.grid(sticky=W + N)

        self.text_scroll = tkinter.Scrollbar(self, command=self.text.yview, background=Config['BUTTON_BACKGROUND'])
        self.text.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.grid(row=0, column=1, sticky="ns")

    def show(self):
        print("Showing frame")
        self.grid(row=FRAME_SERVERSTATUS[0], column=FRAME_SERVERSTATUS[1], sticky=N + W, rowspan=4)

    def hide(self):
        self.grid_forget()

    def get_line_number(self):
        self.current_line += 1
        data = "%d.%d" % (self.current_line, 0)
        # logfile("Line data = %s right?" % data )
        return data

    def insert_line(self, text, tag=None):
        self.text.config(state=NORMAL)
        if tag is None:
            self.text.insert(self.get_line_number(), text + '\n')
        else:
            self.text.insert(self.get_line_number(), text + '\n', tag)
        self.text.config(state=DISABLED)

    def clear(self):
        self.current_line = 0
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=DISABLED)


class NoticeLabel(tkinter.Label):
    def __init__(self, parent=None, cnf=None, **kw):
        if not cnf:
            cnf = {}
        tkinter.Label.__init__(self, parent, cnf, **kw)
        self.ServerFrame = parent
        self.text_variable = tkinter.StringVar(
            value="FS_Basepath and FS_Homepath are not required.\n" +
                  "They will be set to the folder of you ET.exe if not specified.")

        self.config(font=FONT, background=Config['WINDOW_BACKGROUND'], textvariable=self.text_variable)

        # self.show()

    def set(self, message=""):
        self.text_variable.set(message)

    def show(self):
        self.grid(row=LABEL_NOTICE[0], column=LABEL_NOTICE[1], sticky=N + W, rowspan=2)

    def hide(self):
        self.grid_forget()


class ServerFrame(tkinter.Frame):
    """Frame contains all server related frames"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.MainWindow = parent

        self.config(background=Config['WINDOW_BACKGROUND'], padx=5, pady=5)

        self.HeaderFrame = HeaderFrame(self)
        self.ServerListFrame = ServerListFrame(self)
        self.ServerDataFrame = ServerDataFrame(self)
        self.ServerStatusFrame = ServerStatusFrame(self)

        self.button_addserver = MenuButton(self.MainWindow.navbar, BUTTON_ADD, text="Add", command=self.add_server)
        self.button_removeserver = MenuButton(self.MainWindow.navbar, BUTTON_REMOVE, text="Remove",
                                              command=self.remove_server)
        # self.button_rcon = MenuButton( self.parent.navbar , BUTTON_RCON , text="Rcon"       , command=parent.rcon)
        self.button_joinserver = MenuButton(self.MainWindow.navbar, BUTTON_JOIN, text="Join", command=self.join_server)
        self.button_addserver.show()

        self.HeaderFrame.show()
        self.ServerListFrame.show()
        self.NoticeLabel = NoticeLabel(self)

        self.grid(sticky=W + S + N + E)

        self.after(100, self.create_server_list)

    def create_server_list(self):
        self.ServerStatusFrame.hide()
        self.ServerDataFrame.hide()
        self.ServerDataFrame.clear()
        self.button_joinserver.hide()
        self.button_removeserver.hide()
        self.get_server_list()
        # self.refresh_list(None)

    def refresh_list(self, select_id=None):
        self.ServerListFrame.clear()
        for Server in self.MainWindow.ServerData.Servers:
            self.ServerListFrame.add(Server)
        if select_id is not None:
            self.ServerListFrame.select(select_id)

    # Buttons
    def add_server(self):  # Leaving error checking up to the join command
        server_title = tkinter.simpledialog.askstring("New Server Title", "Please insert a unique server title")
        if not server_title or any(s['title'] == server_title for s in self.MainWindow.ServerData.Servers):
            logfile("add_server: Invalid server title")
            return
        server_address = tkinter.simpledialog.askstring("New Server Address", "Please insert full server address." +
                                                        "(unique)\nExample: 127.0.0.1:27960\n" +
                                                        "If it is a hostname make sure you have the port at the end")
        if not server_address or any(s['address'] == server_address for s in self.MainWindow.ServerData.Servers):
            logfile("add_server: Invalid server address")
            return
        self.MainWindow.ServerData.add_server({'address': server_address, 'title': server_title})
        self.create_server_list()
        self.ServerListFrame.select(END)  # Select added server

        self.refresh_list(None)

    def remove_server(self):
        select_id = self.ServerListFrame.get()
        if select_id is None:
            return
        if not self.MainWindow.ServerData.Servers[select_id]:
            logfile("remove_server: Error updating server %d" % select_id)
            return
        del self.MainWindow.ServerData.Servers[select_id]
        self.create_server_list()

    # noinspection PyUnusedLocal
    def get_command_line(self, select_id=None):
        # TODO Move this to serverdata?
        if select_id is None:
            return
        server = self.MainWindow.ServerData.Servers[select_id]
        if not server:
            logfile("get_command_line: Error getting command line for server %d" % select_id)
            return
        # Generate Startup Line #
        etpath = ''
        fs_basepath = ''
        fs_homepath = ''
        fs_game = 'etmain'  # Etmain by default if mod does not exist
        parameters = ''
        address = server['address']
        password = server['password']

        # Check ET Path
        # This entry is required
        # If not exist then return None for command line
        if server['ETPath']:
            etpath = server['ETPath']
        else:
            etpath = self.MainWindow.ServerData.ETPath
        if not isfile(etpath):
            logfile("getcommandline: ET Path is not valid file")
            return None

        # Check for fs_basepath
        # This entry is not required
        # If not exist then do not add it to line ?
        if server['fs_basepath']:
            fs_basepath = server['fs_basepath']
        else:
            fs_basepath = self.MainWindow.ServerData.fs_basepath
        if not isdir(fs_basepath):
            fs_basepath = ''  # will this work? or will it just default to wolfstarter directory
        # if not fs_basepath: fs_basepath = "/".join(etpath.replace('\\', '/').split("/")[0:-1])

        # Check for fs_homepath
        # This entry is not required
        # If not exist then do not add to line ?
        if server['fs_homepath']:
            fs_homepath = server['fs_homepath']
        else:
            fs_homepath = self.MainWindow.ServerData.fs_homepath
        if not isdir(fs_homepath):
            fs_homepath = ''
        # if not fs_homepath: fs_homepath = fs_basepath

        # Paramaters are extra parameters like exec configs or something.
        if self.MainWindow.ServerData.parameters:
            parameters = self.MainWindow.ServerData.parameters
        if server['parameters']:
            if parameters:
                parameters += ' '
            parameters += server['parameters']

        if Config['launchmod']:
            if "gamename" in server['cvar']:
                fs_game = server['cvar']['gamename']
            if fs_basepath:
                if not isdir(join(fs_basepath, fs_game)):
                    logfile("get_command_line: Mod path does not exist in basepath - setting to etmain")
                    fs_game = "etmain"
            else:
                etpathdir = "/".join(etpath.replace('\\', '/').split("/")[0:-1])
                if not isdir(join(etpathdir, fs_game)):
                    logfile("get_command_line: Mod path does not exist in et path - setting to etmain")
                    fs_game = "etmain"

        if not address:
            logfile("get_command_line: Address not valid")
            return
        if not isfile(etpath):
            logfile("get_command_line: ET Executable is not valid")
            return

        commandline = "\"%s\"" % etpath
        if fs_basepath and isdir(fs_basepath):
            commandline += " +set fs_basepath \"%s\"" % fs_basepath
        if fs_homepath and isdir(fs_homepath):
            commandline += " +set fs_homepath \"%s\"" % fs_homepath
        if fs_game and fs_game != "etmain":
            commandline += " +set fs_game %s" % fs_game

        if parameters:
            commandline += ' ' + parameters

        if password and "g_needpass" in server['cvar'] and int(server['cvar']['g_needpass']) == 1:
            commandline += ' +set password ' + password
        commandline += ' +connect ' + address

        # End command line generate #

        logfile("get_command_line: " + commandline)
        return commandline, "/".join(etpath.replace('\\', '/').split("/")[0:-1])

    # noinspection PyUnusedLocal
    def join_server(self, e=None):
        select_id = self.ServerListFrame.get()
        if select_id is None:
            return
        command_info = self.get_command_line(select_id)
        if not command_info or not command_info[0] or not command_info[1]:
            logfile("join_server: Couldn't find command line")
            LogWindow(self.MainWindow,
                      "There was an error with your configuration. This error log should tell you what went wrong.")
            return
        cwd = getcwd()
        logfile("join_server: Changing directory to %s" % command_info[1])
        chdir(command_info[1])
        logfile("join_server: Joining server %s" % select_id)
        open_process(command_info[0])
        logfile("join_server: Returning directory to %s" % cwd)
        chdir(cwd)

    def get_server_list(self):
        self.ServerListFrame.clear()
        for x in range(0, len(self.MainWindow.ServerData.Servers)):
            self.MainWindow.ServerData.getstatus(x)
            self.set_server_info(x)
            self.ServerListFrame.add(self.MainWindow.ServerData.Servers[x])
            self.update_idletasks()

    def set_server_info(self, serverid=None):
        if serverid is None:
            return
        server = self.MainWindow.ServerData.Servers[serverid]
        if not server:
            return
        if server['ping'] <= 0:
            return
        current_players = 0
        current_bots = 0
        for player in server['playerlist']:
            if player['ping'] == 0:
                current_bots += 1
            else:
                current_players += 1
        server['players'] = "%d/%d (%d)" % (current_players, int(server['cvar']['sv_maxclients']), current_bots)

    def server_status(self, select_id=None):
        if select_id is None:
            select_id = self.ServerListFrame.get()
        if select_id is None:
            logfile("server_status: No select_id selected")
            return

        server = self.MainWindow.ServerData.Servers[select_id]

        if not server:
            logfile("server_status: Error getting server player list %d" % select_id)
            return
        self.ServerStatusFrame.clear()
        self.ServerStatusFrame.hide()

        logfile("server_status: Getting server status for %d (%s)" % (select_id, server['title']))

        self.MainWindow.ServerData.getstatus(select_id)

        if server['ping'] <= 0:
            logfile("server_status: Could not ping server")
            return

        if "sv_hostname" in server['cvar']:
            self.ServerStatusFrame.insert_line(
                "%s : %s" % ("Server Name".ljust(11), clean_str(server['cvar']['sv_hostname']).ljust(HEADERLENGTH)))
        if "mapname" in server['cvar']:
            self.ServerStatusFrame.insert_line(
                "%s : %s" % ("Map".ljust(11), server['cvar']['mapname'].ljust(HEADERLENGTH)))
        if "gamename" in server['cvar']:
            self.ServerStatusFrame.insert_line(
                "%s : %s" % ("Mod".ljust(11), server['cvar']['gamename'].ljust(HEADERLENGTH)))
        self.ServerStatusFrame.insert_line(
            "%s : %s" % ("Ping".ljust(11), (str(server['ping']) + 'ms').ljust(HEADERLENGTH)))
        self.ServerStatusFrame.insert_line('')
        self.ServerStatusFrame.insert_line("%s %s %s" % (
            "Name".ljust(PLAYER_NAME_LENGTH), "Ping".ljust(PLAYER_PING_LENGTH), "Score".ljust(PLAYER_SCORE_LENGTH)),
                                           "headerLine")

        for player in server['playerlist']:
            name = clean_str(player['name'][:PLAYER_NAME_LENGTH]) if len(
                clean_str(player['name'])) > PLAYER_NAME_LENGTH else clean_str(player['name'])
            self.ServerStatusFrame.insert_line("%s %s %s" % (
                name.ljust(PLAYER_NAME_LENGTH), str(player['ping']).ljust(PLAYER_PING_LENGTH),
                str(player['score']).ljust(PLAYER_SCORE_LENGTH)))

        self.ServerStatusFrame.insert_line('')
        self.ServerStatusFrame.insert_line('')
        self.ServerStatusFrame.insert_line("%s | %s" % ("Cvar".ljust(HALFLEN), "Value".ljust(HALFLEN)), "headerLine")
        for cvar in server['cvar']:
            self.ServerStatusFrame.insert_line("%s = %s" % (cvar.ljust(HALFLEN), server['cvar'][cvar].ljust(HALFLEN)))
        self.set_server_info(select_id)
        self.refresh_list(select_id)
        if 'g_needpass' in server['cvar'] and int(server['cvar']['g_needpass']) == 1:
            self.ServerDataFrame.show_password()
        else:
            self.ServerDataFrame.hide_password()
        self.ServerStatusFrame.show()

    # Methods
    def get_path(self, browse_var=None, update_method=None):
        if not browse_var:
            return
        if not update_method:
            return
        current_directory = browse_var.get()
        if not current_directory or not isdir(current_directory):
            current_directory = getcwd()
        self.MainWindow.focus_ignore = True
        dir_path = tkinter.filedialog.askdirectory(parent=self, initialdir=current_directory,
                                                   title="Navigate to your path")
        self.MainWindow.focus_ignore = False

        if dir_path and isdir(dir_path):
            browse_var.set(dir_path)
            update_method(self)
        else:
            logfile("getpath-dialog: Could not find directory path")

    def get_file_path(self, browse_var=None, update_method=None):
        if not browse_var:
            return
        if not update_method:
            return
        current_directory = browse_var.get()
        if not current_directory or not isdir(current_directory):
            current_directory = getcwd()
        self.MainWindow.focus_ignore = True
        file_path = tkinter.filedialog.askopenfilename(parent=self, initialdir=current_directory,
                                                       title="Navigate to your your exe",
                                                       filetypes=(("exe files", "*.exe"), ("All files", "*")), )
        self.MainWindow.focus_ignore = False

        if file_path and isfile(file_path):
            browse_var.set(file_path)
            update_method(self)
        else:
            logfile("getfilepath-dialog: Could not find filepath")

    def close_window(self):
        self.button_addserver.destroy()
        self.button_removeserver.destroy()
        self.button_joinserver.destroy()
        for child in self.winfo_children():
            child.destroy()
        self.destroy()


class LogWindow(tkinter.Toplevel):
    def __init__(self, parent=None, label_text="", cnf=None, **kw):
        if not cnf:
            cnf = {}
        tkinter.Toplevel.__init__(self, parent, cnf, **kw)
        self.MainWindow = parent
        self.config(background=Config['WINDOW_BACKGROUND'], padx=5, pady=5)
        self.title("Log Window")

        if label_text:
            self.label = tkinter.Label(self, text=label_text, background="#000000", foreground="#FF0000")
            self.label.grid(row=0, column=0, columnspan=2)

        self.textbox = tkinter.Text(self, width=115, height=47)

        self.text_scroll = tkinter.Scrollbar(self, command=self.textbox.yview, background=Config['BUTTON_BACKGROUND'])
        self.textbox.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.grid(row=1, column=1, sticky="nse")

        with open('wolfstarter.log') as wolfstarter_file:
            wolfstarter_log = wolfstarter_file.read()

        self.textbox.insert(END, wolfstarter_log)
        self.textbox.yview(END)
        self.textbox.grid(row=1, column=0, sticky="W")
        self.grid()


class SettingCheckButton(tkinter.Checkbutton):
    def __init__(self, master=None, label_text=None, row=0, cnf=None, **kw):
        if not cnf:
            cnf = {}
        tkinter.Checkbutton.__init__(self, master, cnf, **kw)

        self.Settings = master

        self.var = tkinter.IntVar()

        self.config(variable=self.var, background=Config['WINDOW_BACKGROUND'])
        self.label = tkinter.Label(self.Settings, text=label_text, background=Config['WINDOW_BACKGROUND'])
        self.label.grid(row=row, column=0, sticky=W)

        self.grid(row=row, column=1, sticky=W)

    def get(self):
        if self.var.get() == 1:
            return True
        else:
            return False


class Settings(tkinter.Frame):
    """Sepearate window for settings"""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.MainWindow = parent

        self.config(background=Config['WINDOW_BACKGROUND'], padx=5, pady=5)

        self.label_info = tkinter.Label(self, text="The color options are only editable in wolfstarter.json",
                                        background=Config['WINDOW_BACKGROUND'])
        self.label_info.grid(sticky=W)

        self.launchmod = SettingCheckButton(self, "Launches ET with the mod of the server instead of etmain", 1)
        self.basepath = SettingCheckButton(self, "Show the basepath text entry", 2)
        self.homepath = SettingCheckButton(self, "Show the homepath text entry", 3)
        self.command = SettingCheckButton(self, "Show the full command line text that will be sent to et executable", 4)
        self.windowborder = SettingCheckButton(self, "Show the Windows's window border at all times", 5)
        self.check_update = SettingCheckButton(self, "Check for update on startup", 6)

        self.savebutton = MenuButton(self, 0, 6, text="save", command=self.close_window)
        self.savebutton.show()

        if Config['launchmod']:
            self.launchmod.toggle()
        if Config['showbasepath']:
            self.basepath.toggle()
        if Config['showhomepath']:
            self.homepath.toggle()
        if Config['showcommandline']:
            self.command.toggle()
        if Config['windowborder']:
            self.windowborder.toggle()
        if Config['checkupdate']:
            self.check_update.toggle()

        self.grid()

    def close_window(self):
        Config['launchmod'] = self.launchmod.get()
        Config['showbasepath'] = self.basepath.get()
        Config['showhomepath'] = self.homepath.get()
        Config['showcommandline'] = self.command.get()
        Config['windowborder'] = self.windowborder.get()
        Config['checkupdate'] = self.check_update.get()

        self.MainWindow.save_config()
        for child in self.winfo_children():
            child.destroy()
        self.MainWindow.ServerData = ServerData()
        self.MainWindow.ServerData.load_server_file(Config['servers'])
        self.MainWindow.ServerFrame = ServerFrame(self.MainWindow)

        if self.windowborder.get():
            self.MainWindow.overrideredirect(False)
        else:
            self.MainWindow.overrideredirect(True)

        self.destroy()


class Window(tkinter.Tk):
    def __init__(self):
        global FONT  # Do I need?
        self.focus_ignore = False
        self.minimized = False
        self.x = None
        self.y = None
        self.load_config()

        tkinter.Tk.__init__(self)
        FONT = tkinter.font.Font(family="Courier New", size=10)
        # self.bind("<FocusIn>"         , self.OnFocus)
        # self.bind("<FocusOut>"        , self.OnLostFocus)
        if not Config['windowborder']:
            self.overrideredirect(True)
        self.config(background=Config['WINDOW_BORDER'], padx=5, pady=5)  # Set padding and background color
        self.title("WolfStarter by Zelly")
        self.bind("<FocusIn>", self.event_window_focus)
        self.bind("<FocusOut>", self.event_window_focus_lost)
        self.bind("<Configure>", self.event_window_configure)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.iconbitmap('WolfStarterLogo.ico')

        self.mainframe = tkinter.Frame(self, background=Config["WINDOW_BACKGROUND"])

        self.navbar = NavBar(self)

        # Bind the move window function
        self.navbar.bind("<ButtonPress-1>", self.event_window_move_start)
        self.navbar.bind("<ButtonRelease-1>", self.event_window_move_stop)
        self.navbar.bind("<B1-Motion>", self.event_window_move)

        self.mainframe.grid()

        self.ServerData = ServerData()
        self.ServerData.load_server_file(Config['servers'])
        self.ServerFrame = ServerFrame(self)

        self.mainloop()

    # noinspection PyMethodMayBeStatic
    def load_config(self):
        logfile(str(" Loading config ").center(24, "-"))
        if not isfile(join(getcwd(), 'wolfstarter.json')):
            logfile("Config not found using default")
        else:
            with open(join(getcwd(), 'wolfstarter.json')) as json_config:
                json_date = json.load(json_config)
            if json_date:
                for key in json_date:
                    if key in Config:
                        Config[key] = json_date[key]
                        logfile(key.ljust(32) + " = " + str(json_date[key]))
                        # Make sure to only do keys that exist.
        logfile(str(" Loaded config ").center(24, "-"))

    def save_config(self):
        self.ServerData.save_server_file(Config['servers'])
        json_config = open(join(getcwd(), 'wolfstarter.json'), 'w')
        json.dump(Config, json_config, skipkeys=True, sort_keys=True, indent=4)

    # Opening and closing files and application
    def open_servers_file(self):
        self.focus_ignore = True
        file_name = tkinter.filedialog.askopenfilename(
            parent=self,
            initialdir=getcwd(),
            title="Select servers file",
            filetypes=(("json file", "*.json"), ("All files", "*")),
        )
        if not file_name:
            self.focus_ignore = False
            logfile("No file from dialog")
            return
        if not isfile(file_name):
            tkinter.messagebox.showinfo(title="Invalid servers file", message="Servers file was not found", parent=self)
            self.focus_ignore = False
            logfile("Invalid Servers file was not found %s" % file_name)
            return
        self.focus_ignore = False
        Config['servers'] = file_name
        self.ServerData = ServerData()
        self.ServerData.load_server_file(Config['servers'])
        logfile("Loaded Servers file: %s" % Config['servers'])
        if self.ServerFrame:
            self.ServerFrame.destroy()
        self.ServerFrame = ServerFrame(self)

    def save_as_file(self):
        self.focus_ignore = True
        file_name = tkinter.filedialog.asksaveasfilename(
            parent=self,
            initialdir=getcwd(),
            title="Select servers file",
            filetypes=(("json file", "*.json"), ("All files", "*")),
        )
        if not file_name:
            tkinter.messagebox.showinfo(title="Invalid servers file", message="Servers file was not found", parent=self)
            self.focus_ignore = False
            # self.parent.focus_force()
            logfile("saveasfile: Invalid Servers file was not found %s" % file_name)
            return
        self.focus_ignore = False
        Config['servers'] = file_name
        self.ServerData.save_server_file(Config['servers'])
        logfile("save_as_file: Saved servers file %s" % Config['servers'])

    def quit(self):
        self.save_config()
        self.destroy()

    # Moving application on screen
    def event_window_move_start(self, event):
        self.x = event.x
        self.y = event.y

    # noinspection PyUnusedLocal
    def event_window_move_stop(self, event):
        self.x = None
        self.y = None

    def event_window_move(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        self.geometry("+%s+%s" % (x, y))

    # noinspection PyUnusedLocal
    def event_window_focus(self, event):
        if Config['windowborder']:
            return  # Ignore window focus events
        if self.minimized or self.focus_ignore:
            return
        w = self.focus_get()
        if w:
            self.overrideredirect(True)
            w.focus_force()

    # noinspection PyUnusedLocal
    def event_window_focus_lost(self, event):
        if Config['windowborder']:
            return  # Ignore window focus events
        if self.minimized or self.focus_ignore:
            return
        if not self.focus_get():
            self.overrideredirect(False)

    # noinspection PyUnusedLocal
    def event_window_configure(self, event):
        if Config['windowborder']:
            return  # Ignore window focus events
        if self.minimized and not self.focus_get():
            # If minimized, and window does not have focus and there is a new event.
            # Is most likely that the event is a maximize event.
            # However the window isn't maximized until after this event.
            def task():
                if self.minimized and self.focus_get():
                    self.minimized = False
                    self.overrideredirect(True)

            self.after(50, task)  # Do task after 50 ms (Basically after the window is maximized)
