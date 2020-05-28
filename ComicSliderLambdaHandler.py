import sys, os, tempfile, time
from base64 import urlsafe_b64decode
from pathlib import Path
import boto3, json
from ComicSliderExceptions import BadRequestError, ForbiddenError, InternalServerError
from UtilsLambda import CheckArchive, IsComic, DecompressToTemp, CleanFolder
from ImagesPPTXLambda import MakePresentation, AddSlide, FirstImageDimensions, AddXmlSlide, \
    SavePPTX, ProcessImages
import shutil #for free space
import email.parser

COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
IMAGEEXT = ['.jpg','.jpeg', 'gif', 'png', 'bmp', 'tiff']
OTHEREXT = ['.xml']
ALLOWEDEXT = IMAGEEXT + OTHEREXT

def lambda_handler(event, context):
    file_name = None
    file_contents = None
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

        # Expecting the File to arrive within a HTTP Form of type: multipart/form-data
        form_data = urlsafe_b64decode(event['body-json'])

        msg = email.parser.BytesParser().parsebytes(form_data)

        #print({
         #   part.get_param('name', header='content-disposition'): part.get_payload(decode=True)
         #   for part in msg.get_payload()
        #})

        ############ Temparally Returning early ##########
        return {
            'statusCode': 200,
            'body': json.dumps(msg)
        }

        # Assign values
        file_name       = event['file_name']
        file_contents   = event['file_contents']

        # Check file_name has one of the accepted extensions
        if not IsComic(file_name, COMICEXT):
            raise Exception('Bad Comic Extension')

        # Check temp_dir is empty.
        for file in next(os.walk(temp_dir))[2]: # files in temp_dir
            os.remove(file)
        for folder in next(os.walk(temp_dir))[1]: # subfolders in temp_dir
            shutil.rmtree(folder)


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

        CleanFolder(temp_dir, file_name, ALLOWEDEXT, temp_dir)

        if not ProcessImages(temp_dir, IMAGEEXT):  # Check dimensions, portrait # returns W&H
            print('Process Images Failed')
            exit()
        #TODO: @JOHN if processImages fails/returns false, what exception should be raised?
        # How would it fail?

        # Get dimensions of first image
        width, height = FirstImageDimensions(temp_dir)  # in inches

        # Make presentation
        prs = MakePresentation(width, height)

        # Check XML exists
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
        for page in pageList:  # iterate through the pages
            prs = AddSlide(prs, (os.path.join(temp_dir, page)))  # make page

            if page == pageList[0]:  # if current page is the cover
                if len(XmlDict) > 1:  # if something in XmlDict
                    prs = AddXmlSlide(prs, XmlDict)  # Create Main Metadata page
                if 'Summary' in SummaryDict:  # If Summary dict exists
                    prs = AddXmlSlide(prs, SummaryDict)  # Create Summary page
        return prs

        # TODO make sure the original filename in the variable below
        newFile = SavePPTX(prs, file_name, temp_dir)
        # TODO PPTX File is built, path and file stored as newFile
    except Exception as e:
        raise InternalServerError(str(e))



    # Copy to S3 and return link
    try:
        # write file to S3             source, bucket, target
        s3.meta.client.upload_file(file_name, "comicslidertemp", file_name, Callback=print_progress)


        # TODO fill with remaining copy/link functions


        # Make sure link has been assigned
        assert link is not None

    except Exception as e:
        raise InternalServerError(str(e))

    return {
        'statusCode': 200,
        'body': json.dumps(link)
    }