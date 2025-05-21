import type { Transferable } from '@common/models/Transferable';

type TransferableListResponse = {
  offset: number;
  count: number;
  newItems: boolean;
  pages: {
    previous: string | null;
    current: string;
    next: string | null;
  };
  paginatedAt: string;
  results: Transferable[];
};
