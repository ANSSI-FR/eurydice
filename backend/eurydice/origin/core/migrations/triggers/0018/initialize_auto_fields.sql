-- Initialize auto_bytes_transferred
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_bytes_transferred = t2.bytes_transferred
FROM (
    SELECT
        SUM(size) AS bytes_transferred,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    WHERE
        transfer_state = 'TRANSFERRED'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_last_range_finished_at
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_last_range_finished_at = t2.last_range_finished_at
FROM (
    SELECT
        MAX(finished_at) AS last_range_finished_at,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_revocations_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_revocations_count = t2.revocations_count
FROM (
    SELECT
        COUNT(id) AS revocations_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_revocations
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_user_revocations_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_user_revocations_count = t2.user_revocations_count
FROM (
    SELECT
        COUNT(id) AS user_revocations_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_revocations
    WHERE
        transfer_state = 'USER_CANCELED'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_ranges_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_ranges_count = t2.ranges_count
FROM (
    SELECT
        COUNT(id) AS ranges_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_canceled_ranges_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_canceled_ranges_count = t2.canceled_ranges_count
FROM (
    SELECT
        COUNT(id) AS canceled_ranges_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    WHERE
        transfer_state = 'CANCELED'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_error_ranges_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_error_ranges_count = t2.error_ranges_count
FROM (
    SELECT
        COUNT(id) AS error_ranges_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    WHERE
        transfer_state = 'ERROR'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_pending_ranges_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_pending_ranges_count = t2.pending_ranges_count
FROM (
    SELECT
        COUNT(id) AS pending_ranges_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    WHERE
        transfer_state = 'PENDING'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id;

-- Initialize auto_transferred_ranges_count
UPDATE
    eurydice_outgoing_transferables t1
SET
    auto_transferred_ranges_count = t2.transferred_ranges_count
FROM (
    SELECT
        COUNT(id) AS transferred_ranges_count,
        outgoing_transferable_id
    FROM
        eurydice_transferable_ranges
    WHERE
        transfer_state = 'TRANSFERRED'
    GROUP BY
        outgoing_transferable_id) t2
WHERE
    t1.id = t2.outgoing_transferable_id
