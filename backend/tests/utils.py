import faker
from django import conf

fake = faker.Faker()
fake.seed_instance(conf.settings.FAKER_SEED)

__all__ = ("fake",)
