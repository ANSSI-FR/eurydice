import apiClient from '@common/api/api-client';
import { getServerMetadata } from '@common/services/server-metadata.service';
import { describe, expect, it, vi } from 'vitest';

describe('server-metadata service', () => {
  it('Default mock values work', async () => {
    const res = await getServerMetadata();
    expect(Object.keys(res).length).toBe(3);
    expect('contact' in res).toBe(true);
    expect('badgeColor' in res).toBe(true);
    expect('badgeContent' in res).toBe(true);
  });
  it('Executes correctly the request', async () => {
    const mockFunction = async () => {
      return {
        test: 'serverMetadata',
      };
    };
    const spyOnGetServerMetadata = vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);
    expect(spyOnGetServerMetadata).not.toBeCalled();
    await getServerMetadata();
    expect(spyOnGetServerMetadata).toBeCalled();
  });
});
