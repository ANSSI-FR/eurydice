import en_US from '@assets/i18n/en-US.json';
import fr_FR from '@assets/i18n/fr-FR.json';
import { createI18n } from 'vue-i18n';

export type MessageSchema = typeof en_US;

export const i18n = createI18n<[MessageSchema], 'en-US' | 'fr-FR'>({
  legacy: false,
  locale: 'fr-FR',
  messages: {
    'en-US': en_US,
    'fr-FR': fr_FR,
  },
  datetimeFormats: {
    'en-US': {
      short: {
        year: '2-digit',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short',
        hour: 'numeric',
        minute: 'numeric',
      },
    },
    'fr-FR': {
      short: {
        year: '2-digit',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short',
        hour: 'numeric',
        minute: 'numeric',
      },
    },
  },
});
