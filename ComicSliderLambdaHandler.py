import sys, os, tempfile, time
from base64 import urlsafe_b64decode
from pathlib import Path
import boto3, json
from ComicSliderExceptions import BadRequestError, ForbiddenError, InternalServerError
from UtilsLambda import CheckArchive, IsComic, DecompressToTemp, CleanFolder, EmptyFolderDrop
import shutil #for free space

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
        if not hasattr(event, 'body-json'):
            raise Exception("Missing key:body-json")

        # Expecting the File to arrive within a HTTP Form of type: multipart/form-data
        form_data = urlsafe_b64decode(event['body-json'])

        ############ Temparally Returning early ##########
        return {
            'statusCode': 200,
            'body': form_data
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

    except Exception as e:
        raise InternalServerError(str(e))



    # Copy to S3 and return link
    try:
        # write file to S3
        # s3.meta.client.upload_file(fileToCopy, "comicslidertemp", "LICENSE.txt", Callback=print_progress)


        # TODO fill with remaining copy/link functions


        # Make sure link has been assigned
        assert link is not None

    except Exception as e:
        raise InternalServerError(str(e))




    return {
        'statusCode': 200,
        'body': json.dumps(link)
    }