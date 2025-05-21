import apiClient from '@common/api/api-client';
import StatusBanner from '@common/components/StatusBanner.vue';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

const TEST_CASES = [
  {
    apiResponse: {
      maintenance: true,
      lastPacketSentAt: '2000-01-01T00:00:00.000000+01:00',
    },
    expected: {
      showMaintenance: true,
      showTimeout: true,
    },
  },
  {
    apiResponse: {
      maintenance: true,
      lastPacketSentAt: new Date(Date.now()).toUTCString(),
    },
    expected: {
      showMaintenance: true,
      showTimeout: false,
    },
  },
  {
    apiResponse: {
      maintenance: false,
      lastPacketSentAt: '2000-01-01T00:00:00.000000+01:00',
    },
    expected: {
      showMaintenance: false,
      showTimeout: true,
    },
  },
  {
    apiResponse: {
      maintenance: false,
      lastPacketSentAt: new Date(Date.now()).toUTCString(),
    },
    expected: {
      showMaintenance: false,
      showTimeout: false,
    },
  },
  {
    apiResponse: {
      lastPacketReceivedAt: new Date(Date.now()).toUTCString(),
    },
    expected: {
      showMaintenance: false,
      showTimeout: false,
    },
  },
  {
    apiResponse: {
      lastPacketReceivedAt: '2000-01-01T00:00:00.000000+01:00',
    },
    expected: {
      showMaintenance: false,
      showTimeout: true,
    },
  },
  {
    apiResponse: {
      lastPacketReceivedAt: '',
    },
    expected: {
      showMaintenance: false,
      showTimeout: true,
    },
  },
];

describe('StatusBanner.vue', () => {
  it('does not display a status banner', async () => {
    const wrapper = mount(StatusBanner);
    await flushPromises();
    expect(wrapper.findAll('[data-testid="StatusBanner.maintenanceMessage"]').length).toEqual(0);
    expect(wrapper.findAll('[data-testid="StatusBanner.serverTimeout"]').length).toEqual(0);
  });

  it.each(TEST_CASES)('for $apiResponse expect $expected', async ({ apiResponse, expected }) => {
    useServerMetadataStore().setServerMetadata({
      contact: 'TEST CONTACT',
      badgeColor: '',
      badgeContent: '',
    });
    const spyOnGetStatus = vi.spyOn(apiClient, 'get').mockImplementation(() => {
      return Promise.resolve(apiResponse);
    });
    const wrapper = mount(StatusBanner);
    await flushPromises();
    expect(wrapper.findAll('[data-testid="StatusBanner.maintenanceMessage"]').length).toEqual(
      expected.showMaintenance ? 1 : 0,
    );
    expect(wrapper.findAll('[data-testid="StatusBanner.serverTimeout"]').length).toEqual(
      expected.showTimeout ? 1 : 0,
    );
    expect(spyOnGetStatus).toBeCalled();
    if (expected.showTimeout) {
      const serverTimeoutMessage = wrapper.find('[data-testid="StatusBanner.serverTimeout"]');
      expect(serverTimeoutMessage.text()).toContain('TEST CONTACT');
    }
  });
});
