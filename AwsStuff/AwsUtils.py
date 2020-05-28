import boto3
import json
import os
from zipfile import ZipFile

CLIENT = boto3.client('lambda')


class AwsLambdaPot:

    # Default Values
    runtime = "python3.8"
    role = 'arn:aws:iam::080763178885:role/lambda_full'
    handler = "ComicSliderLambdaHandler.lambda_handler"
    function_name = None
    file_list = None

    def __init__(self, function_name, file_list):
        self.function_name = function_name
        self.file_list = file_list

    @staticmethod
    def make_zip(zipfilename, file_list):
        # create a ZipFile object
        zip_obj = ZipFile(zipfilename, 'w')

        # Add multiple files to the zip
        for file in file_list:
            zip_obj.write(file)

        # close the Zip File
        zip_obj.close()

        return os.path.abspath(zipfilename)

    def create_new(self):

        zipfile_abspath = AwsLambdaPot.make_zip(self.function_name + '.zip', self.file_list)
        contents = open(zipfile_abspath, 'rb').read()

        CLIENT.create_function(
            FunctionName=self.function_name,
            Runtime=self.runtime,
            Role=self.role,
            Handler=self.handler,
            #Environment=DEFAULTS['environment'],
            Code={
               'ZipFile': contents
            }
    )

    def delete(self):
        CLIENT.delete_function(
            FunctionName=self.function_name
        )
        return

    def update(self):

        zipfile_abspath = AwsLambdaPot.make_zip(self.function_name + '.zip', self.file_list)
        contents = open(zipfile_abspath, 'rb').read()

        resp = CLIENT.update_function_code(
            FunctionName=self.function_name,
            ZipFile=contents
        )

        print(resp)
        return

#function to copy temp file to bucket
def TempToBucket(file, filename, targetbucket): #"comicslidertemp"
    s3 = boto3.resource('s3')
    def print_progress(num_of_bytes_uploaded):
        print(f"Written {num_of_bytes_uploaded} to S3 bucket.") #this doesn't seem to return anything in lambda
                                                                # when whole func is run

    s3.meta.client.upload_file(file, targetbucket, filename, Callback=print_progress)
    return {'body': json.dumps('File written')}


#Generate URL to Bucket file
def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
