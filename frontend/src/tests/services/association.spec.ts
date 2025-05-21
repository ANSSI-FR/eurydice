import apiClient from '@common/api/api-client';
import {
  getAssociationToken,
  validateAssociationToken,
} from '@common/services/association.service';
import { describe, expect, it, vi } from 'vitest';

describe('association service GET Token', () => {
  it('Default mock values work', async () => {
    const res = await getAssociationToken();
    expect(Object.keys(res).length).toBe(2);
    expect('expiresAt' in res).toBe(true);
    expect('token' in res).toBe(true);
  });
  it('Executes correctly the request', async () => {
    const mockFunction = async () => {
      return {
        expires_at: Date.now(),
        token: 'test token',
      };
    };
    const spyOnGetAssociationToken = vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);
    expect(spyOnGetAssociationToken).not.toBeCalled();
    await getAssociationToken();
    expect(spyOnGetAssociationToken).toBeCalled();
  });
});

describe('association service POST Token', () => {
  it('Default mock values work', async () => {
    const res = await validateAssociationToken('test token');
    expect(Object.keys(res).length).toBe(0);
  });
  it('Executes correctly the request', async () => {
    const mockFunction = async () => {
      return {};
    };
    const spyOnPostAssociationToken = vi.spyOn(apiClient, 'post').mockImplementation(mockFunction);
    expect(spyOnPostAssociationToken).not.toBeCalled();
    await validateAssociationToken('test token');
    expect(spyOnPostAssociationToken).toBeCalled();
  });
});
