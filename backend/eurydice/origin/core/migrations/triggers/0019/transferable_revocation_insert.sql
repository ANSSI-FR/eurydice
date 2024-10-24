CREATE OR REPLACE FUNCTION trigger_on_revocation_insert ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Update 'auto_' fields in the OutgoingTransferable associated to
    -- newly insterted TransferableRevocations
    --
    IF NEW.reason = 'USER_CANCELED' THEN
        UPDATE
            eurydice_outgoing_transferables
        SET
            auto_revocations_count = auto_revocations_count + 1,
            auto_user_revocations_count = auto_user_revocations_count + 1
        WHERE
            id = NEW.outgoing_transferable_id;
        RETURN NULL;
    ELSE
        UPDATE
            eurydice_outgoing_transferables
        SET
            auto_revocations_count = auto_revocations_count + 1
        WHERE
            id = NEW.outgoing_transferable_id;
        RETURN NULL;
    END IF;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_revocation_insert ON eurydice_transferable_revocations;

CREATE TRIGGER on_revocation_insert
    AFTER INSERT ON eurydice_transferable_revocations
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_on_revocation_insert ();
