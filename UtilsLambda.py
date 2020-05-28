import patoolib
import os
import shutil
from pathlib import Path
from datetime import date
import xmltodict
import patoolib #compression


class FileUtils():
    @staticmethod # Always there, without creating the object instance
    def ListFiles(folder): #remove self if made static
        print(next(os.walk(folder))[2])


def DoesNewFileExist(newFile):
    if os.path.isfile(newFile):  # If file already exists
        print("File Already Exists. " + newFile)
        return True
    else:
        return False

def NewFilePath(originalfile, SOURCEDIR, OUTPUTDIR):
    # get original filename & ext
    FName, FExt = os.path.splitext(originalfile) #path\file and .ext
    FName = Path(FName).stem #Removes path, leaving extensionless filename

    # if source file in SOURCEDIR root, or doesn't come from any SOURCEDIR subdirs:
    if os.path.dirname(originalfile) == SOURCEDIR or os.path.dirname(originalfile) not in SOURCEDIR:

        # build new path & filename for OUTPUTDIR root file
        newFile = str(os.path.join(OUTPUTDIR, FName)) + '.pptx'
    else:
        # build path and filename for OUTPUTDIR subdirs
        newFile = os.path.dirname(originalfile) #gets the folder&path the file is in
        newFile = os.path.relpath(originalfile, SOURCEDIR)  # get relative path to source
        newFile = str(os.path.join(OUTPUTDIR, newFile, FName)) + '.pptx'  # build new path & filename
    return newFile

def get_size(FolderSource):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(FolderSource):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

    # print(get_size(), 'bytes')
    # print((get_size() // (1024 * 1024)), 'MegaBytes')
    # print((get_size() // (1024 * 1024 * 1024)), 'GigaBytes')  # Little bit off

    # Space on destination drive
    total, used, free = shutil.disk_usage(OutputDir)
    # print(free // (1024 * 1024 * 1024), "GBs free")

def DecompressToTemp(file, TEMPDIR):
    try:
        patoolib.extract_archive(archive=os.path.join(file), verbosity=0, outdir=TEMPDIR)
    except Exception as e:
        print('Decompression failed. Exception Thrown: ' + str(e))
        return False
    else:
        return True

#Function to test Comic
def CheckArchive(archive_path):
    """Check that a given archive is actually ok for reading.
    Args:
        archive_path (str): Archive to check
    Returns:
        True if archive is successfully read, False otherwise.
    """
    try:
        patoolib.test_archive(archive_path, verbosity=-1)
    except Exception as e:
        print('Exception Thrown: ' + str(e))
        return False
    else:
        return True

# Function to check image is not in SHITLIST
def InSHITLIST():
    pass

def FindNewFilename(Destination, Filename):
    i = 0
    FName, FExt = os.path.splitext(Filename)  # Split filename and ext
    while os.path.exists(os.path.join(Destination, FName + str(i) + FExt)):
        i += 1
    NewFileName = FName + str(i) + FExt
    return NewFileName

#Check if Output & Source are absolute paths
# if os.path.isabs(OUTPUTDIR) is False or os.path.isabs(SOURCEDIR) is False:
#     print("CHANGE THE SOURCE OR OUTPUT")
#     exit()

#check if directory exists
# if os.path.exists(OUTPUTDIR) is False:  # If default folder doesn't exist
#     os.makedirs(OUTPUTDIR)

#Check size of source folder

#Load XML
def XmlReader(comicinfo):
    try:
        fd = open(comicinfo)
        doc = xmltodict.parse(fd.read())
    except (Exception, UnicodeDecodeError):
        fd = open(comicinfo, encoding = "utf8")
        doc = xmltodict.parse(fd.read())
        print("Using UTF8 for encoding")

    #remove crap
    XmlDelete = []
    for key in doc['ComicInfo']:
        if key[0] == "@":
            #print(XmlDict[key])
            XmlDelete.append(key) # makes a list of keys to delete#######################
        if isinstance(doc['ComicInfo'][key], str) is False:
            XmlDelete.append(key)
    for key in XmlDelete:
        del doc['ComicInfo'][key] # deletes keys


    return doc['ComicInfo']




def IsComic(Filename, COMICEXT): #is file a comic
    #global COMICEXT
    FName, FExt = os.path.splitext(Filename)  # Split filename and ext
    if FExt in COMICEXT:
        print('Is Comic: ' + Filename)
        return True
    else:
        print('Is Not Comic: ' + Filename)
        return False

def Logger(String, OUTPUTDIR):
    today = date.today()
    LoggerFile = open((os.path.join(OUTPUTDIR, 'log.txt')), 'a')
    LoggerFile.write(String + " " + str(today.strftime("%d %B %Y")) + "\n")
    LoggerFile.close()
