from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import uuid
from datetime import datetime
import random,traceback,logging

# ProxyMesh configuration (use your ProxyMesh account credentials)
PROXY_LIST = [
    "http://username:password@us.proxymesh.com:31280",
    "http://username:password@de.proxymesh.com:31280",
    "http://username:password@fr.proxymesh.com:31280"
]

# MongoDB configuration

DB_NAME = "twitter_trends"
COLLECTION_NAME = "trends"
MONGO_URI="mongodb://localhost:27017"
# Access variables
TWITTER_USERNAME=""
TWITTER_PASSWORD=""


def get_driver_with_proxy():
    try:
        options = Options()
        proxy = random.choice(PROXY_LIST)
        # options.add_argument(f'--proxy-server={proxy}')
        service = Service('C:/webdrivers/chromedriver.exe')  # Ensure this path is correct
        driver = webdriver.Chrome(service=service, options=options)
        print(f"Using Proxy: {proxy}")
        return driver, proxy
    except Exception as e:
        print("Error initializing WebDriver:", str(e))
        traceback.print_exc()
        raise

def scrape_twitter_trends():
    unique_id = str(uuid.uuid4())
    trends = []
    proxy = None

    try:
        driver, proxy = get_driver_with_proxy()
        driver.get("https://x.com/i/flow/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))

        # Login to Twitter
        username = driver.find_element(By.NAME, "text")
        username.send_keys(TWITTER_USERNAME)
        username.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))

        password = driver.find_element(By.NAME, "password")
        password.send_keys(TWITTER_PASSWORD)
        password.send_keys(Keys.RETURN)

        # Wait for "What's Happening" section
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//section//span[contains(text(), 'What’s happening')]"))
        )
        trending_elements = driver.find_elements(By.XPATH, "//div[@data-testid='trend']")[:5]

        # Extract Trend Texts
        trends = [trend.text for trend in trending_elements]

        
    except Exception as e:
        print("Error during scraping:", str(e))
        traceback.print_exc()
        raise e
    finally:
        if 'driver' in locals():
            driver.quit()

    # Save to MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        record = {
            "_id": unique_id,
            "nameoftrend1": trends[0] if len(trends) > 0 else "No Trend Available",
            "nameoftrend2": trends[1] if len(trends) > 1 else "No Trend Available",
            "nameoftrend3": trends[2] if len(trends) > 2 else "No Trend Available",
            "nameoftrend4": trends[3] if len(trends) > 3 else "No Trend Available",
            "nameoftrend5": trends[4] if len(trends) > 4 else "No Trend Available",
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": proxy if proxy else "No Proxy"
        }

        
        collection.insert_one(record)
        print("Record inserted into MongoDB:", record)
        return record

    except Exception as e:
        print("Error saving to MongoDB:", str(e))
        traceback.print_exc()
        raise 


if __name__ == "__main__":
    logging.info("Script starting...")
    try:
        scrape_twitter_trends()
    except Exception as e:
        logging.error("Unhandled exception occurred.")
        traceback.print_exc()