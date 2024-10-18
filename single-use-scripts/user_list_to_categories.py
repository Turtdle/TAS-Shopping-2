
import google.generativeai as genai
import os
import re
import json
def categorize(users_list, list_of_possible_categories):
    genai.configure(api_key="AIzaSyAqU_M34G6tMTlTcNTCmznAX83xGnyBOG0")
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
    system_instruction="You must output a json. The list of items is a list of strings, and the categories are a list of strings. The function should return a dictionary where the keys are the categories and the values are lists of items that belong to that category. If an item does not belong to any of the categories, it should be ignored. If an item belongs to multiple categories, it should be included in all the relevant categories.")
    try:
        response = model.generate_content(f'categorize(items: {users_list}, categories:{list_of_possible_categories})')
        response = response.text
        response = re.sub(r'\s+', '', response)
        response = response.replace('\n+"', response)
        clean = re.findall(r'```(.+?)```', response)[0]
        clean = clean[4:]
        a = json.loads(clean)
        if len(a.keys()) - 1 == len(list_of_possible_categories):
            return a
        else:
            return None
    except:
        return None
