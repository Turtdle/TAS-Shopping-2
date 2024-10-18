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
json_data = {"state": "michigan", "address": "10025 E Highland Rd, Howell, MI 48843-1879", "grocery_list":shopping_list}


url = "https://oj35b6kjt7.execute-api.us-west-2.amazonaws.com/default/create_route"

key = ""
headers = {
    "Content-Type": "application/json",
    "x-api-key": key
}

response = requests.post(url, json=json_data, headers=headers)
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