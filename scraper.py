import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import re
from datetime import datetime

def scrape_amazon_page(search_query, page_number, driver_path='/Users/bingyi/PycharmProjects/AmazonScrapeList/chromedriver'):
    base_url = "https://www.amazon.com"
    options = webdriver.ChromeOptions()
    options.headless = True
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(1)

    product_name = []
    product_price = []
    product_ratings = []
    product_ratings_num = []
    product_link = []
    product_review_count = []
    bought_last_month = []
    scrape_date = []

    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        driver.get(f'{base_url}/s?k={search_query}&page={page_number}')

        items = wait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]'))
        )

        for item in items:
            try:
                # Try different XPaths to find the product name
                name_xpaths = [
                    './/span[@class="a-size-medium a-color-base a-text-normal"]',
                    './/span[contains(@class, "a-text-normal")]',
                    './/h2/a/span'
                ]
                name = None
                for xpath in name_xpaths:
                    try:
                        name = item.find_element(By.XPATH, xpath).text
                        if name:
                            break
                    except Exception:
                        continue
                if not name:
                    name = 'N/A'
                product_name.append(name)
            except Exception as e:
                product_name.append('N/A')
                print(f"Name Error: {e}")

            try:
                whole_price = item.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
                fraction_price = item.find_elements(By.XPATH, './/span[@class="a-price-fraction"]')
                if whole_price and fraction_price:
                    price = '.'.join([whole_price[0].text, fraction_price[0].text])
                else:
                    price = 'N/A'
                product_price.append(price)
            except Exception as e:
                product_price.append('N/A')
                print(f"Price Error: {e}")

            try:
                ratings_box = item.find_element(By.XPATH, './/div[@class="a-row a-size-small"]')
                ratings = ratings_box.find_element(By.XPATH, './/span[@aria-label]').get_attribute('aria-label')
                product_ratings.append(ratings)
            except Exception as e:
                product_ratings.append('N/A')
                print(f"Ratings Error: {e}")

            try:
                ratings_num = ratings_box.find_element(By.XPATH, './/span[@aria-label]').get_attribute('aria-label')
                product_ratings_num.append(ratings_num)
            except Exception as e:
                product_ratings_num.append('N/A')
                print(f"Ratings Count Error: {e}")

            try:
                link = item.find_element(By.XPATH,
                                         './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute(
                    "href")
                full_link = urljoin(base_url, link)
                product_link.append(full_link)
            except Exception as e:
                product_link.append('N/A')
                print(f"Link Error: {e}")

            try:
                review_count = item.find_element(By.XPATH, './/span[@class="a-size-base s-underline-text"]').text
                review_count = int(re.sub('[^0-9]', '', review_count))
                product_review_count.append(review_count)
            except Exception as e:
                product_review_count.append(0)
                print(f"Review Count Error: {e}")

            try:
                bought_last_month_text = item.find_element(By.XPATH, './/span[@class="a-size-base a-color-secondary"]').text
                if "bought in past month" in bought_last_month_text.lower():
                    bought_last_month.append(bought_last_month_text)
                else:
                    bought_last_month.append('N/A')
            except Exception as e:
                bought_last_month.append('N/A')
                print(f"Bought Last Month Error: {e}")

            scrape_date.append(current_date)

    except Exception as e:
        print(f"Error occurred while scraping: {e}")

    finally:
        driver.quit()

    dict_df = {
        "Name": product_name,
        "Price": product_price,
        "Rating_Stars": product_ratings,
        "Rating_Count": product_ratings_num,
        "Product_Link": product_link,
        "Review_Count": product_review_count,
        "Bought_Last_Month": bought_last_month,
        "Scrape_Date": scrape_date
    }
    return pd.DataFrame(dict_df)

`
def scrape_amazon(search_query, num_pages, driver_path='/Users/bingyi/PycharmProjects/AmazonScrapeList/chromedriver'):
    search_query = search_query.replace(' ', '+')
    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_amazon_page, search_query, i, driver_path) for i in range(1, num_pages + 1)]
            results = [future.result() for future in futures]
        df = pd.concat(results, ignore_index=True)
        df = df.sort_values(by='Review_Count', ascending=False)
        return df
    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        return pd.DataFrame()