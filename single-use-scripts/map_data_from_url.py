from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import os
import time
from tqdm import tqdm

def get_html_data(filename, link, max_retries=10, desired_width=800, desired_height=800):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(link)

        def click_button_with_retry(selector, retries):
            for attempt in range(retries):
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    return
                except StaleElementReferenceException:
                    if attempt == retries - 1:
                        raise
                    print(f"Stale element, retrying... (Attempt {attempt + 1}/{retries})")
                    driver.refresh()

        click_button_with_retry("[class^='StoreMap_storeInformationButton']", max_retries)

        map_selector = "[class^='FloorMap_svgMapStyles']"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, map_selector))
        )

        html = driver.page_source
        with open(filename, "w") as f:
            f.write(html)
    except TimeoutException:
        print("Timed out waiting for page elements to load")
    except StaleElementReferenceException:
        print("Stale element reference persisted after multiple retries")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        
        driver.quit()

def main():
    with open("output_urls.txt", "r") as f:
        data = f.read() 
    data = eval(data)
    for state in tqdm(data, desc="Processing states"):
        state_folder = "html/" + state.split("/")[-1]
        os.makedirs(state_folder, exist_ok=True)
        for store in tqdm(data[state], desc="Processing stores", leave=False):
            address = store
            filename = state_folder + "/" + address + ".txt"
            link = data[state][store]
            get_html_data(filename, link)
            time.sleep(3)
            
if __name__ == "__main__":
    main()

