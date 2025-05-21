type TransferableListRequestParams = {
  createdAfter?: number;
  createdBefore?: number;
  delta?: number;
  from?: string;
  name?: string;
  page?: string;
  pageSize?: number;
  sha1?: string;
  state?: TransferableState;
  submissionSucceededAfter?: number;
  submissionSucceededBefore?: number;
  transferFinishedAfter?: number;
  transferFinishedBefore?: number;
};
