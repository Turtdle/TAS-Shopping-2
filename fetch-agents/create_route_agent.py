from uagents import Agent, Context, Model
import boto3
from io import BytesIO
from PIL import Image
from create_route_helper import *

class ShoppingRouteRequest(Model):
    state: str
    address: str
    grocery_list: list

class ShoppingRouteResponse(Model):
    route_image: bytes

def get_s3_object(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

shopping_agent = Agent(
    name="shopping_route_agent",
    endpoint=["http://127.0.0.1:8000"],
    
)
@shopping_agent.on_message(model=ShoppingRouteRequest)
async def handle_shopping_route_request(ctx: Context, sender: str, msg: ShoppingRouteRequest):
    ctx.logger.info(f"Received request from {sender}")
    
    state = msg.state
    address = msg.address
    grocery_list = msg.grocery_list

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
    
    shopping_route = shopping_order(label_positions=label_positions(label_pixels), label_list=grocery_list)
    barriers = process_barriers(barriers, bbox)
    route_image = draw_route(trimmed_image, shopping_route, label_positions(label_pixels), barriers=barriers)
    
    # Convert the image to bytes
    img_byte_arr = BytesIO()
    route_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    response = ShoppingRouteResponse(route_image=img_byte_arr)
    await ctx.send(sender, response)

if __name__ == "__main__":
    shopping_agent.run()