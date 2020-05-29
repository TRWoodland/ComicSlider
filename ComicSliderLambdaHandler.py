import sys, os, tempfile, time
from base64 import urlsafe_b64decode
from pathlib import Path
import boto3, json
from ComicSliderExceptions import BadRequestError, ForbiddenError, InternalServerError
from UtilsLambda import CheckArchive, IsComic, DecompressToTemp, CleanFolder, XmlReader, create_presigned_url
from ImagesPPTXLambda import MakePresentation, AddSlide, FirstImageDimensions, AddXmlSlide, \
    SavePPTX, ProcessImages
import shutil #for free space
import email.parser

COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
IMAGEEXT = ['.jpg','.jpeg', 'gif', 'png', 'bmp', 'tiff']
OTHEREXT = ['.xml']
ALLOWEDEXT = IMAGEEXT + OTHEREXT

s3 = boto3.resource('s3')

def lambda_handler(event, context):
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

    # Check/Validate Input(The HTTP Request)
    try:
        # Determine Input contains body-json (API Gateway will pass form-data within this)
        if not 'body-json' in event:
            raise Exception("Missing key:body-json")
        if not 'params' in event:
            raise Exception("Missing key:params")
        # Expecting the File to arrive within a HTTP Form of type: multipart/form-data
        form_data = urlsafe_b64decode(event['body-json'])
        form_hdr = event['params']['header']['Content-Type']
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

        # Write the incoming file onto the filesystem
        f = open(os.path.join(temp_dir, file_name), "wb")
        f.write(file_bytes )
        f.close()

        # Check file_name has one of the accepted extensions
        if not IsComic(file_name, COMICEXT):
            raise Exception('Bad Comic Extension')

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



    # Decompress and clean
    try:
        if not DecompressToTemp(os.path.join(temp_dir, file_name), temp_dir): #File, and folder
            raise Exception('Failed to decompress into Temp directory')

        # TODO fill with remaining clean functions
        print("CleanFolder")
        CleanFolder(temp_dir, file_name, ALLOWEDEXT, temp_dir)
        print("")
        if not ProcessImages(temp_dir, IMAGEEXT):  # Check dimensions, portrait # returns W&H
            print('Process Images Failed')
            exit()
        #TODO: @JOHN if processImages fails/returns false, what exception should be raised?
        # How would it fail?

        # Get dimensions of first image
        width, height = FirstImageDimensions(temp_dir)  # in inches

        # Make presentation
        print("Make presentation")
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

        # BUILD COMIC
        print("Build comic")
        for page in pageList:  # iterate through the pages
            prs = AddSlide(prs, (os.path.join(temp_dir, page)))  # make page

            if page == pageList[0]:  # if current page is the cover
                if len(XmlDict) > 1:  # if something in XmlDict
                    prs = AddXmlSlide(prs, XmlDict)  # Create Main Metadata page
                if 'Summary' in SummaryDict:  # If Summary dict exists
                    prs = AddXmlSlide(prs, SummaryDict)  # Create Summary page

        if prs is None:
            raise Exception('prs is none')

        # TODO make sure the original filename in the variable below
        newFile = SavePPTX(prs, file_name, temp_dir)
        # TODO PPTX File is built, path and file stored as newFile
    except Exception as e:
        raise InternalServerError(str(e))



    # Copy to S3 and return link
    try:
        # write file to S3             source, bucket, target
        s3.meta.client.upload_file(file_name, "comicslidertemp", newFile)

        bucketUrl = create_presigned_url("comicslidertemp", newFile, 3600)

        # TODO fill with remaining copy/link functions


        # Make sure link has been assigned
        if bucketUrl is None:
            raise Exception('link is none')

    except Exception as e:
        raise InternalServerError(str(e))

    return {
        'statusCode': 200,
        'body': bucketUrl
    }