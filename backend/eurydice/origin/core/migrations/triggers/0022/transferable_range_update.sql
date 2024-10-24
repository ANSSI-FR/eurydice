CREATE OR REPLACE FUNCTION trigger_on_range_update ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Update 'auto_' fields in the OutgoingTransferable associated to
    -- updated TransferableRanges
    --
    -- Below are strict rules about when a TransferableRange is allowed to change ;
    -- these rules were made so that the code below does not have to handle subtle cases
    -- such as updating the size of an already TRANSFERRED range, or the finished_at
    -- field of a range already in a final state
    IF (OLD.outgoing_transferable_id != NEW.outgoing_transferable_id) THEN
        RAISE EXCEPTION 'TransferableRanges should not change their associated OutgoingTransferable';
    END IF;
    IF (OLD.transfer_state != 'PENDING') THEN
        RAISE EXCEPTION 'TransferableRanges should not change if they are not PENDING';
    END IF;
    IF NEW.transfer_state = 'PENDING' THEN
        RAISE EXCEPTION 'TransferableRanges should not change if their state does not change';
    END IF;
    IF NEW.transfer_state = 'TRANSFERRED' THEN
        UPDATE
            eurydice_outgoing_transferables
        SET
            auto_bytes_transferred = auto_bytes_transferred + NEW.size,
            auto_pending_ranges_count = auto_pending_ranges_count - 1,
            auto_transferred_ranges_count = auto_transferred_ranges_count + 1,
            auto_last_range_finished_at = NEW.finished_at,
            auto_state_updated_at = NEW.finished_at
        WHERE
            id = NEW.outgoing_transferable_id;
        RETURN NULL;
    END IF;
    IF NEW.transfer_state = 'ERROR' THEN
        UPDATE
            eurydice_outgoing_transferables
        SET
            auto_pending_ranges_count = auto_pending_ranges_count - 1,
            auto_error_ranges_count = auto_error_ranges_count + 1,
            auto_last_range_finished_at = NEW.finished_at,
            auto_state_updated_at = NEW.finished_at
        WHERE
            id = NEW.outgoing_transferable_id;
        RETURN NULL;
    END IF;
    IF NEW.transfer_state = 'CANCELED' THEN
        UPDATE
            eurydice_outgoing_transferables
        SET
            auto_pending_ranges_count = auto_pending_ranges_count - 1,
            auto_canceled_ranges_count = auto_canceled_ranges_count + 1,
            auto_last_range_finished_at = NEW.finished_at,
            auto_state_updated_at = NEW.finished_at
        WHERE
            id = NEW.outgoing_transferable_id;
        RETURN NULL;
    END IF;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_range_update ON eurydice_transferable_ranges;

CREATE TRIGGER on_range_update
    AFTER UPDATE ON eurydice_transferable_ranges
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_on_range_update ();

