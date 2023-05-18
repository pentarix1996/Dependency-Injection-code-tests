# provider.py
class Provider:
    def __init__(self) -> None:
        self.products = ["product_1", "product_2"]


# Client.py
from provider import Provider

class Client:
    def __init__(self, provider: Provider) -> None:
        self.provider = provider
    
    def list_products(self):
        print(self.provider.products)