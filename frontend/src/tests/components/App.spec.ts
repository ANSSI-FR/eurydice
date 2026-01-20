import App from '@common/App.vue';
import * as serverMetadataService from '@common/services/server-metadata.service';
import { useUserStore } from '@common/store/user.store';
import { router } from '@origin/router';
import { flushPromises, mount, shallowMount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('App.vue', () => {
  it('Displays a ToastMessage when calling toastMessage', () => {
    const wrapper = shallowMount(App);
    expect(wrapper.find('[data-testid="Toast"]').exists()).toBeTruthy();
  });
  it('Calls server metadata endpoint', async () => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    const spyOnServerMetadata = vi.spyOn(serverMetadataService, 'getServerMetadata');
    mount(App, { global: { plugins: [router] } });
    await flushPromises();
    expect(spyOnServerMetadata).toBeCalledTimes(1);
    expect(document.title).toEqual('badgeContent');
  });
});
