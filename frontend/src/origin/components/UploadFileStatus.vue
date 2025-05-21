<template>
  <Tag
    rounded
    :icon="statusToIconSeverityAndValue[status].icon"
    :severity="statusToIconSeverityAndValue[status].severity"
    :value="$t(statusToIconSeverityAndValue[status].tkey, { progress })"
  />
</template>

<script setup lang="ts">
import type { UploadingFile } from '@origin/models/UploadingFile';
import { Tag } from 'primevue';

const { status, progress } = defineProps<{ status: UploadingFile['status']; progress: number }>();

const statusToIconSeverityAndValue: {
  [key in UploadingFile['status']]: {
    tkey: string;
    icon: string;
    severity: 'warn' | 'danger' | 'success' | 'info';
  };
} = {
  error: {
    icon: 'pi pi-times-circle',
    tkey: 'UploadFile.status.error',
    severity: 'danger',
  },
  aborted: {
    icon: 'pi pi-exclamation-triangle',
    tkey: 'UploadFile.status.aborted',
    severity: 'warn',
  },
  uploaded: {
    icon: 'pi pi-check',
    tkey: 'UploadFile.status.uploaded',
    severity: 'success',
  },
  uploading: {
    icon: 'pi pi-spinner pi-spin',
    tkey: 'UploadFile.status.uploading',
    severity: 'info',
  },
};
</script>
