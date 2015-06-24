# ETWolfStarter
Wolfenstein: Enemy Territory launcher.
  
* Add servers to favourites, and see who is on the server.
* Customize per servers file(a collection of related server favourites) or per server your parameters,paths, and executable.

![fbe074dd4e26b59ad8e9412d77761b6b](https://cloud.githubusercontent.com/assets/705940/8338982/f9057732-1a79-11e5-858d-aef47f1fe0a0.png)

## Choosing a package to download
** You only need one of the following: **
* **WolfStarter-vX.X.X.exe
> Is a single executable which will be kind of large.
> However this one will load slower than the folder installation.
* **WolfStarter-vX.X.X.zip**
> Is a folder based installation, it contains WolfStarter.exe and a bunch of files required by the exe.
> This one loads faster.
> You can't move the exe out of this folder.
  
## Running ETWolfStarter
Both when ran will create a wolfstarter.json this file should always stay in the same directory as the WolfStarter.exe  
### The Menu
#### Open...
Will open a servers json file which contains a list of servers. You won't have one to open on your first run.
#### Save...
By default the first server file will save to servers.json next to your executable. If you want to change this you can select a new area to save here. If you want to save all your silent mod servers in one file you can save your list as silent.json and then for etpro servers save that list as etpro.json.
#### Quit
Saves your server list to the serversfile you have selected with Save...  
** Warning: If you close the application some other way, your data will not save **
#### Add
Will ask you for a unique title and unique IP to a server.  
After inputted you will see your server added to your list.
#### Remove
You can only see this option when selected on a server. It will delete the server from your list.
#### Join...
Will join the server with the options you have defined for that server.

### The Rest
What you will see when you have added a server is 3 areas(From top to bottom):  
* ** Settings **
> Contains **fs_basepath**,**fs_homepath**, **et executable path**. These are the settings to be used if a server doesn't have them defined.
> For normal ET Installations fs_basepath and fs_homepath will be the same. And ET Path will be fs_basepath/ET.exe
> You are only **required** to set the etpath
> The setting in this section is **parameters** this will be added to your startup line **before** the server parameters setting.
* ** Server List **
> This contains all of your servers you have added for your current list.
> It will display their title/ping/map and players
> The players will display like this: REALPLAYERS/MAXPLAYERS (BOTS)
> If you select a server a new frame will popup to the right containing the actual server data.
> The serverdata will display all of the currently connected players and the server's server cvars from a getstatus request
* ** Server Settings **
> Has all of the same things as ** Settings ** but remember the paths are used from here if they are defined.
> The parameters are placed **after** the ** Settings ** paramaters but **before** the connect and password.
> **Address** is the full address of the server. (Accepts hostnames)
> If the server has a g_needpass = 1 in its cvars then a password entry will also popup.
> Another note is that the gamename will be applied to your startup line as well.
> This means the launcher will start in the mod you are connecting to, which could cause errors if you do not have the mod.(Will fix in later versions, is pretty easy)

## Configuring
In wolfstarter.json there is color codes you can change if you want different colors for the application.