def Examiner(String, OUTPUTDIR):
    today = date.today()
    LoggerFile = open((os.path.join(OUTPUTDIR, 'examiner.txt')), 'a')
    LoggerFile.write(String + " " + str(today.strftime("%d %B %Y")) + "\n")
    LoggerFile.close()


def MoveFolders(Source, Destination):
    for entry in os.scandir(Source):
        shutil.move(entry.path, Destination)

#Counts XML files in TEMPDIR, logs it
def XmlCheck(TEMPDIR, Filename, OUTPUTDIR):
    XmlCheck = []
    for file in os.listdir(TEMPDIR):
        if file.endswith(".xml"):
            XmlCheck.append(file)
    if len(XmlCheck) > 1: #If there is more than one Xml file
        Examiner('More than one Xml in ' + Filename, OUTPUTDIR)#Store XmlCheck list and current directory structure
    #Remove crap

#If TEMPDIR has no files but 1 folder, bring everything from folder to TEMPDIR
def EmptyFolderDrop(TEMPDIR):
    files = next(os.walk(TEMPDIR))[2] #Files in TEMPDIR, not subfolders.
    if len(files) < 1: #if there are no files
        folders = next(os.walk(TEMPDIR))[1] #How many folders?
        if len(folders) == 1: #If there is one folder
            MoveFolders(os.path.join(TEMPDIR, folders[0]), TEMPDIR) #Move everything in this folder to TEMPDIR

def CleanFolder(TEMPDIR, ComicFileName, ALLOWEDEXT, OUTPUTDIR):
    #
    # if not type(TEMPDIR) is str:
    #     print('TEMPDIR ' + type(TEMPDIR) + ' not string')
    # if not type(ComicFileName) is str:
    #     print('ComicFileName ' + type(ComicFileName) + ' not string')
    # if not isinstance(SHITLIST, list):
    #     print('SHITLIST ' + type(SHITLIST) + ' not list')
    # if not isinstance(EXAMINERLIST, list):
    #     print('EXAMINERLIST ' + type(EXAMINERLIST) + ' not list')
    # if not isinstance(ALLOWEDEXT, list):
    #     print('ALLOWEDEXT ' + type(ALLOWEDEXT) + ' not list')
    # if not type(OUTPUTDIR) is str:
    #     print('OUTPUTDIR ' + type(OUTPUTDIR) + ' not string')


    #First checks first folder has something in it
    #Move all files in folders to TEMPDIR
    #Make sure files have different names
    #New Filename means they're last in the order of everything
    #Other filetypes get added to a text file and deleted
    #Leaves empty folders for deletion later

    EmptyFolderDrop(TEMPDIR)

    for Foldername, Subfolders, Filenames in os.walk(TEMPDIR):
        #print('Current folder:' + Foldername)
        for Filename in Filenames:

            if Filename in SHITLIST:
                os.unlink(os.path.join(Foldername, Filename)) #delete file
                continue

            FName, FExt = os.path.splitext(Filename)  # Split filename and ext
            if FExt in EXAMINERLIST:
                Examiner('Comic: ' + ComicFileName, Filename) # Any bonus extras found get logged

            if FExt not in ALLOWEDEXT:
                Logger(ComicFileName + " Deleting file because wrong extension: " + os.path.join(Foldername, Filename), OUTPUTDIR)
                print('Deleting: ' + os.path.join(Foldername, Filename))
                os.unlink(os.path.join(Foldername, Filename))  # deleting file because wrong extension
            elif Foldername != TEMPDIR: # For subfolders of TEMPDIR
                # New Filename:
                NewFileName = """{Extra} """ + Filename  # Adding { } so that its the end of Alphanumeric & symbol order

                #print(Foldername + ' not in TEMPDIR')

                if os.path.isfile(os.path.join(TEMPDIR, NewFileName)):  # if file exists
                    #print(NewFileName)
                    NewFileName = FindNewFilename(TEMPDIR, NewFileName)  # Function to find new file name
                    # print(ComicFileName)
                    # print(Filename)
                    # print(NewFileName)
                    Logger(ComicFileName + ' Old filename: ' + Filename + " New FileName: " + NewFileName,
                           OUTPUTDIR)
                    shutil.move(os.path.join(Foldername, Filename),
                                (os.path.join(TEMPDIR, NewFileName)))  # move to TEMPDIR
                else:

                    # print(Foldername)
                    # print(Filename)
                    # print(TEMPDIR)
                    # print(NewFileName)
                    shutil.move(os.path.join(Foldername, Filename),
                                (os.path.join(TEMPDIR, NewFileName)))  # move to TEMPDIR

    FilesInComic = os.listdir(TEMPDIR)
    #Counts how many Xml files
    XmlCheck(TEMPDIR, Filename, OUTPUTDIR)


