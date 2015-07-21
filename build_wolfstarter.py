from subprocess import call
from shutil import move,rmtree,copyfile
from os import makedirs,walk,getcwd,chdir
from os.path import isdir,exists,join,abspath
from zipfile import ZipFile,ZIP_DEFLATED
from zelly.constants import WOLFSTARTER_VERSION

buildOneFile=False
buildUpdater=False
# TODO Write Version text on buil;d


def zipdir(path,zippath,mode="w",extradir=None):
    zippath = abspath(zippath)
    cwd     = getcwd()
    chdir(path)
    zipH = ZipFile(zippath,mode,compression=ZIP_DEFLATED)
    for root , _ , files in walk('.'):
        for file in files:
            print("Zipping %s" % join(root,file))
            if extradir:
                zipH.write(join(root,file),arcname=extradir+join(root,file))
            else:
                zipH.write(join(root,file))
    zipH.close()
    chdir(cwd)

def rmtree_z(dirpath):
    if not dirpath or not isdir(dirpath): return
    print("Removing directory tree %s" % dirpath)
    rmtree(dirpath)
    
def copyfile_z(filename,filepath):
    print("Moving %s to %s" % (filename,filepath))
    copyfile(filename,filepath)
    
def main():
    version = input("What version tag are you using? (Hit enter to use %s)" % WOLFSTARTER_VERSION)
    if not version: version = WOLFSTARTER_VERSION.replace('v','')
    input("Is v%s correct? (If not then do Ctrl+C)" % version)
    
    releasedir="releases/ETWolfStarter-v%s" % version
    if isdir(releasedir): input("That version folder already exists, do you wish to overwrite? (Ctrl+C to cancel)")
    if not exists(releasedir) or not isdir(releasedir):
        print("Creating release directory")
        makedirs(releasedir)
    
    print("Building WolfStarter...")
    if buildOneFile:
        print("Building Wolfstarter[One File]")
        call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefile_dist --workpath=./onefile_build -y -w --onefile WolfStarter.py")
        print("Moving WolfStarter.exe[One File]")
        move("onefile_dist/WolfStarter.exe","%s/WolfStarter.exe" % releasedir)
        print("Completed WolfStarter[One File]")
    print("Building WolfStarter[Folder]")
    call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefolder_dist --workpath=./onefolder_build -y -w --onedir WolfStarter.py")
    print("Completed WolfStarter[Folder]")
    
    if buildUpdater:
        print("Building WolfStarterUpdater")
        if buildOneFile:
            print("Building WolfStarterUpdater[One File]")
            call("pyinstaller --uac-admin --icon=WolfStarterLogo.ico --distpath=./onefile_updater_dist --workpath=./onefile_updater_build -y -w --onefile WolfStarterUpdater.py")
            print("Moving WolfStarterUpdater.exe[One File]")
            move("onefile_updater_dist/WolfStarterUpdater.exe","%s/WolfStarterUpdater.exe" % releasedir)
            print("Completed WolfStarterUpdater[One File]")
        print("Building WolfStarterUpdater[Folder]")
        call("pyinstaller --icon=WolfStarterLogo.ico --distpath=./onefolder_updater_dist --workpath=./onefolder_updater_build -y -w --onedir WolfStarterUpdater.py")
        print("Making updater folder in WolfStarter")
        makedirs("onefolder_dist/WolfStarter/updater/")
        copyfile_z("updater/version.txt","onefolder_dist/WolfStarter/updater/version.txt")
        print("Completed WolfStarterUpdater[Folder]")
    
    print("Copying extra files")
    copyfile_z("WolfStarterLogo.ico","onefolder_dist/WolfStarter/WolfStarterLogo.ico")
    copyfile_z("README.md","onefolder_dist/WolfStarter/README.md")
    copyfile_z("version.txt","onefolder_dist/WolfStarter/version.txt")
    
    print("Zipping WolfStarter")
    zipdir("onefolder_dist/WolfStarter","%s/ETWolfStarter-v%s.zip" % ( releasedir , version ) )
    print("Completed Zipping wolfstarter")
    
    if buildUpdater:
        print("Zipping Updater")
        #move("onefolder_updater_dist/WolfStarterUpdater","onefolder_dist/WolfStarter/updater")
        zipdir("onefolder_updater_dist/WolfStarterUpdater","%s/ETWolfStarter-v%s.zip" % ( releasedir , version ) , mode="a" , extradir="updater/" )
        print("Completed Zipping Updater")
    
    print("Removing build data")
    
    rmtree_z("onefile_dist")
    rmtree_z("onefile_build")
    rmtree_z("onefolder_dist")
    rmtree_z("onefolder_build")
    rmtree_z("onefolder_updater_dist")
    rmtree_z("onefolder_updater_build")
    rmtree_z("onefile_updater_dist")
    rmtree_z("onefile_updater_build")
    
    print("Build Complete")
def temp():
    print("Creating temp wolfstarter")
    call("pyinstaller --manifest=WolfStarterUpdater.exe.manifest --icon=WolfStarterLogo.ico --distpath=./onefolder_updater_dist --workpath=./onefolder_updater_build -y -w --onedir WolfStarterUpdater.py")
if __name__ == "__main__":
    main()
    #temp()
