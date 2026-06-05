from faker import Faker

fake = Faker()


def make_user_data(email=None, password="123456"):
    return {"email": email or fake.unique.email(), "password": password}
