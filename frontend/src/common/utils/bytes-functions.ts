import { i18n } from '@common/plugins/i18n.plugin';

export const bytesToString = (bytes: number, decimals = 2) => {
  const { t } = i18n.global;

  if (!+bytes) return t('ByteSize.bytes', { count: 0 });

  const sizes = [
    'ByteSize.bytes',
    'ByteSize.kiloBytes',
    'ByteSize.megaBytes',
    'ByteSize.gigaBytes',
    'ByteSize.teraBytes',
    'ByteSize.petaBytes',
    'ByteSize.exbiBytes',
    'ByteSize.zebiBytes',
    'ByteSize.yobioBytes',
  ];

  const base = 1024;
  const power = Math.floor(Math.log(bytes) / Math.log(base));
  const value = parseFloat((bytes / Math.pow(base, power)).toFixed(decimals < 0 ? 0 : decimals));

  return t(sizes[power], { count: value });
};
