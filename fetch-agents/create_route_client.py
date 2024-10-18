from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from PIL import Image
from io import BytesIO

class ShoppingRouteRequest(Model):
    state: str
    address: str
    grocery_list: list

class ShoppingRouteResponse(Model):
    route_image: bytes

# Create a client agent
client_agent = Agent(name="client_agent", endpoint=["http://127.0.0.1:8000/submit"], port=8000)

# Fund the agent if necessary
fund_agent_if_low(client_agent.wallet.address())

# Store the shopping agent address
SHOPPING_AGENT_ADDRESS = "http://0.0.0.0:8000" # Replace with the actual address of your shopping agent

@client_agent.on_interval(period=10.0)
async def send_request(ctx: Context):
    # Prepare the request
    request = ShoppingRouteRequest(
        state="alabama",
        address="250 S Colonial Dr, Alabaster, AL 35007-4657",
        grocery_list=["tech", "grocery", "shoes", "girls", "mens", "bedding", "pets"]
    )
    
    # Send the request to the shopping agent
    ctx.logger.info(f"Sending request to shopping agent")
    await ctx.send(SHOPPING_AGENT_ADDRESS, request)

@client_agent.on_message(model=ShoppingRouteResponse)
async def handle_response(ctx: Context, sender: str, msg: ShoppingRouteResponse):
    ctx.logger.info(f"Received response from {sender}")
    
    # Convert bytes to image and display
    image = Image.open(BytesIO(msg.route_image))
    image.show()

if __name__ == "__main__":
    client_agent.run()