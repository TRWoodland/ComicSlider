import boto3
import json
import os

# DEFAULTS = {'role': open('aws_role.txt').read().strip(),
#             'environment': json.load(open('env_vars.txt'))}
CLIENT = boto3.client('lambda')
# arn:aws:iam::080763178885:user/TomWoodland
#
# arn:aws:iam::0225887334136:role/lambda_exec_role
class AwsUtils(): #namespace

    @staticmethod  # Always there, without creating the object instance
    def Create(zipfilename): # zipfilename is ComicSlider.zip
        abspath = os.path.abspath(zipfilename)
        contents = open(abspath, 'rb').read()

        # Offending code
        CLIENT.create_function(
            FunctionName="ComicSlider",
            Runtime="python3.8",
            Role='arn:aws:iam::080763178885:role/lambda_full',
            Handler="test.MainHandler",
            #Environment=DEFAULTS['environment'],
            Code={
               'ZipFile': contents
            }
    )

    @staticmethod  # Always there, without creating the object instance
    def Remove(functionName):
        return
        #look for client.remove
