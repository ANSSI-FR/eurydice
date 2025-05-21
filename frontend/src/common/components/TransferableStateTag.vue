<template>
  <Tag
    :value="stateToTag[state].value"
    :severity="stateToTag[state].severity"
    :icon="stateToTag[state].icon"
    v-tooltip.bottom="stateToTag[state].tooltip"
    data-testid="TransferableStateTag"
    v-if="stateToTag[state]"
  >
    <div class="flex flex-col gap-2 items-center md:flex-row">
      {{ stateToTag[state].value }}
      <ProgressBar
        :value="progress"
        :show-value="false"
        class="!h-[0.25rem] w-20"
        v-tooltip.bottom="`${progress}%`"
        v-if="progress && state === 'ONGOING'"
      >
      </ProgressBar>
    </div>
  </Tag>
</template>

<script setup lang="ts">
import { ProgressBar, Tag } from 'primevue';
import { useI18n } from 'vue-i18n';

const { state, progress } = defineProps<{ state: TransferableState; progress: number }>();
const { t } = useI18n();

const stateToTag: Record<
  TransferableState,
  {
    value: string;
    severity: 'success' | 'warn' | 'secondary' | 'info' | 'danger';
    icon: string;
    tooltip: string;
  }
> = {
  PENDING: {
    value: t('TransferableState.pending'),
    severity: 'secondary',
    icon: 'pi pi-stopwatch',
    tooltip: t('TransferableState.pendingExplanation'),
  },
  ONGOING: {
    value: t('TransferableState.ongoing'),
    severity: 'info',
    icon: 'pi pi-spinner pi-spin',
    tooltip: t('TransferableState.ongoingExplanation'),
  },
  ERROR: {
    value: t('TransferableState.error'),
    severity: 'danger',
    icon: 'pi pi-exclamation-triangle',
    tooltip: t('TransferableState.errorExplanation'),
  },
  CANCELED: {
    value: t('TransferableState.canceled'),
    severity: 'warn',
    icon: 'pi pi-info-circle',
    tooltip: t('TransferableState.canceledExplanation'),
  },
  SUCCESS: {
    value: t('TransferableState.success'),
    severity: 'success',
    icon: 'pi pi-check-circle',
    tooltip: t('TransferableState.successExplanation'),
  },
  EXPIRED: {
    value: t('TransferableState.expired'),
    severity: 'secondary',
    icon: 'pi pi-hourglass',
    tooltip: t('TransferableState.expiredExplanation'),
  },
  REVOKED: {
    value: t('TransferableState.revoked'),
    severity: 'danger',
    icon: 'pi pi-times-circle',
    tooltip: t('TransferableState.revokedExplanation'),
  },
  REMOVED: {
    value: t('TransferableState.removed'),
    severity: 'warn',
    icon: 'pi pi-trash',
    tooltip: t('TransferableState.removedExplanation'),
  },
};
</script>
