export type UploadingFile = {
  progress: number;
  name: string;
  id: string;
  onUploadProgress: (progress: number) => void;
  status: 'uploaded' | 'uploading' | 'aborted' | 'error';
  abortController: AbortController;
  size: number;
};
