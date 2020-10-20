# require libraries pip install rarfile xmltodict patool, Pillow
import os
import shutil
import time  # for sleep
from datetime import datetime
import argparse  # allows input by commandline
import tempfile
import logging
from sys import platform
import shutil
from OO_Utils import CS_Utils
from OO_Image import CS_Image
from pathlib import Path


failed_list = []

"""Entry parameters"""
parser = argparse.ArgumentParser(description='Comic Slider parser')
parser.add_argument('--filename', help='the file name')
parser.add_argument('--sourcefolder', help='the sourcefolder')
parser.add_argument('--outputfolder', help='the outputfolder')
args = parser.parse_args()

if os.environ.get("AWS_EXECUTION_ENV") is None:  # test whether on AWS Lambda
    AWS = False
    print("Not running on AWS Lambda")
else:
    AWS = True
    print("on aws. Script not configured for AWS yet")
    exit()

""" INPUT ARGUMENTS """

if not args.outputfolder or not os.path.exists(args.outputfolder):  # if no output folder, or folder doesn't exist
    print("No output folder given or incomplete path")
    exit()

if args.filename:  # arg given, do this
    print("Filename given: " + args.filename)
    if not os.path.isfile(args.filename):
        print("File doesn't exist")
        exit()
    if not os.path.isabs(args.filename):  # If file doesn't have a complete path
        print("File doesn't have a complete path: " + args.filename)
    else:
        print("File Found: " + args.filename)

        """ STARTING """
        print("Ignoring sourcefolder arg. Using file for sourcefolder. Starting process")
        test = CS_Utils(SUBMITTED_FILE=args.filename,
                        SOURCEDIR=os.path.dirname(args.filename),
                        OUTPUTDIR=args.outputfolder,
                        AWS=AWS)
        test.start_the_process()


if args.sourcefolder:  # arg given, do this
    print("sourcefolder given: " + args.sourcefolder)
    if not os.path.exists(args.sourcefolder):
        print("Source folder doesn't exist")
        exit()
    else:
        print("Source folder: " + args.sourcefolder)

        """ STARTING """
        sourcedir = str(args.sourcefolder)
        for dirpath, dirname, files in os.walk(sourcedir):
            for file in files:
                print("Current file: " + os.path.join(dirpath, file))
                test = CS_Utils(SUBMITTED_FILE=os.path.join(dirpath, file),
                                SOURCEDIR=args.sourcefolder,
                                OUTPUTDIR=args.outputfolder,
                                AWS=AWS)
                status = (test.start_the_process())
                # TODO """ NEED TO RETURN PROPER VALUES """
                failed_list.append(status)
        if len(failed_list) > 0:
            print(failed_list)
        else:
            print("Files converted successfully")


if args.filename is None and args.sourcefolder is None:  # if arg not given, do this
    print("No file or source folder given")
    exit()


""" TEST AREA!!! """




#
# print("Run test? y?")
# runtest = input()
# if runtest.lower() == "y":
#     #from OO_Utils import CS_Utils
#
#     OUTPUTDIR = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\ProcessedComics'''
#
#
#     #SOURCEDIR = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics'''
#     SOURCEDIR = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics'''
#     # SUBMITTED_FILE = r"""F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics\7. Marvel Zombies Return\8. Marvel Zombies 3\Marvel Zombies 3 V2008 #1 (of 4) (2008).cbz"""
#     SUBMITTED_FILE = r'''F:\Google Drive\Synced\PythonProjects\ComicSlider\Comics\7. Marvel Zombies Return\8. Marvel Zombies 3\Test.zip'''
#     test = CS_Utils(SUBMITTED_FILE=SUBMITTED_FILE, SOURCEDIR=SOURCEDIR, OUTPUTDIR=OUTPUTDIR, AWS=False)
#     test.start_the_process()

