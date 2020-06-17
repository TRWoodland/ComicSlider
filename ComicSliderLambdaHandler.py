import sys, os, tempfile, time
from base64 import urlsafe_b64decode
from pathlib import Path
import boto3, json
from ComicSliderExceptions import BadRequestError, ForbiddenError, InternalServerError, SeeOther
from UtilsLambda import CheckArchive, IsComic, DecompressToTemp, CleanFolder, XmlReader, create_presigned_url
from ImagesPPTXLambda import MakePresentation, AddSlide, FirstImageDimensions, AddXmlSlide, \
    SavePPTX, ProcessImages
import shutil  # for free space
import email.parser
import json

COMICEXT = ['.cbz', '.zip']
IMAGEEXT = ['.jpg','.jpeg', 'gif', 'png', 'bmp', 'tiff']
OTHEREXT = ['.xml']
ALLOWEDEXT = IMAGEEXT + OTHEREXT

s3 = boto3.resource('s3')


def lambda_handler(event, context):
    print("Loaded Modules - Remaining Execution Time: " + str(context.get_remaining_time_in_millis()))
    file_name = None
    file_bytes = None
    link = None
    temp_dir = tempfile.gettempdir()

    try:
        # Test we can write into temp directory
        if not os.access(temp_dir, os.W_OK):
            raise Exception('Unable to get write access to Temp directory')

        # if temp subdirectory doesn't exist
        if not os.path.exists(os.path.join(temp_dir, 'ComicSliderTemp')):
            os.mkdir(os.path.join(temp_dir, 'ComicSliderTemp'))  # make it

        # Update to new temp dir to include sub-directory
        temp_dir = os.path.join(temp_dir, 'ComicSliderTemp')

        # Check we have plenty of space in the temp directory
        total, used, free = shutil.disk_usage(temp_dir) #in bytes
        if free < 419430400: # bytes // (1024 * 1024) # converts to megabytes
            raise Exception('Not enough space to continue')

    except Exception as e:
        raise InternalServerError(str(e))

    print("Temp Dir Checked - Remaining Execution Time: " + str(context.get_remaining_time_in_millis()))

    # Check/Validate Input(The HTTP Request)
    try:
        # Determine Input contains body-json (API Gateway will pass form-data within this)
        if 'body-json' not in event:
            raise Exception("Missing key:body-json")
        if 'params' not in event:
            raise Exception("Missing key:params")
        if 'header' not in event['params']:
            raise Exception("Missing key:header")
        if 'Content-Type' in event['params']['header']:
            form_hdr = event['params']['header']['Content-Type']
        elif 'content-type' in event['params']['header']:
            form_hdr = event['params']['header']['content-type']

        if not isinstance(form_hdr, str):
            raise Exception("Missing form_hdr")

        # Expecting the File to arrive within a HTTP Form of type: multipart/form-data
        # TODO Check encoding in Content-Type header
        form_data = urlsafe_b64decode(event['body-json'])

        # Build a compliant SMIME message
        msg_bytes = "Content-Type: ".encode("utf8") + form_hdr.encode("utf8") + "\n".encode("utf8") + form_data

        # Run through Multipart message sections
        msg = email.message_from_bytes(msg_bytes)
        if msg.is_multipart():
            for part in msg.walk():
                payload = part.get_payload(decode=True)
                if payload is not None:
                    file_bytes = payload
                    file_name = part.get_filename()
        else:
           raise Exception("Unable to open Multipart Form")

        assert file_name is not None
        assert file_bytes is not None

        # Check file_name has one of the accepted extensions
        if not IsComic(file_name, COMICEXT):
            raise Exception('Bad Comic Extension')

        # Check file is too small
        if len(file_bytes) < 1024:
            raise Exception('Comic is too small')

        # Check file is too big
        if len(file_bytes) > 10485760:
            raise Exception('Comic is too big')

        # Write the incoming file onto the filesystem
        f = open(os.path.join(temp_dir, file_name), "wb")
        f.write(file_bytes)
        f.close()

        # Check temp_dir is empty.
        for file in next(os.walk(temp_dir))[2]: # files in temp_dir
            try:
                os.remove(file)
            except Exception:
                print(file + " file could not be deleted when checking temp_dir is empty")

        for folder in next(os.walk(temp_dir))[1]: # subfolders in temp_dir
            try:
                shutil.rmtree(folder)
            except Exception:
                print(folder + " folder could not be deleted when checking temp_dir is empty")


        # Save file into Temp
        # TODO please could new file in temp be stored as file_name

        # Check file is a archive
        if not CheckArchive(os.path.join(temp_dir, file_name)):
            raise Exception('File is not Archive')

        # TODO fill with remaining checking functions

    except Exception as e:
        # If anything wrong with the users input response with BadRequestError Exception
        raise BadRequestError(str(e))

    print("Checked Input is Archive - Remaining Execution Time: " + str(context.get_remaining_time_in_millis()))

    # Decompress and clean
    try:
        if not DecompressToTemp(os.path.join(temp_dir, file_name), temp_dir): #File, and folder
            raise Exception('Failed to decompress into Temp directory')

        if not CleanFolder(temp_dir, file_name, ALLOWEDEXT, temp_dir):
            raise Exception('Clean Folder Failed')

        if not ProcessImages(temp_dir, IMAGEEXT):  # Check dimensions, portrait # returns W&H
            raise Exception('Process Images Failed')

        # Get dimensions of first image
        width, height = FirstImageDimensions(temp_dir)  # in inches

        # Make presentation
        prs = MakePresentation(width, height)

        # Check XML exists
        print("Check XML exists")
        XmlDict = {}
        if os.path.isfile(os.path.join(temp_dir, 'ComicInfo.xml')):  # If ComicInfo exists
            XmlDict = XmlReader(os.path.join(temp_dir, 'ComicInfo.xml'))
        else:
            if os.path.isfile(os.path.join(temp_dir, '{Extra} ComicInfo.xml')):
                XmlDict = XmlReader(os.path.join(temp_dir, '{Extra} ComicInfo.xml'))

        # Seperate Summary
        SummaryDict = {}
        if 'Summary' in XmlDict:
            SummaryDict['Summary'] = XmlDict['Summary']
            del XmlDict['Summary']

        # Make list of filenames
        pageList = []
        for page in next(os.walk(temp_dir))[2]:
            FName, FExt = os.path.splitext(page)
            if FExt == '.jpg':
                pageList.append(page)

        pageList = sorted(pageList)
        print("sorted:")
        print(*pageList)

        # BUILD COMIC
        for page in pageList:  # iterate through the pages
            prs = AddSlide(prs, (os.path.join(temp_dir, page)))  # make page

            if page == pageList[0]:  # if current page is the cover
                if len(XmlDict) > 1:  # if something in XmlDict
                    prs = AddXmlSlide(prs, XmlDict)  # Create Main Metadata page
                if 'Summary' in SummaryDict:  # If Summary dict exists
                    prs = AddXmlSlide(prs, SummaryDict)  # Create Summary page

        if prs is None:
            raise Exception('prs is none')

        newFile = SavePPTX(prs, file_name, temp_dir)

    except Exception as e:
        raise InternalServerError(str(e))

    print("Built PPTX - Remaining Execution Time: " + str(context.get_remaining_time_in_millis()))

    # Copy to S3 and return link
    try:
        # write file to S3             source, bucket, target
        s3.meta.client.upload_file(newFile, "comicslidertemp", os.path.split(newFile)[1]) #strips path from newFile

        bucketUrl = create_presigned_url("comicslidertemp", os.path.split(newFile)[1], 3600)

        # TODO fill with remaining copy/link functions


        # Make sure link has been assigned
        if not isinstance(bucketUrl, str):
            raise Exception('link is not a string')
        if bucketUrl is None:
            raise Exception('link is none')

    except Exception as e:
        raise InternalServerError(str(e))

    print("Saved to S3 - Remaining Execution Time: " + str(context.get_remaining_time_in_millis()))

    # Default is to response with a HTTP 303 SeeOther, which redirects the client to the comic file
    return {"location": bucketUrl}