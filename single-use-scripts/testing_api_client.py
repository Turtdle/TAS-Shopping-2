import requests
import json
import base64
from PIL import Image
from io import BytesIO

# Replace these with your actual API Gateway URL and API Key
api_url = "https://om6pwsal2i.execute-api.us-west-2.amazonaws.com/default/create_route"
api_key = "vMEKwZ3DMH9CTzD0pmLcR5RQV95XeFoa2JjxyH89"

# The data to send in the request body
payload = {
    "state": "alabama",
    "address": "250 S Colonial Dr, Alabaster, AL 35007-4657",
    "grocery_list": ["tech", "grocery", "shoes", "girls", "mens", "bedding", "pets"]
}

# Set up the headers, including the API key
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

# Make the POST request
response = requests.post(api_url, json=payload, headers=headers)

# Check the response
if response.status_code == 200:
    result = response.json()
    # The image will be in the 'image' field of the response as a base64 encoded string
    image_base64 = result['image']
    
    # Decode the base64 string
    image_data = base64.b64decode(image_base64)
    
    # Create a PIL Image object from the decoded data
    image = Image.open(BytesIO(image_data))
    
    # Display the image
    image.show()
    
    print("Successfully received and displayed the route image.")
else:
    print(f"Error: {response.status_code}, {response.text}")