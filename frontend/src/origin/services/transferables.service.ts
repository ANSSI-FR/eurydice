import apiClient from '@common/api/api-client';
import { toastMessage } from '@common/services/toast-message.service';
import { bytesToString } from '@common/utils/bytes-functions';
import { type AxiosProgressEvent } from 'axios';

export const cancelTransferable = (transferableId: string): Promise<void> => {
  return apiClient.delete(`/transferables/${transferableId}/`);
};

export const createTransferable = (
  file: File,
  onUploadProgress: (progress: number) => void,
  abortSignal: AbortSignal,
): Promise<void> => {
  if (validateTransferable(file)) {
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
    });
  } else {
    return Promise.reject();
  }
};

export const validateTransferable = (file: any): boolean => {
  const TRANSFERABLE_MAX_SIZE = Number(
    import.meta.env.VITE_TRANSFERABLE_MAX_SIZE ?? '54975581388800',
  );
  if (!file?.size || file.size > TRANSFERABLE_MAX_SIZE) {
    toastMessage(
      'ValidateTansferable.fileTooLargeTitle',
      'ValidateTansferable.fileTooLargeMessage',
      'error',
      true,
      {
        paramsMessage: {
          fileSize: bytesToString(file.size),
          maxFileSize: bytesToString(TRANSFERABLE_MAX_SIZE),
        },
      },
    );
    return false;
  }
  return true;
};
