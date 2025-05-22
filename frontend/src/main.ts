import '@assets/main.css';

import { createApp } from 'vue';

import { createPinia } from 'pinia';

import { i18n } from '@common/plugins/i18n.plugin';

import Aura from '@primeuix/themes/aura';
import { DialogService, ToastService, Tooltip } from 'primevue';
import PrimeVue from 'primevue/config';

import App from '@common/App.vue';
import { definePreset, palette } from '@primeuix/themes';

const app = createApp(App);

// Init Pinia
app.use(createPinia());

const darkPalette = {
  50: '#fcfdfe',
  100: '#eef6fa',
  200: '#e1eff6',
  300: '#d4e7f3',
  400: '#c6e0ef',
  500: '#3d505c',
  600: '#34444e',
  700: '#2b3840',
  800: '#222c33',
  900: '#182025',
  950: '#0f1417',
};

const eurydicePreset = definePreset(Aura, {
  semantic: {
    primary: palette('#01426a'),
    colorScheme: {
      light: { surface: palette('#01426a'), primary: palette('#01426a') },
      dark: {
        surface: darkPalette,
        primary: darkPalette,
      },
    },
  },
});

// Init PrimeVue
app.use(PrimeVue, {
  theme: {
    preset: eurydicePreset,
    options: {
      darkModeSelector: '.dark',
    },
  },
});
app.use(ToastService);
app.directive('tooltip', Tooltip);
app.use(DialogService);

// Init i18n for translation
app.use(i18n);

// Separate origin from destination
if (import.meta.env.VITE_EURYDICE_GUICHET === 'origin') {
  import('@origin/router').then(({ router }) => {
    app.use(router);
    app.mount('#app');
  });
} else {
  import('@destination/router').then(({ router }) => {
    app.use(router);
    app.mount('#app');
  });
}
