//import { i18n } from '@/plugins/i18n.config';
import { i18n } from '@common/plugins/i18n.plugin';
import SodiumTools from '@origin/utils/sodiumTools';
import { handlers } from '@tests/mocks/server/handlers';
import { config } from '@vue/test-utils';
import 'blob-polyfill';
import _sodium from 'libsodium-wrappers';
import { setupServer } from 'msw/node';
import { createPinia, setActivePinia } from 'pinia';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';
import ResizeObserver from 'resize-observer-polyfill';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';

global.Blob = Blob; // from blob-polyfill, reading a Blob content in jsdom isn't possible by default
global.ResizeObserver = ResizeObserver;

config.global.plugins = [PrimeVue, ToastService, i18n];
config.global.provide = [ToastService];
config.global.directives = { tooltip: Tooltip };

setActivePinia(createPinia());

const server = setupServer(...handlers);

// Start server before all tests
beforeAll(async () => {
  server.listen({ onUnhandledRequest: 'error' });
  // Init Sodium
  await _sodium.ready;
  new SodiumTools(_sodium, 'gtC32LH1n6qCbkqQog/QwAr7TjxuED2+85o1CRlSl2Y=');
});

// Close server after all tests
afterAll(() => {
  server.close();
  vi.clearAllMocks();
  vi.unstubAllEnvs();
});

// Reset handlers after each test for test isolation
afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

// Some components use window.matchMedia internally, which is not defined by default in Vitest
// To fix "matchMedia is not a function" error :
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  enumerable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
