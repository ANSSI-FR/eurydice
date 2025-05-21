import DefaultLayout from '@common/layouts/DefaultLayout.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe.concurrent('Default Layout', () => {
  it('Contains a header, a main and a footer', async () => {
    // We mount DefaultLayout without content
    const wrapper = mount(DefaultLayout);

    expect(wrapper.find('header').exists()).toBe(true);
    expect(wrapper.find('main').exists()).toBe(true);
    expect(wrapper.find('footer').exists()).toBe(true);
  });
  it('Default placeholders are Skeleton objects', () => {
    // We mount DefaultLayout without content
    const wrapper = mount(DefaultLayout);
    // We expect Skeletons to be displayed by default
    expect(wrapper.find('header').find('.p-skeleton').exists()).toBe(true);
    expect(wrapper.find('main').find('.p-skeleton').exists()).toBe(true);
    expect(wrapper.find('footer').find('.p-skeleton').exists()).toBe(true);
  });
  it('Slots are working', () => {
    const wrapper = mount(DefaultLayout, {
      slots: {
        navbar: 'Navbar Content',
        main: 'Main Content',
        footer: 'Footer Content',
      },
    });

    expect(wrapper.find('header').text()).toContain('Navbar Content');
    expect(wrapper.find('main').text()).toContain('Main Content');
    expect(wrapper.find('footer').text()).toContain('Footer Content');
  });
});
