import apiClient from '@common/api/api-client';
import type { Transferable } from '@common/models/Transferable';
import type { TransferableListResponse } from '@common/models/TransferableListResponse';
import type { GenericAbortSignal } from 'axios';

export const listTransferables = (
  params?: TransferableListRequestParams,
  abortSignal?: GenericAbortSignal,
): Promise<TransferableListResponse> => {
  return apiClient.get('/transferables/', { signal: abortSignal, params });
};

export const retrieveTransferable = (transferableId: string): Promise<Transferable> => {
  return apiClient.get(`/transferables/${transferableId}/`);
};
