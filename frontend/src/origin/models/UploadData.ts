export type MultipartUploadData = {
  id: string;
  name: string;
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
