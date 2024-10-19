import os
from anthropic import Anthropic
import json
def categorize_backup(users_list, list_of_possible_categories):
    client = Anthropic(
        api_key=""
    )
    categories = list_of_possible_categories
    shopping_list = users_list
    prompt = f'Given this shopping list: {shopping_list}, and these categories: {categories}, categorize the shopping list into the categories. Output must be in json format, where keys is the categories and values is the items.'
    message = client.messages.create(
        max_tokens=500,
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

shopping_list = [
    "apples",
    "shampoo",
    "dogfood",
    "toiletpaper",
    "socks",
]

cat = ['accessories', 'activewear', 'automotive', 'baby', 'bath', 'beauty', 'bedding', 'boys', 'cafe', 'cards/party', 'checkout', 'entertainment', 'entrance', 'fitting rooms', 'furniture', 'girls', 'grocery', 'guest service', 'health/beauty', 'home decor', 'home improvement', 'hosiery', 'household', 'household paper', 'infant/toddler', 'intimates', 'kids', 'kitchen', 'maternity', 'meat/seafood', 'mens', 'personal care', 'pets', 'pharmacy', 'restrooms', 'school/office', 'seasonal', 'shoes', 'snacks', 'sporting goods', 'starbucks', 'storage', 'tech', 'toys/games', 'travel', 'womens']

print(categorize_backup(shopping_list, cat))