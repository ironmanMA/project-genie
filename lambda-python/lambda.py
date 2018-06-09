import boto3
import time
from binascii import a2b_base64


BUCKET_NAME='project-genie-meetings'

s3_client = boto3.client('s3')

def lambda_handler(event,context):
    localtime = time.asctime( time.localtime(time.time()) )
    print "Local current time :", localtime
    print("body",event['body'])
    print("headers",event['headers'])
    object_key="meeting_"+event['headers']['meeting_id']+"/raw_audio/"+event['headers']['audio_part_name']
    
    binary_data = a2b_base64(event['body'])
    
    response=s3_client.put_object(ACL='public-read',
    Body=binary_data,
    Bucket=BUCKET_NAME,
    Key=object_key,
    ContentType='audio/mp3',
    Metadata={
        'username': event['headers']['username'],
        'meeting_id': event['headers']['meeting_id'],
    })
    print("response",response)
    response = {
        "statusCode": 200
    };
    return response
