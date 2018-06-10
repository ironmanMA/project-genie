from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from time import strftime
import boto3
from binascii import a2b_base64
from ffmpy import FFmpeg
import uuid

__author__ = "@ironman"
BUCKET_NAME = 'project-genie-meetings'
s3_client = boto3.client('s3')

LOG_ROOT = "/home/ubuntu/encoder-server/"
# LOG_ROOT = "/Users/mohammad/Personal/project-genie/lambda-python/"

import logging
import traceback
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/encode', methods=['POST'])
def encode():
    logger.info("request.headers " + str(request.headers))
    logger.info(request.headers.environ)
    webm_binary_data = a2b_base64(request.data.split("base64,")[1])
    rand_filename = str(uuid.uuid4())
    input_file_name = "/tmp/" + rand_filename + ".webm"
    output_file_name = "/tmp/" + rand_filename + ".mp3"
    convertWebmToMp3(webm_binary_data, input_file_name, output_file_name)
    output_s3key_mp3 = "meeting_" + request.headers.environ['HTTP_MEETING_ID'] + "/raw_audio/" + \
                       request.headers.environ[
                           'HTTP_AUDIO_PART_NAME'] + ".mp3"
    uploadToS3(output_file_name, output_s3key_mp3, request.headers.environ['HTTP_USERNAME'],
               request.headers.environ['HTTP_MEETING_ID'], "audio/mp3")
    logger.info("request.data " + request.data)
    os.remove(input_file_name)
    os.remove(output_file_name)

    response = {
        "statusCode": 200
    }
    return response

@app.route('/endMeeting', methods=['POST'])
def encode():
    rand_filename = str(uuid.uuid4())
    input_file_name = "/tmp/" + rand_filename + ".txt"
    input_file = open(input_file_name, 'wb')
    input_file.write("COMPLETED")
    input_file.close()
    output_s3key_mp3 = "meeting_" + request.headers.environ['HTTP_MEETING_ID'] + "/complete"
    uploadToS3(input_file, output_s3key_mp3, request.headers.environ['HTTP_USERNAME'],
               request.headers.environ['HTTP_MEETING_ID'], "text/plain")
    logger.info("request.data " + request.data)
    os.remove(input_file_name)
    response = {
        "statusCode": 200
    }
    return response

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.error('%s %s %s %s %s %s',
                     ts,
                     request.remote_addr,
                     request.method,
                     request.scheme,
                     request.full_path,
                     response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                 ts,
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 tb)
    return "Internal Server Error", 500


def convertWebmToMp3(webm_binary_data, input_file_name, output_file_name):
    input_file = open(input_file_name, 'wb')
    input_file.write(webm_binary_data)
    input_file.close()

    ff = FFmpeg(
        inputs={input_file_name: None},
        outputs={output_file_name: '-vn -ab 128k -ar 44100 -y'}
    )
    print(ff.cmd)
    ff.run()


def uploadToS3(file_path, key_name, username, meeting_id, content_type):
    f = open(file_path, 'r')
    binary_data = f.read()
    f.close()
    response = s3_client.put_object(ACL='public-read',
                                    Body=binary_data,
                                    Bucket=BUCKET_NAME,
                                    Key=key_name,
                                    ContentType=content_type,
                                    Metadata={
                                        'username': username,
                                        'meeting_id': meeting_id,
                                    })
    logger.info("response: " + str(response))


if __name__ == '__main__':
    # maxBytes to small number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler(LOG_ROOT + 'app.log', maxBytes=10000, backupCount=3)
    # getLogger(__name__):   decorators loggers to file + werkzeug loggers to stdout
    # getLogger('werkzeug'): decorators loggers to file + nothing to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    app.run(host="0.0.0.0", port=8000, debug=True)
