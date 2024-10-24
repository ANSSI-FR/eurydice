import factory

from eurydice.common import association


class AssociationTokenFactory(factory.Factory):
    user_profile_id = factory.Faker("uuid4", cast_to=None)

    class Meta:
        model = association.AssociationToken


__all__ = ("AssociationTokenFactory",)
