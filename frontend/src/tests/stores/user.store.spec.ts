import { useUserStore } from '@common/store/user.store';
import { describe } from 'node:test';
import { expect, it } from 'vitest';

describe('user store', () => {
  it('sets and get user from store', () => {
    const userStore = useUserStore();
    const user: User = { username: 'username' };
    expect(userStore.getCurrentUser).toBeUndefined();
    userStore.setCurrentUser(user);
    expect(userStore.getCurrentUser).toEqual(user);
  });
});
