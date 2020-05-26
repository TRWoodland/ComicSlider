#require libraries pip install rarfile xmltodict patool, Pillow
import os
import shutil
import time
import argparse #allows input by commandline
import tempfile
from sys import platform
import shutil
from Utils import CheckArchive, DecompressToTemp, get_size, IsComic, CleanFolder, \
    Logger, Examiner, MoveFolders, XmlReader
from ImagesPPTX import RotateToPortrait, ConvertToJpg, GetImageDimensionsInches, \
    MakePresentation, AddSlide, FirstImageDimensions, AddXmlSlide, SavePPTX

#AWS Test
if platform == "linux": #if platform is linux
    if os.path.exists("/tmp"): #if /tmp exists
        TEMPDIR = ()
        amazon = True

SHITLIST = ['zThe-Hand.jpg']
IMAGEEXT = ['.jpg','.jpeg', 'gif', 'png', 'bmp', 'tiff']
OTHEREXT = ['.xml', 'txt', 'text']
COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
ALLOWEDEXT = IMAGEEXT + OTHEREXT
EXAMINERLIST = ['.mp4', '.mpg', '.avi', '.mov', '.flv', '.mpeg', '.mp3', '.mpa', '.doc', '.docx'
                '.wav', '.flac', '.ogg', '.zip', '.rar', '.cbr', '.cbz', '7z', '.pdf']

#INPUT Output Directory
if amazon == False:
    OUTPUTDIR = 'F:\Google Drive\Synced\PythonProjects\ComicSlider\ProcessedComics'
    SOURCEDIR = 'F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics'
else:
    if not os.path.exists(os.path.join(tempfile.gettempdir(), 'SOURCEDIR')):  # if folder doesn't exist
        os.mkdir(os.path.join(tempfile.gettempdir(), 'SOURCEDIR'))  # make it
    SOURCEDIR = os.path.join(tempfile.gettempdir(), 'SOURCEDIR')

    if not os.path.exists(os.path.join(tempfile.gettempdir(), 'OUTPUTDIR')):  # if folder doesn't exist
        os.mkdir(os.path.join(tempfile.gettempdir(), 'OUTPUTDIR'))  # make it
    OUTPUTDIR = os.path.join(tempfile.gettempdir(), 'OUTPUTDIR')


