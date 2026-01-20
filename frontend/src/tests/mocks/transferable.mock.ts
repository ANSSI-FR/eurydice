import type { Transferable } from '@common/models/Transferable';

export const transferableMock: Transferable = {
  id: '6778135b-6406-448d-8119-788c594062ac',
  createdAt: '2025-03-06T15:50:39.871828+01:00',
  name: 'TEST1.pdf',
  sha1: null,
  size: 1073741824,
  userProvidedMeta: { 'Metadata-Name': 'TEST1.pdf' },
  submissionSucceeded: false,
  submissionSucceededAt: null,
  state: 'SUCCESS',
  progress: 0,
  bytesTransferred: 0,
  finishedAt: null,
};

export const txtTransferableMock: Transferable = {
  id: '6778135b-6406-448d-8119-788c594062ab',
  createdAt: '2025-03-06T15:50:39.871828+01:00',
  name: 'TEST2.txt',
  sha1: null,
  size: 1073741824,
  userProvidedMeta: { 'Metadata-Name': 'TEST2.txt' },
  submissionSucceeded: false,
  submissionSucceededAt: null,
  state: 'ERROR',
  progress: 0,
  bytesTransferred: 0,
  finishedAt: null,
};
