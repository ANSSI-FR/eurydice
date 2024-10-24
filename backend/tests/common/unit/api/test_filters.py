from unittest import mock

from faker import Faker

from eurydice.common.api import filters


def test_filter_queryset_by_sha1(faker: Faker):
    sha1_hex = faker.sha1()
    sha1_bin = bytes.fromhex(sha1_hex)

    queryset = mock.Mock()
    filters._filter_queryset_by_sha1(queryset, "sha1", sha1_hex)
    queryset.filter.assert_called_once_with(sha1=sha1_bin)
