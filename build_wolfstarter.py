from subprocess import call
from shutil import move,rmtree,copyfile
from os import makedirs,walk,getcwd,chdir
from os.path import isdir,exists,join,abspath
from zipfile import ZipFile,ZIP_DEFLATED
buildOneFile=False
def zipdir(path,zippath,mode="w",extradir=None):
    zippath = abspath(zippath)
    cwd     = getcwd()
    chdir(path)
    zipH = ZipFile(zippath,mode,compression=ZIP_DEFLATED)
    for root , _ , files in walk('.'):
        for file in files:
            if extradir:
                zipH.write(join(root,file),arcname=extradir+join(root,file))
            else:
                zipH.write(join(root,file))
    zipH.close()
    chdir(cwd)
    
def main():
    version = input("What version tag are you using? ")
    input("Is v%s correct? (If not then do Ctrl+C)" % version)
    
    releasedir="releases/ETWolfStarter-v%s" % version
    if isdir(releasedir): input("That version folder already exists, do you wish to overwrite? (Ctrl+C to cancel)")
    if not exists(releasedir) or not isdir(releasedir): makedirs(releasedir)
    
    print("Building WolfStarter")
    if buildOneFile: call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefile_dist --workpath=./onefile_build -y -w --onefile WolfStarter.py")
    call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefolder_dist --workpath=./onefolder_build -y -w --onedir WolfStarter.py")
    
    print("Building WolfStarterUpdater")
    if buildOneFile: call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefile_updater_dist --workpath=./onefile_updater_build -y -w --onefile updater/WolfStarterUpdater.py")
    call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefolder_updater_dist --workpath=./onefolder_updater_build -y -w --onedir updater/WolfStarterUpdater.py")
    
    print("Moving executables")
    if buildOneFile: move("onefile_dist/WolfStarter.exe","%s/WolfStarter.exe" % releasedir)
    if buildOneFile: move("onefile_updater_dist/WolfStarterUpdater.exe","%s/WolfStarterUpdater.exe" % releasedir)
    
    print("Copying icon")
    copyfile("WolfStarterLogo.ico","onefolder_dist/WolfStarter/WolfStarterLogo.ico")

    print("Copying extra files")
    copyfile("README.md","onefolder_dist/WolfStarter/README.md")
    copyfile("version.txt","onefolder_dist/WolfStarter/version.txt")
    makedirs("onefolder_dist/WolfStarter/updater/")
    copyfile("updater/version.txt","onefolder_dist/WolfStarter/updater/version.txt")
    
    print("Zipping directory")
    zipdir("onefolder_dist/WolfStarter","%s/ETWolfStarter-v%s.zip" % ( releasedir , version ) )
    
    print("Moving updater to wolfstarter")
    #zipdir("onefolder_updater_dist/WolfStarterUpdater","onefolder_dist/WolfStarter/updater")
    zipdir("onefolder_updater_dist/WolfStarterUpdater","%s/ETWolfStarter-v%s.zip" % ( releasedir , version ) , mode="a" , extradir="updater/" )
    
    print("Removing build data")
    if buildOneFile:
        rmtree("onefile_dist")
        rmtree("onefile_updater_dist")
        rmtree("onefile_updater_build")
        rmtree("onefile_build")
    rmtree("onefolder_dist")
    rmtree("onefolder_updater_dist")
    rmtree("onefolder_build")
    rmtree("onefolder_updater_build")
    print("Done")
def temp():
    print("Creating temp wolfstarter")
    call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefolder_updater_dist --workpath=./onefolder_updater_build -y -w --onedir updater/WolfStarterUpdater.py")
if __name__ == "__main__":
    #main()
    temp()
