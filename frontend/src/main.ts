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

const eurydicePreset = definePreset(Aura, {
  semantic: {
    primary: palette('#01426a'),
    colorScheme: {
      light: { surface: palette('#01426a'), primary: palette('#01426a') },
      dark: { surface: palette('#3D505C'), primary: palette('#b9d9eb') },
    },
  },
});

// Init PrimeVue
app.use(PrimeVue, {
  theme: {
    preset: eurydicePreset,
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
