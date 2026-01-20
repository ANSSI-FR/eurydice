import apiClient from '@common/api/api-client';
import type { EncryptedFileData, MultipartUploadData } from '@origin/models/UploadData';
import SodiumTools from '@origin/utils/sodiumTools';
import { type AxiosResponse } from 'axios';

export const initEncryptedMultipartUpload = async (
  file: File,
  onUploadProgress: (progress: number) => void,
  abortSignal: AbortSignal,
): Promise<MultipartUploadData> => {
  const formData = new FormData();
  return apiClient.post('/transferables/init-multipart-upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'Metadata-Name': encodeURI(file.name),
      'Metadata-Encrypted': 'true',
    },
    onUploadProgress: () => {
      onUploadProgress(0);
    },
    timeout: 0,
    signal: abortSignal,
  });
};

export const yieldFileParts = function* (file: File, partSize: number, nbTotalParts: number) {
  for (let i = 0; i < nbTotalParts; i++) {
    const start = i * partSize;
    const end = Math.min(start + partSize, file.size);
    yield { index: i, part: file.slice(start, end) };
  }
};

export const uploadEncryptedFileParts = async (
  uploadData: MultipartUploadData,
  file: File,
  abortSignal: AbortSignal,
  onUploadProgress: (progress: number) => void,
): Promise<EncryptedFileData> => {
  const nbTotalParts = Math.ceil(file.size / uploadData.partSize);
  const generator = yieldFileParts(file, uploadData.partSize, nbTotalParts);
  let isFirstValue = true;
  let mainPartSize, lastPartSize;

  let result = generator.next();

  const sodiumTools = new SodiumTools();

  while (!result.done) {
    const value = result.value;
    onUploadProgress(Math.ceil((value.index / nbTotalParts) * 100));
    const encryptedPart = sodiumTools.encryptDataSymmetrical(
      new Uint8Array(await value.part.arrayBuffer()),
    );
    if (isFirstValue) {
      mainPartSize = encryptedPart.byteLength;
      isFirstValue = false;
    }
    lastPartSize = encryptedPart.byteLength;

    await sendOneFilePart(uploadData, encryptedPart, abortSignal);

    result = generator.next();
  }
  const totalEncryptedSize = lastPartSize + (nbTotalParts - 1) * mainPartSize;

  return {
    encryptedSize: totalEncryptedSize,
    nbUploadParts: nbTotalParts,
    mainPartSize: mainPartSize,
    lastPartSize: lastPartSize,
    header: sodiumTools.header,
    symmetricKey: await sodiumTools.getEncryptedSymKey(),
  };
};

const sendOneFilePart = async (
  uploadData: MultipartUploadData,
  encryptedFilePart: ArrayBuffer,
  abortSignal: AbortSignal,
) => {
  const formData = new FormData();
  formData.append('file_part', new Blob([encryptedFilePart], { type: 'application/octet-stream' }));
  return apiClient.post(`/transferables/${uploadData.id}/file-part/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'Metadata-Name': encodeURI(uploadData.filename),
    },
    signal: abortSignal,
    timeout: 0,
  });
};

export const finalizeEncryptedMultipartUpload = (
  uploadData: MultipartUploadData,
  file: File,
  encryptionData: EncryptedFileData,
  abortSignal: AbortSignal,
  onUploadProgress: (progress: number) => void,
): Promise<AxiosResponse<any, any>> => {
  const res = apiClient.get(`/transferables/${uploadData.id}/finalize-multipart-upload/`, {
    headers: {
      'Metadata-Name': encodeURI(uploadData.filename),
      'Metadata-Encrypted': true,
      'Metadata-Parts-Count': encryptionData.nbUploadParts,
      'Metadata-Main-Part-Size': encryptionData.mainPartSize,
      'Metadata-Last-Part-Size': encryptionData.lastPartSize,
      'Metadata-Encrypted-Size': encryptionData.encryptedSize,
      'Metadata-Header': encryptionData.header,
      'Metadata-Encrypted-Symmetric-Key': encryptionData.symmetricKey,
    },
    timeout: 0,
    signal: abortSignal,
  });
  res.then(() => {
    onUploadProgress(100);
  });
  return res;
};
