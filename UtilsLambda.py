import patoolib
import os
import shutil
from pathlib import Path
from datetime import date
import xmltodict
import patoolib #compression
import boto3


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
    FName, FExt = os.path.splitext(Filename.lower())  # Split filename and ext
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



def MoveFolders(Source, Destination):
    for entry in os.scandir(Source):
        shutil.move(entry.path, Destination)



#If TEMPDIR has no files but 1 folder, bring everything from folder to TEMPDIR
def EmptyFolderDrop(TEMPDIR):
    files = next(os.walk(TEMPDIR))[2] #Files in TEMPDIR, not subfolders.
    if len(files) < 1: #if there are no files
        folders = next(os.walk(TEMPDIR))[1] #How many folders?
        if len(folders) == 1: #If there is one folder
            MoveFolders(os.path.join(TEMPDIR, folders[0]), TEMPDIR) #Move everything in this folder to TEMPDIR

def CleanFolder(TEMPDIR, ComicFileName, ALLOWEDEXT, OUTPUTDIR):
    EmptyFolderDrop(TEMPDIR)

    for Foldername, Subfolders, Filenames in os.walk(TEMPDIR):
        #print('Current folder:' + Foldername)
        for Filename in Filenames:
            FName, FExt = os.path.splitext(Filename)  # Split filename and ext
            if FExt not in ALLOWEDEXT:
                os.unlink(os.path.join(Foldername, Filename))  # deleting file because wrong extension

            elif Foldername != TEMPDIR: # For subfolders of TEMPDIR
                # New Filename:

                NewFileName = """{Extra} """ + Filename  # Adding { } so that its the end of Alphanumeric & symbol order

                if os.path.isfile(os.path.join(TEMPDIR, NewFileName)):  # if file exists
                    NewFileName = FindNewFilename(TEMPDIR, NewFileName)  # Function to find new file name

                    shutil.move(os.path.join(Foldername, Filename),
                                (os.path.join(TEMPDIR, NewFileName)))  # move to TEMPDIR
                else:

                    shutil.move(os.path.join(Foldername, Filename),
                                (os.path.join(TEMPDIR, NewFileName)))  # move to TEMPDIR

#Generate URL to Bucket file
def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    # The response contains the presigned URL
    return response


