import json
from user_list_to_categories import *
from user_list_to_categories_backup import *
import time
def lambda_handler(event, context):
    body = json.loads(event['body'])
    categories = body['categories']
    grocery_list = body['grocery_list']
    for i in range(4):
        dic = categorize(grocery_list, categories)
        if dic:
            break
        time.sleep(0.25)
    if not dic:
        for i in range(2):
            dic = categorize_backup(grocery_list, categories)
            if dic:
                break
            time.sleep(0.25)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(dic)
    }