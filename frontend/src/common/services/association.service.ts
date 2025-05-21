import apiClient from '@common/api/api-client';

export const getAssociationToken = (config = {}): Promise<AssociationToken> => {
  return apiClient.get('/user/association/', config);
};

export const validateAssociationToken = (token: string, config = {}): Promise<any> => {
  return apiClient.post('/user/association/', { token: token }, config);
};
