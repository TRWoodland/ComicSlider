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
        return

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
            # Environment=DEFAULTS['environment'],
            Code={
               'ZipFile': contents
            }
        )
        os.remove(zipfile_abspath)
        return

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
        os.remove(zipfile_abspath)
        return


