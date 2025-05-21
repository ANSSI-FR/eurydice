<template>
  <Dialog
    v-model:visible="isDeleteMultipleDialogVisible"
    :header="$t('TransferableDeleteMultipleDialog.title')"
    closable
    modal
    data-testid="TransferableDeleteMultipleDialog"
    class="w-xl"
  >
    <div class="flex flex-col gap-5">
      <p>
        {{
          $t('TransferableDeleteMultipleDialog.messageIntro', {
            count: selectedTransferables?.length ?? 0,
          })
        }}
      </p>

      <ul class="list-disc list-inside indent-2">
        <li v-for="file of selectedTransferables" :key="file.id">
          {{ file.name }}
        </li>
      </ul>

      <p>
        {{
          $t('TransferableDeleteMultipleDialog.messageQuestion', {
            count: selectedTransferables?.length ?? 0,
          })
        }}
      </p>
    </div>
    <template #footer>
      <MainButton
        severity="secondary"
        icon="pi pi-times"
        tkey="Actions.cancel"
        @click="
          () => {
            isDeleteMultipleDialogVisible = false;
          }
        "
        data-testid="TransferableDeleteMultipleDialog-cancelButton"
      />
      <MainButton
        icon="pi pi-trash"
        severity="danger"
        :label="$t('Actions.deleteSelected', { count: selectedTransferables?.length ?? 0 })"
        @click="deleteMultiple"
        data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"
        :loading="isDeleting"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import type { Transferable } from '@common/models/Transferable';
import { toastMessage } from '@common/services/toast-message.service';
import { deleteTransferable } from '@destination/services/transferables.service';
import { Dialog } from 'primevue';
import { computed, onUnmounted, ref } from 'vue';

const isDeleteMultipleDialogVisible = defineModel<boolean>();
const selectedTransferables = defineModel<Transferable[]>('selectedTransferables');
const stringOfFileNames = computed(() => {
  return selectedTransferables.value?.map((transferable) => transferable.name).join(', ');
});
const isDeleting = ref<boolean>(false);

const deleteMultiple = () => {
  isDeleting.value = true;
  const deletePromises = selectedTransferables.value
    ? selectedTransferables.value.map((transferable) => {
        return deleteTransferable(transferable.id).then(() => {
          transferable.state = 'REMOVED';
        });
      })
    : [];

  return Promise.all(deletePromises)
    .then(() => {
      toastMessage(
        'TransferableDeleteMultipleDialog.successMessageTitle',
        'TransferableDeleteMultipleDialog.successMessageMessage',
        'success',
        true,
        {
          paramsMessage: {
            files: stringOfFileNames.value,
            count: selectedTransferables.value?.length ?? 0,
          },
        },
      );
    })
    .finally(() => {
      isDeleting.value = false;
      isDeleteMultipleDialogVisible.value = false;
    });
};

onUnmounted(() => {
  isDeleting.value = false;
});
</script>
