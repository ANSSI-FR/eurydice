import { fileURLToPath } from 'node:url';
import { configDefaults, defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      setupFiles: ['vitest.setup.ts'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      alias: {
        '@tests': fileURLToPath(new URL('./src/tests', import.meta.url)),
      },
      coverage: {
        provider: 'v8',
        reporter: ['cobertura', 'html', 'text', 'text-summary'],
        include: ['src/**'],
        reportsDirectory: 'test-reports/coverage',
      },
      reporters: ['default', 'junit'],
      outputFile: 'test-reports/junit.xml',
    },
  }),
);
