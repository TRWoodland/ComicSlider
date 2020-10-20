import time  # for sleep
import os
import shutil
import tempfile
import patoolib
import xmltodict
from datetime import date
from pathlib import Path
from OO_Image import CS_Image

class CS_Utils:
    def __init__(self, SUBMITTED_FILE="", SOURCEDIR="", OUTPUTDIR="", AWS=False):
        # things to initialize
        self.SUBMITTED_FILE = SUBMITTED_FILE
        self.SOURCEDIR = SOURCEDIR
        self.OUTPUTDIR = OUTPUTDIR
        self.AWS = AWS

        # self.OTHEREXT = ['.xml', 'txt', 'text']  # if I decide to make a page of text files
        self.OTHEREXT = ['.xml']
        self.IMAGEEXT = ['.jpg', '.jpeg', '.gif', '.png', '.bmp', '.tif', '.tiff']
        self.IMAGECONV = ['.gif', '.png', '.bmp', '.tif', '.tiff']
        self.ALLOWEDEXT = self.IMAGEEXT + self.OTHEREXT
        self.SHITLIST = ['zThe-Hand.jpg']
        self.XML_FILE = None

        self.COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
        self.FAILED_LIST = ''
        self.EXAMINERLIST = ['.mp4', '.mpg', '.avi', '.mov', '.flv', '.mpeg', '.mp3', '.mpa', '.doc', '.docx', '.wav',
                             '.flac', '.ogg', '.zip', '.rar', '.cbr', '.cbz', '.7z', '.pdf']

        # Generate TEMPDIR. FOLDER IS EMPTIED WHEN PROCESS COMPLETED!
        if not os.path.exists(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')):  # if folder doesn't exist
            os.mkdir(os.path.join(tempfile.gettempdir(), 'ComicSliderTemp'))  # make it
        self.TEMPDIR = os.path.join(tempfile.gettempdir(), 'ComicSliderTemp')
        print("Files will temporarily stored in: " + self.TEMPDIR)  # prints the temp directory

        # Input File
        if self.SUBMITTED_FILE != "":
            self.SUBMITTED_FILE = os.path.abspath(self.SUBMITTED_FILE)
        if not os.path.isfile(self.SUBMITTED_FILE):  # if file doesn't exist
            print("No file selected")
            self.SUBMITTED_FILE = False
        else:
            print("File found: " + self.SUBMITTED_FILE)

        # INPUT Directory
        if self.SOURCEDIR != "":
            self.SOURCEDIR = os.path.abspath(self.SOURCEDIR)
        if not os.path.exists(self.SOURCEDIR):  # if folder doesn't exist
            print("Source folder does not exist")
            self.SOURCEDIR = False
        else:
            print("Folder found: " + self.SOURCEDIR)

        if self.SOURCEDIR is None and self.SUBMITTED_FILE is None:
            print("No valid file or directory selected")
            exit()

        # Output
        if self.SOURCEDIR != "":
            self.SOURCEDIR = os.path.abspath(self.SOURCEDIR)
        if not os.path.exists(self.OUTPUTDIR):  # if folder doesn't exist
            print("Create directory?" + str(self.OUTPUTDIR))
            userentry = input()
            if userentry.lower() == "n":
                exit()
            if not os.path.exists(self.OUTPUTDIR):
                print("Failed to create OUTPUTDIR" + str(self.OUTPUTDIR))
                self.FAILED_LIST = "Failed to create OUTPUTDIR" + str(self.OUTPUTDIR)
                return self.FAILED_LIST
            print("Found OUTPUTDIR: " + str(self.OUTPUTDIR))

        #self.start_the_process()
        """ END OF INIT """

    def empty_temp(self):
        if os.path.exists(self.TEMPDIR):  # makes sure Temp is empty
            shutil.rmtree(self.TEMPDIR)
            print("Deleting Temp Dir: " + self.TEMPDIR)
            time.sleep(2)
            try:
                os.mkdir(self.TEMPDIR)
                print("Remaking Temp Dir: " + self.TEMPDIR)
            except PermissionError:
                print('Too quick to remake folder')
                exit()

    def is_comic(self, file):  # is file a comic
        filename, ext = os.path.splitext(file)  # path\file and .ext
        filename = Path(filename).stem  # Removes path, leaving extensionless filename
        if ext.lower() in self.COMICEXT:
            print('Is Comic: ' + file)
            return True
        else:
            print('Is Not Comic: ' + file)
            return False

    def get_size(self, folder_source):
        total_size = 0
        for dirpath, dirnames, files in os.walk(folder_source):
            for file in files:
                fp = os.path.join(dirpath, file)
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

    def find_new_filename(self, destination, file):
        print("----------------------file")
        if os.path.exists(os.path.join(destination, file)):
            print(file + " already exists. Attempting to find new filename")
            filename, ext = os.path.splitext(file)  # path\file and .ext
            filename = Path(filename).stem  # Removes path, leaving extensionless filename
            i = 0
            while os.path.exists(os.path.join(destination, filename + str(i) + ext)):
                i += 1
            file = filename + str(i) + ext
            print("New filename found:" + file)
        return file

    def xml_reader(self, comicinfo):
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

        # if source file in SOURCEDIR root
        if os.path.dirname(file) == self.SOURCEDIR:
            # build new path & filename for OUTPUTDIR root file
            new_file = str(os.path.join(self.OUTPUTDIR, filename)) + '.pptx'
        else:
            # build path and filename for OUTPUTDIR subdirs
            # os.path.dirname(self.SUBMITTED_FILE)  # gets the folder&path the file is in
            relative_path = os.path.relpath(os.path.dirname(file), self.SOURCEDIR)  # get relative path to source
            dir_list = relative_path.split(os.sep) # make list of folders
            new_structure = self.OUTPUTDIR
            print("file" + file)
            print("relative_path" + relative_path)
            print("dir_list" + str(dir_list))
            print("new_structure" + new_structure)
            for folder in dir_list:
                if not os.path.exists(os.path.join(new_structure, folder)):  # if output\\folder doesn't exist
                    os.mkdir(os.path.join(new_structure, folder))            # make it
                new_structure = os.path.join(new_structure, folder)
                print(new_structure)  # update new_structure string
            new_file = str(os.path.join(new_structure, filename)) + '.pptx'  # build new path & filename
        return new_file

    # Drop everything down to TEMPDIR
    def empty_folder_drop(self):
        # move files
        for dirpath, dirname, files in os.walk(self.TEMPDIR):
            for file in files:
                newfilename = self.find_new_filename(self.TEMPDIR, file)  # checks filename is new

                print("Moving: " + (os.path.join(dirpath, file)) + "\nTo:" + os.path.join(self.TEMPDIR, newfilename))
                shutil.move(os.path.join(dirpath, file), os.path.join(self.TEMPDIR, newfilename))  # move and rename file
        # delete subdirs
        for dirname in next(os.walk(self.TEMPDIR))[1]:
            print("Deleting subdir: " + os.path.join(self.TEMPDIR, dirname))
            shutil.rmtree(os.path.join(self.TEMPDIR, dirname))

    def start_the_process(self):
        if self.SUBMITTED_FILE != False:
            prs = """FINAL RESULT"""
            # If false, not comic
            if not self.is_comic(self.SUBMITTED_FILE):
                self.FAILED_LIST = "Not Comic: " + self.SUBMITTED_FILE
                print("File does not have comic extension: " + self.SUBMITTED_FILE)
                return False
            else:
                print("Has comic extension. Testing archive for corruption")
                if not self.check_archive(self.SUBMITTED_FILE):
                    print('CorruptArchive: ' + self.SUBMITTED_FILE)
                    self.FAILED_LIST = 'CorruptArchive: ' + self.SUBMITTED_FILE
                    return False
                else:
                    print("Archive tested successfully")

            # Clear Temp Folder
            self.empty_temp()

            # Decompress file to temp
            if not self.decompress_to_temp(self.SUBMITTED_FILE):
                self.FAILED_LIST = "Failed to decompress: " + self.SUBMITTED_FILE
                print('Failed to decompress: ' + self.SUBMITTED_FILE)
                return self.FAILED_LIST
            else:
                print('Good decompress')

            # Move all files to root folder, remove subdirs.
            self.empty_folder_drop()

            """ ComicInfo.xml & Remove unwanted files """

            files = next(os.walk(self.TEMPDIR))[2]

            if "ComicInfo.xml" in files:
                print("ComicInfo.xml found")
                self.XML_FILE = os.path.join(self.TEMPDIR, "ComicInfo.xml")

            """ FILE STUFF """

            for file in files:
                filename, ext = os.path.splitext(file)  # path\file and .ext
                filename = Path(filename).stem  # Removes path, leaving extensionless filename

                if file in self.SHITLIST:
                    os.unlink(os.path.join(self.TEMPDIR, file))

                if ext not in self.ALLOWEDEXT:
                    print("Deleting file because wrong extension: " + file)
                    os.unlink(os.path.join(self.TEMPDIR, file))

                if ext == '.jpeg':
                    newfilename = self.find_new_filename(self.TEMPDIR, filename + '.jpg')
                    print("Renaming jpeg tp jpg: " + file + " to " + newfilename)
                    os.rename(os.path.join(self.TEMPDIR, file), os.path.join(self.TEMPDIR, newfilename))

                """ XML STUFF """
                if self.XML_FILE is None:                           # if no xml file is yet found
                    if ext == ".xml":                               # if an ext is xml
                        print("Attempting to load XML metadata from: " + file)
                        self.XML_FILE = os.path.join(self.TEMPDIR, file)

                if self.XML_FILE is not None:                       # if an XML file was found
                    xml_dict = self.xml_reader(self.XML_FILE)       # extract the metadata
                    summary_dict = {}                               # Separate the Summary
                    if 'Summary' in xml_dict:
                        summary_dict['Summary'] = xml_dict['Summary']
                        del xml_dict['Summary']

            """ IMAGE CONVERSION """
            files = next(os.walk(self.TEMPDIR))[2]  # update files list
            csimage = CS_Image(TEMPDIR=self.TEMPDIR)  # image tools

            for file in files:
                filename, ext = os.path.splitext(file)  # path\file and .ext
                filename = Path(filename).stem  # Removes path, leaving extensionless filename

                if ext.lower() in self.IMAGECONV:                       # if its an image to convert and its not a jpg
                    if filename + '.jpg' in files:                              # if the converted filename exists
                        newfilename = self.find_new_filename(self.TEMPDIR, filename + '.jpg')   # generate new fn
                        csimage.convert_to_jpg(os.path.join(self.TEMPDIR, file),
                                               os.path.join(self.TEMPDIR, newfilename))     # input, output
                        os.unlink(os.path.join(self.TEMPDIR, file))                                       # delete original
                    else:
                        csimage.convert_to_jpg(os.path.join(self.TEMPDIR, file), filename + '.jpg')  # input, output

            """ ROTATE, WIDTH, HEIGHT, COUNT"""

            files = next(os.walk(self.TEMPDIR))[2]  # update files list
            page_list = []
            current_width, current_height, width, height = 0, 0, 0, 0

            for file in files:
                filename, ext = os.path.splitext(file)  # path\file and .ext
                filename = Path(filename).stem  # Removes path, leaving extensionless filename

                if ext.lower() == '.jpg':
                    csimage.rotate_to_portrait(os.path.join(self.TEMPDIR, file))
                    page_list.append(os.path.join(self.TEMPDIR, file))

                    current_width, current_height = csimage.get_image_dimensions_inches(os.path.join(self.TEMPDIR, file))
                    if current_width > width:
                        width = current_width
                    if current_height > height:
                        height = current_height

            print("No of Pages: " + str(len(page_list)) +
                  "\nExtra files found: " + str((len(files) - len(page_list))))
            if self.XML_FILE is not None:
                print("XML info found in: " + str(self.XML_FILE))
            else:
                print("No XML info found")

            """ BUILD PPTX """
            # TODO: Bigger font on bigger inches
            prs = csimage.make_presentation(width, height)
            for page in page_list:
                prs = csimage.add_slide(prs, os.path.join(self.TEMPDIR, page))
                if page == page_list[0]:                                    # if current page is the cover
                    if self.XML_FILE is not None:                           # if an XML file was found
                        prs = csimage.add_xml_slide(prs, xml_dict)          # Create Main Metadata page
                    if "summary_dict" in locals():                          # If Summary dict exists in variables
                        if 'Summary' in summary_dict:                       # and contains Summary
                            prs = csimage.add_xml_slide(prs, summary_dict)      # Create Summary page

            """ SAVE PPTX """
            new_pptx_folder_and_filename = self.new_file_path(self.SUBMITTED_FILE)
            csimage.save_pptx(prs, new_pptx_folder_and_filename)
            return self.FAILED_LIST
















# # Remake Folder Structure in SOURCEDIR to OUTPUTDIR
# def RemakeFolderStructure(SOURCEDIR, OUTPUTDIR):
#     for Foldername, Subfolders, Filenames in os.walk(SOURCEDIR):
#          NewFolder(Foldername, SOURCEDIR, OUTPUTDIR)
#
# def NewFolder(foldername, SOURCEDIR, OUTPUTDIR):
#     if os.path.exists(os.path.join(OUTPUTDIR, os.path.relpath(foldername, SOURCEDIR))):  # Does Current Folder exist in new location
#         print(foldername + 'Folder Exists in OUTPUTDIR!')
#     else:
#         os.mkdir(os.path.join(OUTPUTDIR, os.path.relpath(foldername, SOURCEDIR)))  # Create folder
#         print(foldername + ' created in OUTPUTDIR!')

