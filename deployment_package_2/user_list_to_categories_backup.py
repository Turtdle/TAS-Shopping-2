import os
from anthropic import Anthropic
import json
def categorize_backup(users_list, list_of_possible_categories):
    client = Anthropic(
        api_key=os.environ.get("API_KEY_2")
    )
    categories = list_of_possible_categories
    shopping_list = users_list
    prompt = f'Given this shopping list: {shopping_list}, and these categories: {categories}, categorize the shopping list into the categories. Output must be in json format, where keys is the categories and values is the items.'
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="claude-3-opus-20240229"
    )
    try:
        a = json.loads(message.content[0].text)
    except Exception as e:
        a = None
    return a