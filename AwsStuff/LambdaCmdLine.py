from AwsStuff.AwsLambdaClient import AwsLambdaPot
import argparse

# The files to be bundled together and sent up to Amazon
file_list = ["ComicSliderLambdaHandler.py", "ComicSliderExceptions.py", "ImagesPPTX.py", "Utils.py"]
pot = AwsLambdaPot("ComicSlider", file_list)


parser = argparse.ArgumentParser(description='AWS Lambda ComicSlider Function Manager Script')
parser.add_argument('--create_new', action='store_true', help='Create new function on AWS Lambda')
parser.add_argument('--update', action='store_true', help='Update existing function on AWS Lambda')
args = parser.parse_args()


if args.create_new is None and args.update is None:
    print("no arg given")
    exit()


if args.create_new:
    pot.create_new()
    exit()

if args.update:
    pot.update()
    exit()
