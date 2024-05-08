from selenium.webdriver.common.by import By

import logging

from main import base_url
from models import CoordinatedProductInfo, SizeChart, ProductMeta, ItemRating, Review, \
    Product
from utils import auto_scroll, get_text, wait, get_attribute, parse_reviewer_id_from_id, \
    scroll_down


def fetch_product_ids(wd):
    total_pages = [1, 2, 3]
    ids = []

    for page in total_pages:
        url = f"{base_url}/item/?order=11&gender=mens&limit=100&category=wear&page={page}"
        print(f"Fetching Product Page: {url}")
        try:
            wd.get(url)
        except Exception as e:
            logging.error(f"Failed to load page {page}: {e}")

        list_items = wd.find_elements(By.CSS_SELECTOR, ".itemCardArea-cards")
        for index, item in enumerate(list_items):
            if 0 < index < 10:
                scroll_index = index * 10
                try:
                    auto_scroll(wd, f".itemCardArea-cards:nth-child({scroll_index})")
                except Exception as e:
                    logging.error(
                        f"Target Dom not available yet: .itemCardArea-cards:nth-child({scroll_index})")
            try:
                elem = item.find_element(By.CSS_SELECTOR, ".image_link")
                id = elem.get_attribute("data-ga-eec-product-id")
                ids.append(id)
            except Exception as e:
                logging.error(f"[{index}] Failed to find element for attribute: {e}")
    print(f"Total {len(ids)} Product Found")
    return ids


def get_product_info(wd):
    print("Getting Product Detail")
    product_info = Product()

    product_info.breadcrumbs = fetch_breadcrumbs(wd)
    product_info.category = get_text(wd, ".categoryName")
    product_info.name = get_text(wd, ".itemTitle")
    product_info.price = get_text(wd, ".price-value")

    sizes_elements = wd.find_elements(By.CSS_SELECTOR, ".sizeSelectorListItemButton")
    for size_element in sizes_elements:
        size = size_element.text
        product_info.sizes.append(size)

    subheading_elem = wd.find_element(By.CSS_SELECTOR, ".itemFeature")
    product_info.description_title = subheading_elem.text if subheading_elem else ""

    main_text_elem = wd.find_element(By.CSS_SELECTOR, ".commentItem-mainText")
    product_info.description_main_text = main_text_elem.text if main_text_elem else ""

    article_features = wd.find_elements(By.CSS_SELECTOR,
                                        ".articleFeaturesItem.test-feature")
    product_info.description_itemization = [feature.text for feature in
                                            article_features]

    return product_info


def get_coordinated_product_info(wd):
    coordinated_products = []

    carousel_list_items = wd.find_elements(By.CSS_SELECTOR,
                                           ".coordinateItems .carouselListitem")
    for item in carousel_list_items:
        item.click()
        wait(1)
        coordinated_product = CoordinatedProductInfo(
            name=get_text(wd, ".coordinate_item_container .title"),
            price=get_text(wd, ".coordinate_item_container .price-value"),
            product_number=get_attribute(wd, ".coordinate_item_tile", "data-articleid"),
            image_url=base_url + get_attribute(wd, ".coordinate_image_body.test-img",
                                               "src"),
            product_page_url=base_url + get_attribute(wd,
                                                      ".coordinate_item_container .test-link_a",
                                                      "href")
        )
        coordinated_products.append(coordinated_product.__dict__)

    return coordinated_products


def fetch_breadcrumbs(wd):
    breadcrumbs = []

    breadcrumb_items = wd.find_elements(By.CSS_SELECTOR, ".breadcrumbListItemLink")
    for item in breadcrumb_items:
        text = item.text
        breadcrumbs.append(text)

    return breadcrumbs


def parse_size_chart_html(wd):
    size_chart = SizeChart()
    scroll_down(wd)
    rows = wd.find_elements(By.CSS_SELECTOR, ".sizeChartTRow")
    column_headers = wd.find_elements(By.CSS_SELECTOR, ".sizeChartTHeaderCell")
    header_row = [header.text for header in column_headers]
    size_chart.measurements.append(header_row)

    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, ".sizeChartTCell")
        measurements = [cell.text for cell in cells]
        if measurements:
            size_chart.measurements.append(measurements)

    return size_chart.__dict__


def parse_product_meta(wd):
    product_meta = ProductMeta()
    wd.implicitly_wait(2)
    overall_rating_elem = wd.find_element(By.CSS_SELECTOR,
                                          "span.BVRRNumber.BVRRRatingNumber")
    product_meta.overall_rating = overall_rating_elem.text if overall_rating_elem else ""
    num_reviews_elem = wd.find_element(By.CSS_SELECTOR,
                                       "span.BVRRNumber.BVRRBuyAgainTotal")
    product_meta.number_of_reviews = num_reviews_elem.text if num_reviews_elem else ""
    recommended_rate_elem = wd.find_element(By.CSS_SELECTOR, "span.BVRRNumber")
    product_meta.recommended_rate = recommended_rate_elem.text if recommended_rate_elem else ""

    item_ratings = []
    item_rating_elems = wd.find_elements(By.CSS_SELECTOR,
                                         "div.BVRRSecondaryRatingsContainer")
    for item_rating_elem in item_rating_elems:
        label_elem = item_rating_elem.find_element(By.CSS_SELECTOR, ".BVRRLabel")
        label = label_elem.text if label_elem else ""
        rating_elem = item_rating_elem.find_element(By.CSS_SELECTOR,
                                                    ".BVRRRatingRadioImage img")
        rating = rating_elem.get_attribute("title") if rating_elem else ""
        item_ratings.append(ItemRating(label=label, rating=rating).__dict__)
    product_meta.item_ratings = item_ratings

    user_reviews = []
    review_elems = wd.find_elements(By.CSS_SELECTOR, ".BVRRContentReview")
    for review_elem in review_elems:
        review = Review()
        date_elem = review_elem.find_element(By.CSS_SELECTOR, ".BVRRReviewDate")
        review.date = date_elem.text if date_elem else ""
        title_elem = review_elem.find_element(By.CSS_SELECTOR,
                                              ".BVRRValue.BVRRReviewTitle")
        review.title = title_elem.text if title_elem else ""
        desc_elem = review_elem.find_element(By.CSS_SELECTOR,
                                             ".BVRRReviewTextContainer")
        review.description = desc_elem.text if desc_elem else ""
        rating_elem = review_elem.find_element(By.CSS_SELECTOR,
                                               ".BVRRNumber.BVRRRatingNumber")
        review.rating = rating_elem.text if rating_elem else ""
        id_attr = review_elem.get_attribute("id")
        reviewer_id = parse_reviewer_id_from_id(id_attr)
        review.reviewer_id = reviewer_id
        user_reviews.append(review.__dict__)
    product_meta.user_reviews = user_reviews

    return product_meta


def parse_product_tags(wd):
    tags = []
    item_tag_elems = wd.find_elements(By.CSS_SELECTOR,
                                      ".itemTagsPosition .test-category_link .inner a")
    for item_tag_elem in item_tag_elems:
        tag = item_tag_elem.text
        tags.append(tag)
    return tags
