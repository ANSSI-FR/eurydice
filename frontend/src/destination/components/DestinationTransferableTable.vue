<template>
  <TransferableTable v-model:selectedTransferables="selectedTransferables">
    <template #header>
      <Button
        icon="pi pi-trash"
        severity="danger"
        v-tooltip.bottom="$t('Actions.deleteSelected')"
        v-if="listOfDeletableFiles.length > 0"
        @click="
          () => {
            isDeleteMultipleDialogVisible = true;
          }
        "
        rounded
        data-testid="DestinationTransferableTable-deleteMultipleButton"
      />
      <MainButton
        icon="pi pi-trash"
        severity="danger"
        tkey="Actions.deleteAll"
        @click="
          () => {
            isDeleteAllDialogVisible = true;
          }
        "
        data-testid="DestinationTransferableTable-deleteAllButton"
      />
    </template>
    <template #actionColumn="{ data }">
      <div class="flex gap-2" v-if="data.state === 'SUCCESS'">
        <a
          :href="`${API_URL}/transferables/${data.id}/download`"
          download
          data-testid="TransferableTable-DownloadButton"
        >
          <Button icon="pi pi-download" rounded severity="secondary" />
        </a>
        <Button
          icon="pi pi-eye"
          @click="previewItem(data)"
          rounded
          severity="secondary"
          :disabled="isPreviewDisabled(data)"
          v-tooltip.left="
            isPreviewDisabled(data)
              ? $t('TransferableTable.previewTooltip', { nbMio: MAX_PREVIEW_MIO })
              : ''
          "
          data-testid="DestinationTransferableTable-previewButton"
        />
        <Button
          icon="pi pi-trash"
          rounded
          severity="secondary"
          @click="() => deleteItem(data)"
          data-testid="DestinationTransferableTable-deleteSingleItemButton"
        />
      </div>
    </template>
  </TransferableTable>
  <DeleteAllDialog v-model="isDeleteAllDialogVisible" />
  <DeleteMultipleDialog
    v-model="isDeleteMultipleDialogVisible"
    v-model:selectedTransferables="listOfDeletableFiles"
  />
  <DeleteMultipleDialog
    v-model="isDeleteOneTransferableDialogVisible"
    v-model:selectedTransferables="itemToDelete"
  />
  <PreviewDialog v-model:transferable="itemToPreview" v-model="isPreviewDialogVisible" />
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import TransferableTable from '@common/components/TransferableTable.vue';
import type { Transferable } from '@common/models/Transferable';
import DeleteAllDialog from '@destination/components/DeleteAllDialog.vue';
import DeleteMultipleDialog from '@destination/components/DeleteMultipleDialog.vue';
import PreviewDialog from '@destination/components/PreviewDialog.vue';
import { Button } from 'primevue';
import { computed, ref, watch } from 'vue';

const selectedTransferables = ref<Transferable[]>([]);
const isDeleteAllDialogVisible = ref<boolean>(false);
const isDeleteMultipleDialogVisible = ref<boolean>(false);
const isDeleteOneTransferableDialogVisible = ref<boolean>(false);
const itemToDelete = ref<[Transferable]>();
const isPreviewDialogVisible = ref<boolean>(false);
const itemToPreview = ref<Transferable>();
const MAX_PREVIEW_MIO = Number(import.meta.env.VITE_PREVIEW_MAX_MIO ?? '1');

const listOfDeletableFiles = computed(() => {
  return selectedTransferables.value?.filter((file) => file.state === 'SUCCESS');
});

const deleteItem = (transferable: Transferable) => {
  itemToDelete.value = [transferable];
  isDeleteOneTransferableDialogVisible.value = true;
};

watch(isDeleteMultipleDialogVisible, (newValue, oldValue) => {
  if (!newValue && oldValue) {
    selectedTransferables.value = [];
  }
});

watch(isDeleteAllDialogVisible, () => {
  selectedTransferables.value = [];
});

watch(isDeleteOneTransferableDialogVisible, () => {
  selectedTransferables.value = [];
});

const previewItem = (transferable: Transferable) => {
  itemToPreview.value = transferable;
  isPreviewDialogVisible.value = true;
};

const isPreviewDisabled = (transferable: Transferable) => {
  if (transferable) {
    const extensions = ['txt', 'md', 'json', 'xml'];
    const parts = transferable.name ? transferable.name.split('.') : [];
    const MIO = 1048576;
    if (
      parts.length > 1 &&
      extensions.includes(parts[parts.length - 1]!.toLowerCase()) &&
      transferable.size &&
      transferable.size < MAX_PREVIEW_MIO * MIO
    ) {
      return false;
    }
  }
  return true;
};

const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1';
</script>
