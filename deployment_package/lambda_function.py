import json
import boto3
from io import BytesIO
from PIL import Image
import base64
from create_route_helper import *
import time
def get_s3_object(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def lambda_handler(event, context):
    body = json.loads(event['body'])
    state = body['state']
    address = body['address']
    dic = body['grocery_dic']
    print("parsed data!")

    image_data = get_s3_object('targetmapimages', f'images/{state}/{address}.png')
    image = Image.open(BytesIO(image_data))
    trimmed_image, bbox = trim_image(image)
    html_data = get_s3_object('targethtml', f'html/{state}/{address}.txt')
    html = html_data.decode("iso-8859-1")
    barriers_data = get_s3_object('targetmapimages', f'images/{state}/{address}.png_no_names.png')
    print("got s3 data!")
    barriers = Image.open(BytesIO(barriers_data))
    background_size, labels = get_html_data(html)
    adjusted_labels = add_label_markers(trimmed_image, labels, background_size)
    print(labels)
    print(adjusted_labels)
    print("finished func (add label markers)!")
    #label_pixels = flood_fill(Image.new("RGB", trimmed_image.size, "white"), adjusted_labels)
    #print("finished func (flood fill)!")
    label_text = [label[3] for label in labels]
    for label in label_text:
        if label and label not in dic:
            dic[label] = []
    shopping_route = shopping_order(label_positions=labels, grocery_list=dic)
    print("finished func (shopping route)!")
    barriers = process_barriers(barriers, bbox)
    print("finished func (process barriers)!")
    route_image = draw_route(trimmed_image, shopping_route, labels, barriers=barriers, grocery_list=dic)
    print("finished func (draw route)!")  
    buffered = BytesIO()
    route_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'image': img_str
        })
    }
