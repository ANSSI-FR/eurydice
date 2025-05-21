import { server } from '@tests/mocks/server/node';
import { SetupServerApi } from 'msw/node';
import { describe, expect, it } from 'vitest';

describe('MSW Server', () => {
  it('should be set correctly', () => {
    expect(server instanceof SetupServerApi).toBe(true);
  });
});
