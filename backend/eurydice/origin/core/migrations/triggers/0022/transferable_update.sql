CREATE OR REPLACE FUNCTION trigger_on_transferable_update ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Update 'auto_' fields in updated OutgoingTransferables
    --
    IF OLD.submission_succeeded_at IS NULL AND 
       NEW.submission_succeeded_at IS NOT NULL THEN 
        NEW.auto_state_updated_at := NEW.submission_succeeded_at;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_transferable_update ON eurydice_outgoing_transferables;

CREATE TRIGGER on_transferable_update
    BEFORE UPDATE ON eurydice_outgoing_transferables
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_on_transferable_update ();

