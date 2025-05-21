export type Transferable = {
  id: string;
  createdAt: string;
  name: string | null;
  sha1: string | null;
  size: number | null;
  userProvidedMeta: any;
  submissionSucceeded: boolean;
  submissionSucceededAt: string | null;
  state: TransferableState;
  progress: number;
  bytesTransferred: number;
  finishedAt: string | null;
  speed: number | null;
  estimatedFinishDate: string | null;
};
