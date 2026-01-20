export type MultipartUploadData = {
  id: string;
  filename: string;
  partSize: number;
};

export type EncryptedFileData = {
  encryptedSize: number;
  nbUploadParts: number;
  mainPartSize: number;
  lastPartSize: number;
  header: string;
  symmetricKey: string;
};