#Generate TEMPDIR. FOLDER IS EMPTIED WHEN PROCESS COMPLETED!
if not os.path.exists(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')): #if folder doesn't exist
    os.mkdir(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')) #make it
TEMPDIR = os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')

print("Files will temporarily stored in: " + TEMPDIR) # prints the current temporary directory

parser = argparse.ArgumentParser(description='Comic Slider parser')
parser.add_argument('--filename', help='the file name')
parser.add_argument('--foldername', help='the foldername')
args = parser.parse_args()
print(args.foldername)
#Input validation
if args.filename==None and args.foldername==None: #if that particualar arg not given, do this
    print("no arg given")#
    exit()

if args.filename: #arg given, do this
    print("Filename given: " + args.filename)
    if not os.path.isfile(args.filename):
        print("File doesn't exist")
        exit()
    if not os.path.isabs(args.filename): #If file doesn't have a complete path
        print("File doesn't have a complete path: "  + args.filename)
    else:
        print("File Found: " + args.filename)

if args.foldername: #arg given, do this
    print("Foldername given: " + args.foldername)
    if not os.path.exists(args.foldername):
        print("Folder doesn't exist")
        exit()
    else:
        print("Folder Found: " + args.foldername)

#EmptyTempDir
def EmptyTempDir(TEMPDIR):
    if os.path.exists(TEMPDIR): #makes sure Temp is empty
        shutil.rmtree(TEMPDIR)
        time.sleep(2)
        try:
            os.mkdir(TEMPDIR)
        except PermissionError:
            print('Too quick to remake folder')
            exit()
# Remake Folder Structure in SOURCEDIR to OUTPUTDIR
def RemakeFolderStructure(SOURCEDIR, OUTPUTDIR):
    for Foldername, Subfolders, Filenames in os.walk(SOURCEDIR):
         NewFolder(Foldername, SOURCEDIR, OUTPUTDIR)

def NewFolder(Foldername, SOURCEDIR, OUTPUTDIR):
    if os.path.exists(os.path.join(OUTPUTDIR, os.path.relpath(Foldername, SOURCEDIR))): #Does Current Folder exist in new location
        print(Foldername + 'Folder Exists in OUTPUTDIR!')
    else:
        os.mkdir(os.path.join(OUTPUTDIR, os.path.relpath(Foldername, SOURCEDIR))) #Create folder
        print(Foldername + ' created in OUTPUTDIR!')

#Ensure .jpgs & rotate landscapes
def ProcessImages(TEMPDIR):
    for file in next(os.walk(TEMPDIR))[2]: #files in TEMPDIR
        FName, FExt = os.path.splitext(file)
        if FExt in IMAGEEXT: #if file is image
            if not FExt.lower() == '.jpg': #if file is not jpg
                ConvertToJpg(TEMPDIR, file)

            #Check orientation
            RotateToPortrait(os.path.join(TEMPDIR, file))
            #allPageDimensions.update(GetImageDimensionsInches(os.path.join(TEMPDIR, file))) #should add new k&v to dict
            #width, height = GetImageDimensionsInches((os.path.join(TEMPDIR, file)))
            # if width > maxwidth:
            #     maxwidth = width
            # if height > maxheight:
            #     maxheight = height
    #print("maxheight " + str(maxheight) + "maxwidth " + str(maxwidth))
    return True

#FILE
def ConvertComic(file, COMICEXT):
    if IsComic(file, COMICEXT) == False: #If its a comic
        return False

    else:
        print("Is Comic Archive")
        # Check archive
        if not CheckArchive(file):
            print('CorruptArchive')
            Examiner(os.path.join(Foldername, file) + ' is CORRUPT', OUTPUTDIR)
            return False
            #exit()
        else:
            print('Good archive')

    EmptyTempDir(TEMPDIR)

    if not DecompressToTemp(file, TEMPDIR):
        print('Failed to decompress: ' + file)
        exit()
    else:
        print('Good decompress')
    #Trasnverse tempfolder, move files, remove subfolders
    CleanFolder(TEMPDIR, file, SHITLIST, EXAMINERLIST, ALLOWEDEXT, OUTPUTDIR)
    if not ProcessImages(TEMPDIR): #Check dimensions, portrait # returns W&H
        print('Process Images Failed')
        exit()

    #Get dimensions of first image
    width, height = FirstImageDimensions(TEMPDIR) #in inches

    prs = MakePresentation(width, height)

    #Check XML exists
    XmlDict = {}
    if os.path.isfile(os.path.join(TEMPDIR, 'ComicInfo.xml')): #If ComicInfo exists
        XmlDict = XmlReader(os.path.join(TEMPDIR, 'ComicInfo.xml'))

    #Seperate Summary
    SummaryDict = {}
    if 'Summary' in XmlDict:
        SummaryDict['Summary'] = XmlDict['Summary']
        del XmlDict['Summary']

    # Make list of filenames
    pageList = []
    for page in next(os.walk(TEMPDIR))[2]:
        FName, FExt = os.path.splitext(page)
        if FExt == '.jpg':
            pageList.append(page)

    # BUILD COMIC
    for page in pageList: #iterate through the pages
        prs = AddSlide(prs, (os.path.join(TEMPDIR, page))) #make page

        if page == pageList[0]: # if current page is the cover
            if len(XmlDict) > 1: # if something in XmlDict
                prs = AddXmlSlide(prs, XmlDict)  # Create Main Metadata page
            if 'Summary' in SummaryDict: #If Summary dict exists
                prs = AddXmlSlide(prs, SummaryDict)  # Create Summary page

    # for page in next(os.walk(TEMPDIR))[2]:
    #     FName, FExt = os.path.splitext(page)
    #     if FExt == '.jpg':
    #         prs = AddSlide(prs, (os.path.join(TEMPDIR, page)))
    return prs

#FOLDER
if args.foldername:
    RemakeFolderStructure(SOURCEDIR, OUTPUTDIR)
    for Foldername, Sfolders, Filenames in os.walk(SOURCEDIR):
        for file in Filenames:
            prs = ConvertComic(file, COMICEXT)
            SavePPTX(prs, file, SOURCEDIR, OUTPUTDIR)

if args.filename:
    print(args.filename, COMICEXT)
    prs = ConvertComic(args.filename, COMICEXT)
    newFile = SavePPTX(prs, args.filename, SOURCEDIR, OUTPUTDIR)

#Empty TEMPDIR of all Files and Folders
for Foldername, Subfolders, Filenames in os.walk(TEMPDIR):
    for file in Filenames:
        os.unlink(os.path.join(Foldername, file))
    for folder in Subfolders:
        shutil.rmtree(os.path.join(Foldername, folder))

