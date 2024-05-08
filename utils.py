import json
import os
import time
from selenium.webdriver.common.by import By
from pyexcelerate import Workbook


def wait(second):
    time.sleep(second)


def auto_scroll(wd, selector):
    try:
        el = wd.find_element(By.CSS_SELECTOR, selector)
        wd.execute_script("arguments[0].scrollIntoView(true);", el)
        wait(1)
    except Exception as e:
        print(f"Dom scrolling error: {e}")


def get_attribute(wd, selector, attribute):
    try:
        elem = wd.find_element(By.CSS_SELECTOR, selector)
        return elem.get_attribute(attribute)
    except Exception as e:
        print(f"Failed to find element for attribute: {e}")
        return ""


def get_text(wd, selector):
    try:
        elem = wd.find_element(By.CSS_SELECTOR, selector)
        return elem.text
    except Exception as e:
        print(f"Failed to find element for text: {e}")
        return ""


def parse_reviewer_id_from_id(id):
    parts = id.split("_")
    return parts[-1]


def save_product_info_json(products):
    dist_folder = "dist/json"
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)

    filename = os.path.join(dist_folder, "products.json")
    mode = "a" if os.path.exists(filename) else "w"

    with open(filename, mode) as file:
        if mode == "w":
            file.write("[\n")
        else:
            file.seek(-2, os.SEEK_END)

        for i, product in enumerate(products):
            product_json = json.dumps(product.__dict__)
            file.write(product_json)
            if i < len(products) - 1:
                file.write(",\n")

        file.write("\n]")


def save_product_info_spreadsheet(products):
    dist_folder = "dist/sheets"
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)

    filename = os.path.join(dist_folder, "products.xlsx")

    sheet_data = [
        ["ID", "Category", "Name", "Price", "Sizes", "Breadcrumbs", "Coordinates",
         "Description Title", "Description MainText", "Description Itemization",
         "SizeChart", "OverallRating", "NumberOfReviews", "RecommendedRate",
         "KWs", "ItemRatings", "UserReviews"]]

    for product in products:
        coordinates_json = json.dumps(product.coordinates)
        item_ratings_json = json.dumps(product.product_meta.item_ratings)
        user_reviews_json = json.dumps(product.product_meta.user_reviews)

        row_data = [
            product.id, product.category, product.name, product.price,
            ",".join(product.sizes), ",".join(product.breadcrumbs),
            coordinates_json, product.description_title,
            product.description_main_text,
            ",".join(product.description_itemization), str(product.size_chart),
            product.product_meta.overall_rating,
            product.product_meta.number_of_reviews,
            product.product_meta.recommended_rate,
            ",".join(product.tags),
            item_ratings_json, user_reviews_json
        ]
        sheet_data.append(row_data)

    wb = Workbook()
    wb.new_sheet("Products", data=sheet_data)
    wb.save(filename)


def scroll_down(driver):
    """A method for scrolling the page."""

    # Get scroll height.
    stop_scrolling = 0
    while True:
        stop_scrolling += 1
        driver.execute_script("window.scrollBy(0,100)")
        time.sleep(0.5)
        if stop_scrolling > 100:
            break
    time.sleep(3)
