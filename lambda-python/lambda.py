import boto3
import time
from binascii import a2b_base64
from pydub import AudioSegment


BUCKET_NAME='project-genie-meetings'

s3_client = boto3.client('s3')

def convertWebmToMp3(binary_data):
    AudioSegment.from_mp3("/input/file.mp3").export("/output/file.wav", format="wav")


def lambda_handler(event,context):
    localtime = time.asctime( time.localtime(time.time()) )
    print "Local current time :", localtime
    print("body",event['body'])
    print("body_cleaned",event['body'].split("base64,")[1])
    print("headers",event['headers'])
    object_key="meeting_"+event['headers']['meeting_id']+"/raw_audio/"+event['headers']['audio_part_name']
    
    binary_data = a2b_base64(event['body'].split("base64,")[1])
    mp3_binary_data
    
    response=s3_client.put_object(ACL='public-read',
    Body=binary_data,
    Bucket=BUCKET_NAME,
    Key=object_key,
    ContentType=event['headers']['content-type'],
    Metadata={
        'username': event['headers']['username'],
        'meeting_id': event['headers']['meeting_id'],
    })
    print("response",response)
    response = {
        "statusCode": 200
    };
    return response
