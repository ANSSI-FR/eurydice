import type { TransferableListResponse } from '@common/models/TransferableListResponse';
import { transferableMock } from '@tests/mocks/transferable.mock';
import { transferableListMock } from '@tests/mocks/transferableList.mock';

export const transferableListResponseMock: TransferableListResponse = {
  count: transferableListMock.length,
  newItems: false,
  offset: 0,
  pages: { previous: null, current: 'currentPageID', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: transferableListMock,
};

export const transferableListResponseMockPage1: TransferableListResponse = {
  count: transferableListMock.length - 1,
  newItems: false,
  offset: 0,
  pages: { previous: null, current: 'pageOld', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: transferableListMock.slice(0, 2),
};

export const transferableListResponseMockPage2: TransferableListResponse = {
  count: transferableListMock.length - 1,
  newItems: false,
  offset: 2,
  pages: { previous: null, current: 'pageOld', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: transferableListMock.slice(2, 4),
};

export const transferableListResponseMockPage3WithNewItems: TransferableListResponse = {
  count: transferableListMock.length - 1,
  newItems: true,
  offset: 4,
  pages: { previous: null, current: 'pageOld', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: transferableListMock.slice(4, 6),
};

export const transferableListResponseMockPage4: TransferableListResponse = {
  count: transferableListMock.length,
  newItems: false,
  offset: 6,
  pages: { previous: null, current: 'pageOld', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: transferableListMock.slice(6, 7),
};

export const newItemsTransferableListResponseMock: TransferableListResponse = {
  count: transferableListMock.length,
  newItems: true,
  offset: 0,
  pages: { previous: null, current: 'pageNew', next: null },
  paginatedAt: '2025-03-06T16:50:42.906532Z',
  results: transferableListMock.slice(0, 2),
};

export const noPreviewTransferableListResponseMock: TransferableListResponse = {
  count: 6,
  newItems: false,
  offset: 0,
  pages: { previous: null, current: 'currentPageID', next: null },
  paginatedAt: '2025-03-06T15:50:42.906532Z',
  results: [transferableMock],
};
