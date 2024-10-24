/* eslint-disable import/prefer-default-export */

export const TRANSFERABLE_STATES = {
  PENDING: "PENDING",
  SUCCESS: "SUCCESS",
  ONGOING: "ONGOING",
  ERROR: "ERROR",
  CANCELED: "CANCELED",
};

// Maximum object size per operation allowed by minio (50 TiB)
// https://min.io/docs/minio/linux/operations/checklists/thresholds.html#minio-server-limits
export const TRANSFERABLE_MAX_SIZE = 54975581388800;
