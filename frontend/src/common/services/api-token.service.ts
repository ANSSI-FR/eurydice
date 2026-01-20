import apiClient from '@common/api/api-client';

export const getApiToken = (): Promise<any> => {
  return apiClient.get('/user/token/');
};

export const deleteApiToken = (): Promise<any> => {
  return apiClient.delete('/user/token/');
};
