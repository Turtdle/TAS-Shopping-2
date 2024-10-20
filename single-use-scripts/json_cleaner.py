import json
json1 = {}

#load json data from output_urls.txt

with open("output_urls.txt", "r") as f:
    data = f.read() 
json1 = eval(data)

with open("output_urls2.json", "r") as f:
    data = f.read() 

json2 = eval(data)

#merge json data
for item in json2:
    if item in json1:
        json1[item].update(json2[item])
    else:
        json1[item] = json2[item]
print(json1)
clean = {}
for item in json1:
    clean[item.split("/")[-1]] = list(json1[item].keys())

#write to stores.json

with open("stores.json", "w+") as f:
    f.write(json.dumps(clean, indent=4))


