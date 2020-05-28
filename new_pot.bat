@echo off

SET AWS_SHARED_CREDENTIALS_FILE=AwsStuff/.credentials
SET PYTHONPATH=%cd%;%PYTHONPATH%
SET SCRIPT=AwsStuff/LambdaCmdLine.py

py -u %SCRIPT% --create_new