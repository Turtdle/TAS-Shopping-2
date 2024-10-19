import json
import requests
import base64
from PIL import Image
from io import BytesIO
shopping_list = [
    "apples",
    "shampoo",
    "dogfood",
    "toiletpaper",
    "socks",
]
address = "1698 US Highway 98, Daphne, AL 36526-4252"
state = "alabama"
#get_categories #state, address -> labels
#categorize_items #categories, grocery list -> grocery_dic
#create_route #state, address, grocery_dic -> image

base_url = "https://oj35b6kjt7.execute-api.us-west-2.amazonaws.com/default/"


key = ""
headers = {
    "Content-Type": "application/json",
    "x-api-key": key
}

data1 = {
    "state": state,
    "address": address
}
print(data1)
response = requests.post(base_url + "get_categories", json=data1, headers=headers)
print(f'response 1: {response.json()}')
data2 = {
    "categories": response.json()['labels'],
    "grocery_list": shopping_list
}
print(data2)
response = requests.post(base_url + "categorize_items", json=data2, headers=headers)
print(f'response 2: {response.json()}')
data3 = {
    "state": state,
    "address": address,
    "grocery_dic": response.json()
}

print(f'data3: {data3}')
response = requests.post(base_url + "create_route", json=data3, headers=headers, timeout=1000)
if response.status_code == 200:
    print("Request successful!")
    response_data = response.json()
    base64_image = response_data['image']
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))
    image.save("route_image.png")
    print("Image saved as 'route_image.png'")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(f"Response content: {response.text}")