import sys, os, tempfile, time
from pathlib import Path
import boto3, json
from ComicSliderExceptions import BadRequestError, ForbiddenError, InternalServerError
from Utils import CheckArchive, IsComic, DecompressToTemp

COMICEXT = ['.cbz', '.cbr', '.rar', '.zip']
TEMPDIR = "/tmp"

def lambda_handler(event, context):
    file_name = None
    file_contents = None
    link = None

    try:
        # Test we can write into temp directory
        if not os.access(TEMPDIR, os.W_OK):
            raise Exception('Unable to get write acces to Temp directory')

        # Check we have plenty of space in the temp directory

    except Exception as e:
        raise InternalServerError(str(e))

    # Check/Validate Input(The HTTP Request)
    try:
        # Determine Input contains file
        if not hasattr(event, 'file_name'):
            raise Exception("Missing key:file_name")
        if not hasattr(event, 'file_contents'):
            raise Exception("Missing key:file_contents")

        # Assign values
        file_name       = event['file_name']
        file_contents   = event['file_contents']

        # Check file_name has one of the accepted extensions
        if not IsComic(file_name, COMICEXT):
            raise Exception('Bad Comic Extension')

        # Save file into Temp

        # Check file is a archive
        if not CheckArchive(file_name):
            raise Exception('File is not Archive')

        # TODO fill with remaining checking functions

    except Exception as e:
        # If anything wrong with the users input response with BadRequestError Exception
        raise BadRequestError(str(e))



    # Decompress and clean
    try:
        if not DecompressToTemp(file_name, TEMPDIR):
            raise Exception('Failed to decompress into Temp directory')


        # TODO fill with remaining clean functions

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