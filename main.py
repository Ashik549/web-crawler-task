from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import logging

from selenium.webdriver.common.by import By

from models import Product
from utils import save_product_info_spreadsheet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url = "https://shop.adidas.jp"
chrome_driver_path = "./driver/chromedriver.exe"  # Path to ChromeDriver executable
products = []


def main():
    from services import fetch_product_ids

    options = Options()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")
    # headless option is disabled due to macOS optimazation issue.
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")

    driver = webdriver.Chrome(options=options)
    ids = fetch_product_ids(driver)
    start_time = time.time()
    fetch_product(driver, ids)

    save_product_info_spreadsheet(products)

    total_time = (time.time() - start_time) / 60
    logger.info("Total time elapsed: %.2f Minutes", total_time)
    driver.quit()


def fetch_product(driver, ids):
    for product_id in ids:
        product = fetch_product_info(driver, product_id)
        products.append(product)
        logger.info("Product info for ID %s Fetched successfully", product_id)


def fetch_product_info(driver, product_id):
    from services import get_coordinated_product_info, parse_size_chart_html, \
        parse_product_meta, parse_product_tags

    product = Product()
    url = base_url + "/products/" + product_id + "/"
    logger.info("Fetching Product info for Url %s", url)
    try:
        driver.get(url)
        driver.implicitly_wait(3)

        # Fetch product information
        product.category = driver.find_element(By.CSS_SELECTOR, ".categoryName").text
        product.name = driver.find_element(By.CSS_SELECTOR, ".itemTitle").text
        product.price = driver.find_element(By.CSS_SELECTOR, ".price-value").text

        sizes_elements = driver.find_elements(By.CSS_SELECTOR,
                                              ".sizeSelectorListItemButton")
        product.sizes = [size.text for size in sizes_elements]

        # Fetching sub-heading
        subheading_elem = driver.find_element(By.CSS_SELECTOR, ".itemFeature")
        product.description_title = subheading_elem.text

        # Fetching main text
        main_text_elem = driver.find_element(By.CSS_SELECTOR, ".commentItem-mainText")
        product.description_main_text = main_text_elem.text

        # Fetching article features
        article_features = driver.find_elements(By.CSS_SELECTOR,
                                                ".articleFeaturesItem.test-feature")
        product.description_itemization = [feature.text for feature in article_features]

        product.id = product_id
        product.coordinates = get_coordinated_product_info(driver)
        product.size_chart = parse_size_chart_html(driver)
        product.product_meta = parse_product_meta(driver)
        product.tags = parse_product_tags(driver)

    except Exception as e:
        logger.error("Failed to fetch product info for product ID %s: %s", product_id,
                     e)

    return product


if __name__ == "__main__":
    main()
