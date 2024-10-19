import json
import boto3
from io import BytesIO
import re

def get_html_data(html):
    labels = re.findall(r'<text class="adjacency-name normal-format-store" font-family="Helvetica, Verdana" text-anchor="middle" x="(.+?)" y="(.+?)" font-size="(.+?)">(.+?)</text>', html)
    html_no_whitespace = re.sub(r'\n+', '', html)
    background_size = re.findall(r'id="background" role="group" aria-labelledby="background-vo">(.+?)</g>', html_no_whitespace)[0]
    background_size = re.sub(r'[^\d. ]', '', background_size)  
    background_size = background_size.split(" ")
    background_size = [x for x in background_size if x]
    background_size = background_size[:-2]
    background_size = list(zip(background_size[0::2], background_size[1::2]))
    return background_size, labels
def get_s3_object(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()
def lambda_handler(event, context):
    body = json.loads(event['body'])
    state = body['state']
    address = body['address']
    grocery_list = body['grocery_list']
    html_data = get_s3_object('targethtml', f'html/{state}/{address}.txt')
    html = html_data.decode("iso-8859-1")
    background_size, labels = get_html_data(html)
    label_text = [label[3] for label in labels]
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'labels': label_text
        })
    }