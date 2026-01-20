import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { describe } from 'node:test';
import { expect, it } from 'vitest';

describe('server metadata store', () => {
  it('sets and get server metadata from store', () => {
    const serverMetadata = {
      badgeColor: '#000000',
      badgeContent: 'test',
      contact: 'test',
      encryptionEnabled: true,
      encodedPublicKey: 'gtC32LH1n6qCbkqQog/QwAr7TjxuED2+85o1CRlSl2Y=',
    };
    const serverMetadataStore = useServerMetadataStore();
    expect(serverMetadataStore.getServerMetadata).toBeUndefined();
    serverMetadataStore.setServerMetadata(serverMetadata);
    expect(serverMetadataStore.getServerMetadata).toEqual(serverMetadata);
    serverMetadataStore.$reset();
    expect(serverMetadataStore.getServerMetadata).toBeUndefined();
  });
});
