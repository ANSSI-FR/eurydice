CREATE OR REPLACE FUNCTION trigger_on_revocation_update ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Raise an exception if a TransferableRevocation is changed after its creation
    --
    RAISE EXCEPTION 'TransferableRevocations should not include their associated OutgoingTransferable nor their reason in UPDATE clauses';
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_revocation_update ON eurydice_transferable_revocations;

CREATE TRIGGER on_revocation_update
    AFTER UPDATE OF outgoing_transferable_id,
    reason
    ON eurydice_transferable_revocations
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_on_revocation_update ();

