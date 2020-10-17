import time  # for sleep
import os
import shutil
import tempfile
import patoolib
import xmltodict
from datetime import date
from pathlib import Path

class CS_Utils:
    def __init__(self, SUBMITTED_FILE="", SOURCEDIR="", OUTPUTDIR="", AWS=False):
        # things to initialize
        self.SUBMITTED_FILE = SUBMITTED_FILE
        self.SOURCEDIR = SOURCEDIR
        self.OUTPUTDIR = OUTPUTDIR
        self.AWS = AWS

        self.OTHEREXT = ['.xml', 'txt', 'text']
        self.IMAGEEXT = ['.jpg', '.jpeg', 'gif', 'png', 'bmp', 'tiff']
        self.ALLOWEDEXT = self.IMAGEEXT + self.OTHEREXT

        self.COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
        self.EXAMINERLIST = ['.mp4', '.mpg', '.avi', '.mov', '.flv', '.mpeg', '.mp3', '.mpa', '.doc', '.docx', '.wav',
                        '.flac', '.ogg', '.zip', '.rar', '.cbr', '.cbz', '7z', '.pdf']


        if os.environ.get("AWS_EXECUTION_ENV") is None:  # test whether on AWS Lambda
            self.AWS = False
            print("Not running on AWS Lambda")
        else:
            self.AWS = True
            print("on aws. Script not configured for AWS yet")
            exit()

        # Generate TEMPDIR. FOLDER IS EMPTIED WHEN PROCESS COMPLETED!
        if not os.path.exists(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')):  # if folder doesn't exist
            os.mkdir(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp'))  # make it
        self.TEMPDIR = os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')
        print("Files will temporarily stored in: " + self.TEMPDIR)  # prints the temp directory

        # Input File
        if not os.path.isfile(self.SUBMITTED_FILE):  # if file doesn't exist
            print("No file selected")
            self.SUBMITTED_FILE = None
        else:
            print("File found: " + self.SUBMITTED_FILE)

        # INPUT Directory
        if not os.path.exists(self.SOURCEDIR):  # if folder doesn't exist
            print("Source folder does not exist")
            self.SOURCEDIR = None
        else:
            print("Folder found: " + self.SOURCEDIR)

        if self.SOURCEDIR == None and self.SUBMITTED_FILE == None:
            print("No valid file or directory selected")
            exit()

        # Output
        if not os.path.exists(self.OUTPUTDIR):  # if folder doesn't exist
            print("Create directory?" + str(self.OUTPUTDIR))
            userentry = input()
            if userentry.lower() == "n":
                exit()
            if not os.path.exists(self.OUTPUTDIR):
                print("Failed to create OUTPUTDIR" + str(self.OUTPUTDIR))
                exit()
            print("Found OUTPUTDIR: " + str(self.OUTPUTDIR))


        def empty_temp(self):
            if os.path.exists(self.TEMPDIR):  # makes sure Temp is empty
                shutil.rmtree(self.TEMPDIR)
                print(str(self.TEMPDIR) + " Deleted")
                time.sleep(2)
                try:
                    os.mkdir(self.TEMPDIR)
                    print(str(self.TEMPDIR) + " Remade")
                except PermissionError:
                    print('Too quick to remake folder')
                    exit()
        empty_temp(self)
        """ END OF INIT """

    def is_comic(self, file):  # is file a comic
        if file[-4:].lower() in self.COMICEXT:
            print('Is Comic: ' + file)
            return True
        else:
            print('Is Not Comic: ' + file)
            return False

    def get_size(self, folder_source):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_source):
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
        # total, used, free = shutil.disk_usage(OutputDir)
        # print(free // (1024 * 1024 * 1024), "GBs free")

    def check_archive(self, archive_path):
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

    def decompress_to_temp(self, file):
        try:
            patoolib.extract_archive(archive=os.path.join(file), verbosity=0, outdir=self.TEMPDIR)
        except Exception as e:
            print('Decompression failed. Exception Thrown: ' + str(e))
            return False
        else:
            return True

    def find_new_filename(self, destination, filename):
        if os.path.exists(os.path.join(destination, filename)):
            print(filename + " already exists. Attempting to find new filename")
            ext = filename[-3:]  # extension minus filename
            filename = filename[:-4]   # filename minus .ext
            i = 0
            while os.path.exists(os.path.join(destination, filename + str(i) + "." + ext)):
                i += 1
            filename = filename + str(i) + "." + ext
            print("New filename found:" + filename)
        return filename

    def xmlreader(self, comicinfo):
        try:
            fd = open(comicinfo)
            doc = xmltodict.parse(fd.read())
        except (Exception, UnicodeDecodeError):
            fd = open(comicinfo, encoding="utf8")
            doc = xmltodict.parse(fd.read())
            print("Using UTF8 for encoding")

        # remove crap
        XmlDelete = []
        for key in doc['ComicInfo']:
            if key[0] == "@":
                # print(XmlDict[key])
                XmlDelete.append(key)  # makes a list of keys to delete
            if isinstance(doc['ComicInfo'][key], str) is False:
                XmlDelete.append(key)
        for key in XmlDelete:
            del doc['ComicInfo'][key]  # deletes keys
        return doc['ComicInfo']

    def new_file_path(self, file):
        # get original filename & ext
        filename, ext = os.path.splitext(file)  # path\file and .ext
        filename = Path(filename).stem  # Removes path, leaving extensionless filename
        new_file = ""

        # if source file in SOURCEDIR root, or doesn't come from any SOURCEDIR subdirs:
        if os.path.dirname(file) == self.SOURCEDIR or \
                os.path.dirname(file) not in self.SOURCEDIR:

            # build new path & filename for OUTPUTDIR root file
            new_file = str(os.path.join(self.OUTPUTDIR, filename)) + '.pptx'
        else:
            # build path and filename for OUTPUTDIR subdirs
            # os.path.dirname(self.SUBMITTED_FILE)  # gets the folder&path the file is in
            relative_path = os.path.relpath(os.path.dirname(file), self.SOURCEDIR)  # get relative path to source
            dir_list = relative_path.split(os.sep) # make list of folders
            new_structure = self.OUTPUTDIR
                for folder in dir_list:
                    if not os.path.exists(os.path.join(new_structure, folder)):  # if output\\folder doesn't exist
                        os.mkdir(os.path.join(new_structure, folder))            # make it
                    newstructure = os.path.join(new_structure, folder)           # update new_structure string

            new_file = str(os.path.join(new_structure, filename)) + '.pptx'  # build new path & filename
        return new_file




""" TEST AREA!!! """
bob = 1
if bob != 1:
    from OO_Utils import CS_Utils
    OUTPUTDIR = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\ProcessedComics'''
    SOURCEDIR = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics'''
    SUBMITTED_FILE = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics\Test.zip'''
    test = CS_Utils(SUBMITTED_FILE=SUBMITTED_FILE, SOURCEDIR=SOURCEDIR, OUTPUTDIR=OUTPUTDIR, AWS=False)




# Remake Folder Structure in SOURCEDIR to OUTPUTDIR
def RemakeFolderStructure(SOURCEDIR, OUTPUTDIR):
    for Foldername, Subfolders, Filenames in os.walk(SOURCEDIR):
         NewFolder(Foldername, SOURCEDIR, OUTPUTDIR)

def NewFolder(foldername, SOURCEDIR, OUTPUTDIR):
    if os.path.exists(os.path.join(OUTPUTDIR, os.path.relpath(foldername, SOURCEDIR))):  # Does Current Folder exist in new location
        print(foldername + 'Folder Exists in OUTPUTDIR!')
    else:
        os.mkdir(os.path.join(OUTPUTDIR, os.path.relpath(foldername, SOURCEDIR)))  # Create folder
        print(foldername + ' created in OUTPUTDIR!')

