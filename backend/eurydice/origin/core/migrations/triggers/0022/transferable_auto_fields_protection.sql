CREATE OR REPLACE FUNCTION trigger_on_auto_field_update ()
    RETURNS TRIGGER
    AS $$
BEGIN
    --
    -- Raise an exception whenever an 'auto_' field is directly UPDATED through a query;
    -- only database triggers are allowed to modify 'auto_' fields, hence the
    -- `WHEN (pg_trigger_depth() < 1)` check
    --
    RAISE EXCEPTION 'SQL queries are not allowed to update auto-field themselves';
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_auto_field_update ON eurydice_outgoing_transferables;

CREATE TRIGGER on_auto_field_update
    AFTER UPDATE OF auto_revocations_count,
    auto_user_revocations_count,
    auto_ranges_count,
    auto_pending_ranges_count,
    auto_transferred_ranges_count,
    auto_canceled_ranges_count,
    auto_error_ranges_count,
    auto_last_range_finished_at,
    auto_bytes_transferred,
    auto_state_updated_at ON eurydice_outgoing_transferables
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)
    EXECUTE PROCEDURE trigger_on_auto_field_update ();

