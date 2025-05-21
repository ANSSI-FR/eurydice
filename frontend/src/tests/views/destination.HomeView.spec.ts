import { router } from '@destination/router';
import MainView from '@destination/views/MainView.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe.concurrent('Main View Destination', () => {
  it('Contains a header, a main and a footer', async () => {
    // We mount destination MainView without content
    const wrapper = mount(MainView, { global: { plugins: [router] } });

    expect(wrapper.find('header').exists()).toBe(true);
    expect(wrapper.find('main').exists()).toBe(true);
    expect(wrapper.find('footer').exists()).toBe(true);
  });
});
