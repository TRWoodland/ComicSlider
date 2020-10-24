import os
import argparse  # allows input by commandline
from Comic_Slider_Utils_OO import CS_Utils
from Comic_Slider_Logger_OO import CS_Logfile

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
    print(args)
    print("No output folder given or incomplete path")
    exit()

""" FILENAME """

if args.filename:                                   # filename given
    print("Filename given: " + args.filename)
    if not os.path.isfile(args.filename):           # if file doesn't exist
        print("File doesn't exist")
        exit()
    # if not os.path.isabs(args.filename):            # If file doesn't have a complete path
    #     f = os.path.abspath(args.filename)          # build a path from the file
    #     if os.path.isfile(f):                       # if file exist with a built abspath
    #         args.filename = f                      # update it with its path
    #         print("File Found: " + args.filename)
    #     else:
    #         print("File doesn't have a complete path: " + args.filename)
    else:
        print("File Found: " + args.filename)

        """ STARTING """

        print("Ignoring sourcefolder arg. Using file for sourcefolder. Starting process")

        logfile = CS_Logfile()
        test = CS_Utils(SUBMITTED_FILE=args.filename,
                        SOURCEDIR=os.path.dirname(args.filename),   # use arg.filename for sourcefolder
                        OUTPUTDIR=args.outputfolder,
                        AWS=AWS)
        test.start_the_process()

        args.sourcefolder = ""  # preventing sourcefolder being used

""" SOURCEFOLDER """

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
                logfile = CS_Logfile()
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

""" # TODO: """

# TODO: How to better implement the logger module. How to pass between objects?
# TODO: Add check for "File Already Exists" before process starts. Add Ignore.  Overwrite. Overwrite All. Ignore All.
# TODO: Code Review!
