# ETWolfStarter
Wolfenstein: Enemy Territory launcher.
  
* Add servers to favourites, and see who is on the server.
* Customize per servers file(a collection of related server favourites) or per server your parameters,paths, and executable.  
  
![e520f9ebe590c73cf185b3c44d966954](http://i.gyazo.com/e520f9ebe590c73cf185b3c44d966954.png)
## Table of Contents  
* **[Donate](#donate)**  
* **[Changes](#changes)**  
* **[Download](#choosing-a-package-to-download)**  
* **[The Rest](#the-rest)**  
* **[Configure](#configuring)**  

## Donate
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=45BP8LRVZW7JC&lc=US&item_name=Zelly%20Github%20Donate&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted"><img src="https://cloud.githubusercontent.com/assets/705940/8636137/65b21c0a-2817-11e5-93b1-5cfe64500830.gif" /></a>  
If you wish to donate I would be grateful, maybe I could buy a new computer!  

## Changes
### 1.2.1
* Added an automatic updater (testing)
* Added an icon
* Added double click server to join
* Fixed many config options not taking affect
* Fixed minimize button sometimes not showing
* Fixed selecting server columns
* Fixed the scrolling moving in reverse for the serverlist
* Lowered the socket timeout to 500ms from 2000ms to speed up things for offline servers
* Changed default color pattern 
  
### 1.1.0
* Added a sort of error log wrapper. Saves to wolfstarter.log. Look in there if there are unknown issues.
* Added more color options
* Added option to disable adding fs_game gamename to startup parameters. **launchmod** in wolfstarter.json
* Added a check to make sure you have the mod folder in your basepath, if not then default to etmain.
* Added a minimize button(Unfortunately cannot minimize to tray sorry)
* Added a notice label at the bottom telling you you do not need fsbasepath and fshomepath.  
Also when selecting a server it will tell you all the arguments it is using and in what order.
* Updated the arrangement of the entry fields to make more sense
* Updated scrolling in serverlist to synchronize all categories

## Choosing a package to download  
I have decided to stick with only the zip packaging as it works better in all categories.  
Check out out the latest release here: https://github.com/Zelly/ETWolfStarter/releases  
  
## Running ETWolfStarter
Both when ran will create a wolfstarter.json this file should always stay in the same directory as the WolfStarter.exe  
### The Menu
#### Open...
Will open a servers json file which contains a list of servers. You won't have one to open on your first run.
#### Save...
By default the first server file will save to servers.json next to your executable. If you want to change this you can select a new area to save here. If you want to save all your silent mod servers in one file you can save your list as silent.json and then for etpro servers save that list as etpro.json.
#### Quit
Saves your server list to the serversfile you have selected with Save...  
**Warning: If you close the application some other way, your data will not save**
#### Add
Will ask you for a unique title and unique IP to a server.  
After inputted you will see your server added to your list.
#### Remove
You can only see this option when selected on a server. It will delete the server from your list.
#### Join...
Will join the server with the options you have defined for that server.

### The Rest
What you will see when you have added a server is 3 areas(From top to bottom):  
* **Settings**  
Contains **fs_basepath**,**fs_homepath**, **et executable path**. These are the settings to be used if a server doesn't have them defined.  
For normal ET Installations fs_basepath and fs_homepath will be the same. And ET Path will be fs_basepath/ET.exe  
You are only **required** to set the etpath  
The setting in this section is **parameters** this will be added to your startup line **before** the server parameters setting.  
* **Server List**  
This contains all of your servers you have added for your current list.  
It will display their title/ping/map and players  
The players will display like this: REALPLAYERS/MAXPLAYERS (BOTS)  
If you select a server a new frame will popup to the right containing the actual server data.  
The serverdata will display all of the currently connected players and the server's server cvars from a getstatus request  
* **Server Settings**  
Has all of the same things as **Settings** but remember the paths are used from here if they are defined.  
The parameters are placed **after** the **Settings** paramaters but **before** the connect and password.  
**Address** is the full address of the server. (Accepts hostnames)  
If the server has a g_needpass = 1 in its cvars then a password entry will also popup.  
Another note is that the gamename will be applied to your startup line as well.  
This means the launcher will start in the mod you are connecting to, which could cause errors if you do not have the mod.(Will fix in later versions, is pretty easy)  

## Configuring
In wolfstarter.json there is color codes you can change if you want different colors for the application.
