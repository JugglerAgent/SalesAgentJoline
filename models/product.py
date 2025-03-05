class Product:
    def __init__(self, name, description, price, features=None, specifications=None):
        self.name = name
        self.description = description
        self.price = price
        self.features = features or []
        self.specifications = specifications or {}

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'features': self.features,
            'specifications': self.specifications
        }

    def update_info(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_feature(self, feature):
        if feature not in self.features:
            self.features.append(feature)

    def add_specification(self, key, value):
        self.specifications[key] = value