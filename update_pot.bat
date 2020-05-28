@echo off


SET PYTHONPATH=%cd%;%PYTHONPATH%
SET SCRIPT=AwsStuff/LambdaCmdLine.py

py -u %SCRIPT% --update