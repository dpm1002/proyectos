class Book:
    def __init__(self, title, author, series=None, published_date=None, description=None, image_url=None):
        self.title = title
        self.author = author
        self.series = series
        self.published_date = published_date
        self.description = description
        self.image_url = image_url


class Manga:
    def __init__(self, title, description=None, original_language="ja", year=None, content_rating="safe", image_url=None):
        self.title = title
        self.description = description
        self.original_language = original_language
        self.year = year
        self.content_rating = content_rating
        self.image_url = image_url


class Game:
    def __init__(self, title, released=None, rating=None, image_url=None):
        self.title = title
        self.released = released
        self.rating = rating
        self.image_url = image_url


class Transaction:
    def __init__(self, transaction_type, category, amount, date):
        self.transaction_type = transaction_type
        self.category = category
        self.amount = amount
        self.date = date
