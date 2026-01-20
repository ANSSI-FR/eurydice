import apiClient from '@common/api/api-client';
import { toastMessage } from '@common/services/toast-message.service';
import { bytesToString } from '@common/utils/bytes-functions';
import type { MultipartUploadData } from '@origin/models/UploadData';
import {
  finalizeEncryptedMultipartUpload,
  initEncryptedMultipartUpload,
  uploadEncryptedFileParts,
} from '@origin/services/transferables';
import { createPlainTransferable } from '@origin/services/transferables/unencryptedTransferables';
import { type AxiosResponse } from 'axios';

export const cancelTransferable = (transferableId: string): Promise<void> => {
  return apiClient.delete(`/transferables/${transferableId}/`);
};

export const createTransferable = async (
  file: File,
  encrypted: boolean,
  onUploadProgress: (progress: number) => void,
  abortSignal: AbortSignal,
): Promise<AxiosResponse<any, any> | void> => {
  if (validateTransferable(file)) {
    if (encrypted) {
      onUploadProgress(0);
      const uploadData: MultipartUploadData = await initEncryptedMultipartUpload(
        file,
        onUploadProgress,
        abortSignal,
      );
      const encryptedFileData = await uploadEncryptedFileParts(
        uploadData,
        file,
        abortSignal,
        onUploadProgress,
      );
      return finalizeEncryptedMultipartUpload(
        uploadData,
        file,
        encryptedFileData,
        abortSignal,
        onUploadProgress,
      );
    } else {
      return createPlainTransferable(file, onUploadProgress, abortSignal);
    }
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
