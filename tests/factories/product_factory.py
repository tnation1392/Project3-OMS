from faker import Faker

fake = Faker()


def make_product_data(name=None, price=99.99, stock=10):
    return {"name": name or fake.unique.word(), "price": price, "stock": stock}
