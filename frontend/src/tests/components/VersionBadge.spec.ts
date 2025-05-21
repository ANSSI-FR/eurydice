import VersionBadge from '@common/components/VersionBadge.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe('VersionBadge.vue', () => {
  it('Displays an VersionBadge', () => {
    const wrapper = mount(VersionBadge);
    expect(wrapper.text()).toContain('test-version');
  });
});
