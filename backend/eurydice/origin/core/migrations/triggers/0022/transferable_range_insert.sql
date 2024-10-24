CREATE OR REPLACE FUNCTION trigger_on_range_insert ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Update 'auto_' fields in the OutgoingTransferable associated to newly
    -- inserted TransferableRanges
    --
    IF (NEW.transfer_state != 'PENDING') THEN
        RAISE EXCEPTION 'TransferableRanges are supposed to be created in PENDING state';
    END IF;
    UPDATE
        eurydice_outgoing_transferables
    SET
        auto_ranges_count = auto_ranges_count + 1,
        auto_pending_ranges_count = auto_pending_ranges_count + 1,
        auto_state_updated_at = NEW.created_at
    WHERE
        id = NEW.outgoing_transferable_id;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_range_insert ON eurydice_transferable_ranges;

CREATE TRIGGER on_range_insert
    AFTER INSERT ON eurydice_transferable_ranges
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_on_range_insert ();

