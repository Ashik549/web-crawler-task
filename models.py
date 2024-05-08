class Product:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.category = ""
        self.price = ""
        self.sizes = []
        self.breadcrumbs = []
        self.description_title = ""
        self.description_main_text = ""
        self.description_itemization = []
        self.coordinates = []
        self.size_chart = SizeChart()
        self.product_meta = ProductMeta()
        self.tags = []


class CoordinatedProductInfo:
    def __init__(self, name, price, product_number, image_url, product_page_url):
        self.name = name
        self.price = price
        self.product_number = product_number
        self.image_url = image_url
        self.product_page_url = product_page_url


class SizeChart:
    def __init__(self):
        self.measurements = []


class Review:
    def __init__(self):
        self.date = ""
        self.rating = ""
        self.title = ""
        self.description = ""
        self.reviewer_id = ""


class ItemRating:
    def __init__(self, label, rating):
        self.label = label
        self.rating = rating


class ProductMeta:
    def __init__(self):
        self.overall_rating = ""
        self.number_of_reviews = ""
        self.recommended_rate = ""
        self.item_ratings = []
        self.user_reviews = []
