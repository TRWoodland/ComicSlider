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







"""Entry parameters"""
parser = argparse.ArgumentParser(description='Comic Slider parser')
parser.add_argument('--filename', help='the file name')
parser.add_argument('--foldername', help='the foldername')
args = parser.parse_args()

if args.filename:  # arg given, do this
    print("Filename given: " + args.filename)
    if not os.path.isfile(args.filename):
        print("File doesn't exist")
        exit()
    if not os.path.isabs(args.filename):  # If file doesn't have a complete path
        print("File doesn't have a complete path: " + args.filename)
    else:
        print("File Found: " + args.filename)

if args.foldername:  # arg given, do this
    print("Foldername given: " + args.foldername)
    if not os.path.exists(args.foldername):
        print("Folder doesn't exist")
        exit()
    else:
        print("Folder Found: " + args.foldername)

if args.filename is None and args.foldername is None:  # if arg not given, do this
    print("no arg given")
    exit()

if os.environ.get("AWS_EXECUTION_ENV") is None:  # test whether on AWS Lambda
    AWS = False
    print("Not running on AWS Lambda")
else:
    AWS = True
    print("on aws. Script not configured for AWS yet")
    exit()
