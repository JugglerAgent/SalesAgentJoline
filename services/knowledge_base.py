from models.product import Product

class KnowledgeBase:
    def __init__(self):
        self.products = {}
        self.structured_data = {}

    def add_product(self, product):
        if not isinstance(product, Product):
            raise ValueError("Must be a Product instance")
        self.products[product.name] = product

    def get_product(self, name):
        return self.products.get(name)

    def get_all_products(self):
        return list(self.products.values())

    def remove_product(self, name):
        if name in self.products:
            del self.products[name]

    def update_product(self, name, **kwargs):
        if name in self.products:
            self.products[name].update_info(**kwargs)

    def get_product_context(self):
        """Generate a context string about all products for the AI"""
        context = "Available products:\n"
        for product in self.products.values():
            product_dict = product.to_dict()
            context += f"\nProduct: {product_dict['name']}\n"
            context += f"Description: {product_dict['description']}\n"
            # Handle price display
            price = product_dict['price']
            if isinstance(price, (int, float)):
                context += f"Price: {price:.2f}\n"
            else:
                context += f"Price: {price}\n"
            
            if product_dict['features']:
                context += "Features:\n"
                for feature in product_dict['features']:
                    context += f"- {feature}\n"
            
            if product_dict['specifications']:
                context += "Specifications:\n"
                for key, value in product_dict['specifications'].items():
                    context += f"- {key}: {value}\n"
        
        return context
        
    def add_structured_data(self, key, data):
        """Add structured data to the knowledge base"""
        self.structured_data[key] = data
        
    def get_structured_data(self, key):
        """Get structured data from the knowledge base"""
        return self.structured_data.get(key)