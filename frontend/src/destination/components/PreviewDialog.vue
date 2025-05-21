<template>
  <Dialog
    class="w-xl"
    v-model:visible="showPreviewDialog"
    data-testid="TransferablePreviewDialog"
    :header="transferable?.name ? transferable.name : ''"
    modal
    closable
  >
    <Textarea
      v-if="fileContent"
      :value="fileContent"
      class="w-full mt-1"
      auto-resize
      variant="outlined"
    />
    <Skeleton v-if="!fileContent" height="10vh" />
    <template #footer>
      <div class="flex items-center gap-4">
        <MainButton
          icon="pi pi-times"
          tkey="TransferablePreviewDialog.close"
          @click="closeCallback()"
          severity="secondary"
        />
        <MainButton
          icon="pi pi-clone"
          tkey="TransferablePreviewDialog.copyAndClose"
          @click="closeCallback(true)"
          data-testid="PreviewDialog_copyAndCloseBtn"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import type { Transferable } from '@common/models/Transferable';
import { toastMessage } from '@common/services/toast-message.service';
import { getTransferableData } from '@destination/services/transferables.service';
import { Dialog, Skeleton, Textarea } from 'primevue';
import { onMounted, ref, watch } from 'vue';

const transferable = defineModel<Transferable>('transferable');
const showPreviewDialog = defineModel<boolean>();
const fileContent = ref<string>();

onMounted(async () => {
  if (transferable.value) {
    fileContent.value = await getTransferableData(transferable.value.id);
  }
});

watch(transferable, async (transferable) => {
  if (transferable) {
    fileContent.value = await getTransferableData(transferable.id);
  } else {
    fileContent.value = undefined;
  }
});

const closeCallback = (copy = false) => {
  if (copy && fileContent.value) {
    navigator.clipboard.writeText(fileContent.value);
    toastMessage(
      'TransferablePreviewDialog.copyMessage.title',
      'TransferablePreviewDialog.copyMessage.message',
      'success',
      true,
    );
  }
  transferable.value = undefined;
  showPreviewDialog.value = false;
};
</script>
