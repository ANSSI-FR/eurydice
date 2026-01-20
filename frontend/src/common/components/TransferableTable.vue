<template>
  <DataTable
    :value="transferableList"
    class="w-full border rounded-(--p-content-border-radius) border-(--p-content-border-color)"
    scrollable
    v-model:selection="selectedTransferables"
    data-testid="TransferableTable"
    paginator
    :rows="pageSize"
    :totalRecords="totalRecords"
    lazy
    @page="onPageChange"
    :first="first"
  >
    <template #empty>
      <div class="flex w-full p-2 justify-center items-center">
        <span class="text-xl">{{ $t('TransferableTable.empty') }}</span>
      </div>
    </template>
    <template #header>
      <div class="flex justify-between items-center w-full gap-2 flex-wrap">
        <span class="text-xl"> {{ $t('TransferableTable.tableTitle') }}</span>
        <div class="flex justify-end items-center gap-2 flex-wrap">
          <slot name="header"></slot>
          <MainButton
            icon="pi pi-refresh"
            tkey="TransferableTable.refreshNewItems"
            @click="refreshNewItems"
            :isLoading="isRefreshLoading"
            data-testid="TransferableTable-refreshNewItemsButton"
          />
        </div>
      </div>
    </template>
    <Column
      selectionMode="multiple"
      headerStyle="width: 3rem"
      v-if="selectedTransferables !== undefined"
      frozen
      align-frozen="left"
    >
    </Column>
    <Column field="name" :header="$t('TransferableTable.name')">
      <template #body="{ data }">
        <div class="max-w-10 sm:max-w-20 md:max-w-full">
          <span class="truncate block">
            {{ decodeURI(data.name) }}
            <i
              class="pi pi-lock ml-2"
              v-if="data.userProvidedMeta.metadataEncrypted"
              v-tooltip="$t('TransferableTable.lockTooltip')"
            ></i>
          </span>
        </div>
      </template>
    </Column>
    <Column field="sha1" :header="$t('TransferableTable.sha1')">
      <template #body="{ data }">
        <div class="max-w-10 sm:max-w-20 md:max-w-full">
          <span class="truncate block" v-tooltip.bottom="data.sha1">
            {{ data.sha1 }}
          </span>
        </div>
      </template>
    </Column>
    <Column field="size" :header="$t('TransferableTable.size')">
      <template #body="{ data }">
        {{ bytesToString(data.size) }}
      </template>
    </Column>
    <Column field="state" :header="$t('TransferableTable.state')">
      <template #body="{ data }">
        <TransferableStateTag :state="data.state" :progress="data.progress" />
      </template>
    </Column>
    <Column field="createdAt" :header="$t('TransferableTable.createdAt')">
      <template #body="{ data }">
        <span v-tooltip.bottom="$d(Date.parse(data.createdAt), 'long')">{{
          $d(Date.parse(data.createdAt), 'short')
        }}</span>
      </template>
    </Column>
    <Column field="id" :header="$t('TransferableTable.actions')" frozen alignFrozen="right">
      <template #body="{ data }">
        <slot name="actionColumn" :data="data">
          <span data-testid="TransferableTable.noAction">-</span>
        </slot>
      </template>
    </Column>
  </DataTable>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import TransferableStateTag from '@common/components/TransferableStateTag.vue';
import type { TransferableListResponse } from '@common/models/TransferableListResponse';
import { refreshServerStatus } from '@common/services/status.service.ts';
import { listTransferables } from '@common/services/transferables.service';
import { bytesToString } from '@common/utils/bytes-functions';
import { Column, DataTable, type DataTablePageEvent } from 'primevue';
import { onMounted, ref } from 'vue';

const selectedTransferables = defineModel<Transferable[] | undefined>('selectedTransferables');

const transferableList = ref<Transferable[]>([]);
const totalRecords = ref<number>(0);
const delta = ref<number>(0);
const currentPage = ref<number>(0);
const currentPageId = ref<string>();
const pageSize = Number(import.meta.env.VITE_TRANSFERABLES_PER_PAGE ?? '100');
const first = ref<number>();
const newItems = ref<boolean>();
const isRefreshLoading = ref<boolean>(false);

const refreshTransferables = async (): Promise<TransferableListResponse> => {
  return listTransferables({
    pageSize: pageSize,
    from: currentPageId.value,
    delta: currentPageId.value ? delta.value : undefined,
  }).then((transferableListResponse: TransferableListResponse) => {
    if (transferableListResponse.newItems) {
      newItems.value = true;
    }
    currentPageId.value = transferableListResponse.pages.current;
    totalRecords.value = transferableListResponse.count;
    transferableList.value = transferableListResponse.results;
    delta.value = 0;
    return transferableListResponse;
  });
};

const syncWithBackend = async () => {
  isRefreshLoading.value = true;
  try {
    await refreshServerStatus();
    await refreshTransferables();
  } catch {
    isRefreshLoading.value = false;
  }
  isRefreshLoading.value = false;
};

const refreshNewItems = async () => {
  currentPage.value = 0;
  currentPageId.value = undefined;
  first.value = 0;
  newItems.value = false;
  syncWithBackend();
};

const onPageChange = async (pageChangeEvent: DataTablePageEvent) => {
  delta.value = pageChangeEvent.page - currentPage.value;
  currentPage.value = pageChangeEvent.page;
  first.value = pageChangeEvent.first;
  syncWithBackend();
};

onMounted(async () => {
  isRefreshLoading.value = true;
  await refreshTransferables();
  isRefreshLoading.value = false;
});
</script>

<style>
/* Note: This SCSS is present because Prime is not correctly supporting sticky columns for the moment...*/
.p-datatable-frozen-column {
  position: sticky;
}

.p-datatable-frozen-column {
  background-color: var(--p-datatable-row-background);
  border-collapse: separate;
}

table {
  border-collapse: separate;
  border-spacing: 0px;
}

.p-datatable-paginator-bottom {
  border-width: 0 !important;
}

.p-datatable-header {
  border-radius: var(--p-content-border-radius) var(--p-content-border-radius) 0 0;
}
</style>
