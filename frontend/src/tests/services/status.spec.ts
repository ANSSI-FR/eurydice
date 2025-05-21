import apiClient from '@common/api/api-client';
import { getStatus } from '@common/services/status.service';
import { describe, expect, it, vi } from 'vitest';

describe('status service', () => {
  it('Default mock values work for Origin value', async () => {
    const res = await getStatus();
    expect(Object.keys(res).length).toBe(2);
    expect('maintenance' in res).toBe(true);
    expect('lastPacketSentAt' in res).toBe(true);
  });
  it('Executes correctly the request and has correct Destination data', async () => {
    const mockFunction = async () => {
      return {
        lastPacketReceivedAt: Date.now(),
      };
    };
    const spyOnGetStatus = vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);
    expect(spyOnGetStatus).not.toBeCalled();
    const res = await getStatus();
    expect(spyOnGetStatus).toBeCalled();
    expect(Object.keys(res).length).toBe(1);
    expect('lastPacketReceivedAt' in res).toBe(true);
  });
});
