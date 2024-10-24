import django.contrib.sessions.models
import factory


class SessionFactory(factory.django.DjangoModelFactory):
    session_key = factory.Faker("pystr", min_chars=40, max_chars=40)
    session_data = factory.Faker("bs")
    expire_date = factory.Faker(
        "date_time_this_decade",
        tzinfo=django.utils.timezone.get_current_timezone(),
    )

    class Meta:
        model = django.contrib.sessions.models.Session
