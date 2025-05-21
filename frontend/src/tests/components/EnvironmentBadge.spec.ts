import EnvironmentBadge from '@common/components/EnvironmentBadge.vue';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe('EnvironmentBadge.vue', () => {
  it('Displays an EnvironmentBadge', () => {
    const serverMetadata = {
      badgeColor: '#FF0000',
      badgeContent: 'badgeContentTest',
      contact: 'watever',
    };
    const serverMetadataStore = useServerMetadataStore();
    serverMetadataStore.setServerMetadata(serverMetadata);
    const wrapper = mount(EnvironmentBadge);
    expect(wrapper.isVisible()).toBeTruthy();
    expect(wrapper.text()).toContain(serverMetadata.badgeContent);
    expect(wrapper.attributes('style')).toEqual('background-color: rgb(255, 0, 0);');
  });
});
