class AdInfo:
    def __init__(self, title: str, date: str, price: str, url: str, image_url: str = None):
        self.title = title
        self.date = date
        self.price = price
        self.url = url
        self.image_url = image_url 