import { toastMessage } from '@common/services/toast-message.service';
import { describe } from 'node:test';
import { ToastEventBus } from 'primevue';
import { expect, it, vi } from 'vitest';

const TEST_CASES = [
  {
    params: {
      title: 'Error.404.title',
      message: 'Error.404.message',
      severity: 'error' as 'error' | 'info',
      autoExpires: true,
    },
    expectedParams: {
      closable: true,
      detail: "Cette ressource n'existe pas.",
      life: 5000,
      severity: 'error' as 'error' | 'info',
      summary: 'Page non trouvée',
    },
  },
  {
    params: { title: null, message: null, autoExpires: false },
    expectedParams: {
      closable: true,
      detail: null,
      life: undefined,
      severity: 'info' as 'error' | 'info',
      summary: null,
    },
  },
];

describe('toast-message service', () => {
  it.each(TEST_CASES)(
    'expects $params to be sent as $expectedParams in ToastEventBus',
    ({ params, expectedParams }) => {
      const spyOnToastEventBus = vi.spyOn(ToastEventBus, 'emit').mockImplementation(vi.fn());
      toastMessage(params.title, params.message, params.severity, params.autoExpires);
      expect(spyOnToastEventBus).toHaveBeenCalledWith('add', expectedParams);
    },
  );
});
