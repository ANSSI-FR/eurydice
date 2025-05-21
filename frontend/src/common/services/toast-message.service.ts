//@ts-expect-error toasteventbus doesn't support TS
import toasteventbus from 'primevue/toasteventbus';

import { i18n } from '@common/plugins/i18n.plugin';

const t = i18n.global.t;

export const toastMessage = (
  titleTranslationKey: string | null = null,
  messageTranslationKey: string | null = null,
  severity: 'error' | 'info' | 'warn' | 'success' = 'info',
  autoExpires: boolean = true,
  options?: {
    paramsTitle?: any;
    paramsMessage?: any;
  },
) => {
  toasteventbus.emit('add', {
    severity: severity,
    summary: titleTranslationKey !== null ? t(titleTranslationKey, options?.paramsTitle) : null,
    detail:
      messageTranslationKey !== null ? t(messageTranslationKey, options?.paramsMessage) : null,
    life: autoExpires ? parseInt(import.meta.env.VITE_TOAST_MESSAGE_LIFETIME) : undefined,
    closable: true,
  });
};
