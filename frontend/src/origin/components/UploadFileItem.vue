<template>
  <div
    class="bg-(--p-button-secondary-hover-background) card flex flex-col items-center gap-2 p-2 w-[10rem] rounded"
    data-testid="UploadFileItem"
  >
    <span
      class="font-semibold text-ellipsis max-w-full whitespace-nowrap overflow-hidden"
      data-testid="UploadFileItem.name"
    >
      {{ file.name }}
    </span>
    <UploadFileStatus :status="file.status" :progress="file.progress" />
    <div v-if="file.status === 'uploading'" class="flex items-center gap-2 w-full">
      <ProgressBar :value="file.progress" :showValue="false" class="w-full" />
      <i
        @click="
          (e) => {
            e.stopPropagation();
            $emit('abortFileUpload', file);
          }
        "
        class="pi pi-times !text-xs"
        severity="danger"
        v-tooltip.bottom="$t('UploadFile.abortFileUpload')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import UploadFileStatus from '@origin/components/UploadFileStatus.vue';
import type { UploadingFile } from '@origin/models/UploadingFile';
import { ProgressBar } from 'primevue';

const { file } = defineProps<{ file: UploadingFile }>();

defineEmits(['abortFileUpload']);
</script>
