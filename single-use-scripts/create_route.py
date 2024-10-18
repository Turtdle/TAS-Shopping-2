import boto3
from io import BytesIO
from PIL import Image
from create_route_helper import *
from user_list_to_categories import *
import time
def get_s3_object(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def main(state, address, grocery_list):
    image_data = get_s3_object('targetmapimages', f'images/{state}/{address}.png')
    image = Image.open(BytesIO(image_data))
    trimmed_image, bbox = trim_image(image)
    html_data = get_s3_object('targethtml', f'html/{state}/{address}.txt')
    html = html_data.decode("iso-8859-1")
    barriers_data = get_s3_object('targetmapimages', f'images/{state}/{address}.png_no_names.png')
    barriers = Image.open(BytesIO(barriers_data))
    background_size, labels = get_html_data(html)
    image_with_markers, adjusted_labels = add_label_markers(trimmed_image, labels, background_size)
    flood_filled_image, label_pixels = flood_fill(Image.new("RGB", image_with_markers.size, "white"), adjusted_labels)
    label_text = [label[3] for label in labels]
    
    for i in range(4):
        dic = categorize(grocery_list, label_text)
        if dic:
            break
        time.sleep(1)
    if not dic:
        Exception("No categories found")
    dic =  {
    "seasonal" : ["banana"],
    "bedding" : ["banana"],
    "beauty" : ["banana"],
    "entrance" : ["banana"],
    "checkout" : ["banana"]
    }
    shopping_route = shopping_order(label_positions=label_positions(label_pixels), grocery_list=dic)
    barriers = process_barriers(barriers, bbox)
    route_image = draw_route(trimmed_image, shopping_route, label_positions(label_pixels), barriers=barriers, grocery_list=dic)

    route_image.show()

if __name__ == "__main__":
    shopping_list = [
    "seasonal",
    "bedding",
    "beauty"
]
    #json_data = {"state": "michigan", "address": "10025 E Highland Rd, Howell, MI 48843-1879", "grocery_list":shopping_list}


    main("michigan", "10025 E Highland Rd, Howell, MI 48843-1879", shopping_list)