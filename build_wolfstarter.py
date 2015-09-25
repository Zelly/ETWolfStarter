from subprocess import call
from shutil import move, rmtree, copyfile
from os import makedirs, walk, getcwd, chdir
from os.path import isdir, exists, join, abspath
from zipfile import ZipFile, ZIP_DEFLATED
from zelly.constants import WOLFSTARTER_VERSION

buildOneFile = False


# TODO Write Version text on build


def zipdir(path, zip_path, mode="w", extradir=None):
    zip_path = abspath(zip_path)
    cwd = getcwd()
    chdir(path)
    zip_handle = ZipFile(zip_path, mode, compression=ZIP_DEFLATED)
    for root, _, files in walk('.'):
        for file in files:
            print("Zipping %s" % join(root, file))
            if extradir:
                zip_handle.write(join(root, file), arcname=extradir + join(root, file))
            else:
                zip_handle.write(join(root, file))
    zip_handle.close()
    chdir(cwd)


def _rmtree(dir_path):
    if not dir_path or not isdir(dir_path):
        return
    print("Removing directory tree %s" % dir_path)
    rmtree(dir_path)


def _copyfile(filename, filepath):
    print("Moving %s to %s" % (filename, filepath))
    copyfile(filename, filepath)


def main():
    version = input("What version tag are you using? (Hit enter to use %s)" % WOLFSTARTER_VERSION)
    if not version:
        version = WOLFSTARTER_VERSION.replace('v', '')
    input("Is v%s correct? (If not then do Ctrl+C)" % version)

    release_dir = "releases/ETWolfStarter-v%s" % version
    build_command = "pyinstaller --icon=WolfStarterLogo.ico %s -y -w WolfStarter.py"

    if isdir(release_dir):
        input("That version folder already exists, do you wish to overwrite? (Ctrl+C to cancel)")
    if not exists(release_dir) or not isdir(release_dir):
        print("Creating release directory")
        makedirs(release_dir)

    print("Building WolfStarter...")
    if buildOneFile:
        print("Building Wolfstarter[One File]")
        call(build_command % "--distpath=./onefile_dist --workpath=./onefile_build --onefile")
        print("Moving WolfStarter.exe[One File]")
        move("onefile_dist/WolfStarter.exe", "%s/WolfStarter.exe" % release_dir)
        print("Completed WolfStarter[One File]")

    print("Building WolfStarter[Folder]")
    call(build_command % "--distpath=./onefolder_dist --workpath=./onefolder_build --onedir")
    print("Completed WolfStarter[Folder]")

    print("Copying extra files")
    _copyfile("WolfStarterLogo.ico", "onefolder_dist/WolfStarter/WolfStarterLogo.ico")
    _copyfile("README.md", "onefolder_dist/WolfStarter/README.md")
    _copyfile("version.txt", "onefolder_dist/WolfStarter/version.txt")

    print("Zipping WolfStarter")
    zipdir("onefolder_dist/WolfStarter", "%s/ETWolfStarter-v%s.zip" % (release_dir, version))
    print("Completed Zipping wolfstarter")

    print("Removing build data")

    _rmtree("onefile_dist")
    _rmtree("onefile_build")
    _rmtree("onefolder_dist")
    _rmtree("onefolder_build")
    _rmtree("onefolder_updater_dist")
    _rmtree("onefolder_updater_build")
    _rmtree("onefile_updater_dist")
    _rmtree("onefile_updater_build")

    print("Build Complete")


def temp():
    print("Creating temp wolfstarter")
    call(
        "pyinstaller --manifest=WolfStarterUpdater.exe.manifest --icon=WolfStarterLogo.ico " +
        "--distpath=./onefolder_updater_dist --workpath=./onefolder_updater_build -y -w " +
        "--onedir WolfStarterUpdater.py")


if __name__ == "__main__":
    main()
    # temp()
