import { fileURLToPath, URL } from 'node:url';

import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import vueDevTools from 'vite-plugin-vue-devtools';

const PERMISSIONS_POLICY =
  'accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=(), interest-cohort=()';

// NOTE: script-src unsafe-eval should NOT be set in production
// NOTE: some content security policy are set for VueTools plugin
const CONTENT_SECURITY_POLICY =
  "default-src 'none' 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src https://fonts.gstatic.com 'self'; img-src data: 'self'; connect-src 'self'; frame-ancestors 'none' 'self'";

const REFERRER_POLICY = 'same-origin';

const X_CONTENT_TYPE_OPTIONS = 'nosniff';

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@origin': fileURLToPath(new URL('./src/origin', import.meta.url)),
      '@destination': fileURLToPath(new URL('./src/destination', import.meta.url)),
      '@common': fileURLToPath(new URL('./src/common', import.meta.url)),
      '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: Number(process.env.VITE_PORT || 8080),
    strictPort: true,
    allowedHosts: ['origin.test', 'destination.test'],
    headers: {
      // NOTE: this is only for the development environment, production headers
      //       should be set in the production webserver's configuration
      'Permissions-Policy': PERMISSIONS_POLICY,
      'Content-Security-Policy': CONTENT_SECURITY_POLICY,
      'Referrer-Policy': REFERRER_POLICY,
      'X-Content-Type-Options': X_CONTENT_TYPE_OPTIONS,
    },
  },
  build: {
    outDir: process.env['VITE_EURYDICE_GUICHET'] === 'origin' ? 'dist/origin' : 'dist/destination',
  },
  envPrefix: ['EURYDICE_', 'VITE_'],
});
