import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { describe } from 'node:test';
import { expect, it } from 'vitest';

describe('server metadata store', () => {
  it('sets and get server metadata from store', () => {
    const serverMetadata = { badgeColor: '#000000', badgeContent: 'test', contact: 'test' };
    const serverMetadataStore = useServerMetadataStore();
    expect(serverMetadataStore.getServerMetadata).toBeUndefined();
    serverMetadataStore.setServerMetadata(serverMetadata);
    expect(serverMetadataStore.getServerMetadata).toEqual(serverMetadata);
    serverMetadataStore.$reset();
    expect(serverMetadataStore.getServerMetadata).toBeUndefined();
  });
});
