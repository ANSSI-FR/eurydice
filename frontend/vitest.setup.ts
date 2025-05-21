//import { i18n } from '@/plugins/i18n.config';
import { i18n } from '@common/plugins/i18n.plugin';
import { handlers } from '@tests/mocks/server/handlers';
import { config } from '@vue/test-utils';
import { setupServer } from 'msw/node';
import { createPinia, setActivePinia } from 'pinia';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';
import ResizeObserver from 'resize-observer-polyfill';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';
global.ResizeObserver = ResizeObserver;

config.global.plugins = [PrimeVue, ToastService, i18n];
config.global.provide = [ToastService];
config.global.directives = { tooltip: Tooltip };

setActivePinia(createPinia());

const server = setupServer(...handlers);

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

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
