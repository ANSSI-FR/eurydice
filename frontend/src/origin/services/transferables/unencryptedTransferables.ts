import apiClient from '@common/api/api-client';
import type { AxiosProgressEvent } from 'axios';

export const createPlainTransferable = (
  file: File,
  onUploadProgress: (progress: number) => void,
  abortSignal: AbortSignal,
): Promise<void> => {
  return apiClient.post('/transferables/', file, {
    headers: {
      'Content-Type': 'application/octet-stream',
      'Metadata-Name': encodeURI(file.name),
    },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      // We transform progress to percentage
      const progress = progressEvent.total
        ? (progressEvent.progress ?? 0 / progressEvent.total) * 100
        : 0;
      onUploadProgress(Math.floor(progress));
    },
    signal: abortSignal,
    timeout: 0,
  });
};
