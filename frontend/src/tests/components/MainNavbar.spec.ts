import MainNavbar from '@common/components/MainNavbar.vue';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { useUserStore } from '@common/store/user.store';
import { router } from '@origin/router';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe('MainNavbar.vue', () => {
  it('Displays an MainNavbar', async () => {
    const username = 'toto';
    await useServerMetadataStore().fetchServerMetadata();
    useUserStore().setCurrentUser({ username: username });
    const wrapper = mount(MainNavbar, { global: { plugins: [router] } });
    expect(wrapper.findAll('[data-testid="MainNavbarHeader"]').length).toEqual(1);
    expect(wrapper.text()).toContain(username);
    expect(wrapper.text()).toContain('badgeContent');
  });
  it('Displays an MainNavbarHeader', async () => {
    await useServerMetadataStore().fetchServerMetadata();
    const wrapper = mount(MainNavbar, { global: { plugins: [router] } });
    expect(wrapper.findAll('[data-testid="MainNavbarHeader"]').length).toEqual(1);
    wrapper.find('[data-testid="MainNavbarHeader"]');

    const homeLink = wrapper.findAll('a');
    expect(homeLink.length).toEqual(1);
    expect(homeLink[0].attributes('href')).toEqual('/');

    expect(wrapper.text()).toContain('test-version');
    expect(wrapper.text()).toContain('badgeContent');
  });
});
