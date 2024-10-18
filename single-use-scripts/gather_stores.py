import requests
import regex as re
from tqdm import tqdm
import time


def get_state_urls():
    url = "https://www.target.com/store-locator/store-directory"
    response = requests.get(url)
    html = response.text
    state_urls = re.findall(r'href="/store-locator/(.+?)>', html)
    link_prefix = "https://www.target.com/store-locator/"
    state_urls = [link_prefix + store_name for store_name in state_urls]
    state_urls = [store_name for store_name in state_urls if "find-stores" not in store_name]
    state_urls = [store_name[:-1] for store_name in state_urls]
    return state_urls

def get_store_urls(state_url):
    response = requests.get(state_url)
    html = response.text
    store_urls = re.findall(r'<div class="view_cityName__vSrti">(.+?)</a></div>', html)
    for i in range(len(store_urls)):
        store_urls[i] = store_urls[i].split('href="')[1]
        store_urls[i] = store_urls[i].split('">')[0]
    link_prefix = "https://www.target.com"
    store_urls = [link_prefix + store_name for store_name in store_urls]
    return store_urls

def get_store_address(store_url):
    response = requests.get(store_url)
    html = response.text
    address = re.findall(r'data-test="@store-locator/StoreHeader/StoreInfo">(.+?)<br/>Phone:', html)
    if len(address) >= 1:
        address = address[0].replace("<br/>", ", ")
        return address
    return None

def main():
    output = {}
    with open("output_urls.txt", "w+") as f:
        state_urls = get_state_urls()
        for state_url in tqdm(state_urls, desc="Processing states"):
            store_urls = get_store_urls(state_url)
            mini = {}
            for store_url in tqdm(store_urls, desc="Processing stores", leave=False):
                address = get_store_address(store_url)
                if address is not None:
                    mini[address] = store_url
                    time.sleep(1)
            output[state_url] = mini
        f.write(str(output))
                
            

if __name__ == "__main__":
    main()
