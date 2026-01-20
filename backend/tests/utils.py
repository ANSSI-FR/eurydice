import json

import faker
from django import conf

fake = faker.Faker()
fake.seed_instance(conf.settings.FAKER_SEED)


def process_logs(messages):
    return [json.loads(message.replace("'", '"')) for message in messages]


__all__ = ("fake", "process_logs")
