import apiClient from '@common/api/api-client';

export const deleteTransferable = (transferableId: string): Promise<void> => {
  return apiClient.delete(`/transferables/${transferableId}/`);
};

export const deleteAllTransferables = (): Promise<void> => {
  return apiClient.delete('/transferables/');
};

export const getTransferableData = (transferableId: string): Promise<string> => {
  return apiClient.get(`/transferables/${transferableId}/download/`, {
    responseType: 'text',
    timeout: 0,
  });
};
