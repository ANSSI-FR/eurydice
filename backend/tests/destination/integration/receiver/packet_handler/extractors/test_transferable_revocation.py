import hashlib
import logging

import pytest
from faker import Faker

from eurydice.common import enums
from eurydice.common import protocol
from eurydice.destination.core import models
from eurydice.destination.receiver.packet_handler import extractors
from eurydice.destination.receiver.packet_handler.extractors import (
    transferable_revocation,
)
from tests.common.integration import factory as common_factory
from tests.destination.integration import factory as destination_factory
from tests.destination.integration.utils import s3 as s3_utils


@pytest.mark.django_db()
@pytest.mark.parametrize("user_profile_exists", [True, False])
def test_create_failed(
    user_profile_exists: bool, faker: Faker, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.INFO)

    assert not models.IncomingTransferable.objects.exists()

    associated_user_profile_id = faker.uuid4(cast_to=None)

    if user_profile_exists:
        user_profile = models.UserProfile.objects.create(
            associated_user_profile_id=associated_user_profile_id
        )

    transferable_id = faker.uuid4(cast_to=None)
    transferable_name = "archive.zip"
    transferable_sha1 = hashlib.sha1(b"archive.zip").hexdigest()
    transferable_revocation._create_revoked_transferable(
        protocol.TransferableRevocation(
            transferable_id=transferable_id,
            user_profile_id=associated_user_profile_id,
            reason=enums.TransferableRevocationReason.USER_CANCELED,
            transferable_name=transferable_name,
            transferable_sha1=transferable_sha1,
        )
    )

    incoming_transferable = models.IncomingTransferable.objects.get(id=transferable_id)
    assert incoming_transferable.state == models.IncomingTransferableState.REVOKED
    assert incoming_transferable.created_at == incoming_transferable.finished_at
    assert incoming_transferable.name == transferable_name
    assert bytes(incoming_transferable.sha1).decode("utf-8") == transferable_sha1

    if user_profile_exists:
        assert incoming_transferable.user_profile == user_profile
    else:
        assert (
            incoming_transferable.user_profile.associated_user_profile_id
            == associated_user_profile_id
        )


@pytest.mark.django_db()
def test_extract_transferable_revocation_success_no_transferable(
    faker: Faker,
    caplog: pytest.LogCaptureFixture,
):
    assert not models.IncomingTransferable.objects.exists()

    transferable_id = faker.uuid4(cast_to=None)
    transferable_name = "archive.zip"
    transferable_sha1 = hashlib.sha1(b"archive.zip").hexdigest()
    packet = protocol.OnTheWirePacket(
        transferable_revocations=[
            common_factory.TransferableRevocationFactory(
                transferable_id=transferable_id,
                transferable_name=transferable_name,
                transferable_sha1=transferable_sha1,
            )
        ]
    )
    extractors.TransferableRevocationExtractor().extract(packet)

    transferable = models.IncomingTransferable.objects.get(id=transferable_id)
    assert transferable.state == models.IncomingTransferableState.REVOKED
    assert transferable.name == transferable_name
    assert bytes(transferable.sha1).decode("utf-8") == transferable_sha1
    assert [
        f"The IncomingTransferable {transferable_id} has been marked "
        "as REVOKED and its data removed from the storage (if it had any)."
    ] == caplog.messages


@pytest.mark.django_db()
def test_extract_transferable_revocation_success_ongoing_transferable(
    ongoing_incoming_transferable: models.IncomingTransferable,
    caplog: pytest.LogCaptureFixture,
):
    assert (
        ongoing_incoming_transferable.state == models.IncomingTransferableState.ONGOING
    )

    packet = protocol.OnTheWirePacket(
        transferable_revocations=[
            common_factory.TransferableRevocationFactory(
                transferable_id=ongoing_incoming_transferable.id
            )
        ]
    )

    extractors.TransferableRevocationExtractor().extract(packet)
    ongoing_incoming_transferable.refresh_from_db()
    assert (
        ongoing_incoming_transferable.state == models.IncomingTransferableState.REVOKED
    )
    assert not s3_utils.multipart_upload_exists(ongoing_incoming_transferable)
    assert [
        f"The IncomingTransferable {ongoing_incoming_transferable.id} has been marked "
        "as REVOKED and its data removed from the storage (if it had any)."
    ] == caplog.messages


@pytest.mark.django_db()
@pytest.mark.parametrize("state", models.IncomingTransferableState.get_final_states())
def test_extract_transferable_revocation_error_invalid_transferable_state(
    state: models.IncomingTransferableState,
    caplog: pytest.LogCaptureFixture,
):
    incoming_transferable = destination_factory.IncomingTransferableFactory(state=state)
    packet = protocol.OnTheWirePacket(
        transferable_revocations=[
            common_factory.TransferableRevocationFactory(
                transferable_id=incoming_transferable.id
            )
        ]
    )

    extractors.TransferableRevocationExtractor().extract(packet)
    assert [
        f"The IncomingTransferable {incoming_transferable.id} cannot be revoked as "
        f"its state is {state.value}. "
        f"Only {models.IncomingTransferableState.ONGOING.value} transferables "
        f"can be revoked."
    ] == caplog.messages


@pytest.mark.django_db()
def test_extract_transferable_revocation_error_s3(
    caplog: pytest.LogCaptureFixture,
):
    incoming_transferable = destination_factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING
    )
    packet = protocol.OnTheWirePacket(
        transferable_revocations=[
            common_factory.TransferableRevocationFactory(
                transferable_id=incoming_transferable.id
            )
        ]
    )

    extractors.TransferableRevocationExtractor().extract(packet)

    assert "Cannot process revocation" in caplog.text
    incoming_transferable.refresh_from_db()
    assert incoming_transferable.state == models.IncomingTransferableState.ONGOING
