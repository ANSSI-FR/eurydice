import apiClient from '@common/api/api-client';

export const getServerMetadata = async (): Promise<ServerMetadata> => {
  return apiClient.get('metadata/');
};
