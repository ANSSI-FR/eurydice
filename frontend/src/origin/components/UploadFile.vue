<template>
  <FileUpload
    @uploader="uploadFiles"
    @uploadTest="uploadFiles"
    auto
    customUpload
    multiple
    id="fileUpload"
    :pt="{
      root: '!border-none',
    }"
    ref="uploader"
  >
    <template #header="{ chooseCallback }">
      <div class="flex justify-between items-center w-full gap-2">
        <span class="text-xl"> {{ $t('UploadFile.title') }}</span>

        <div class="flex w-full justify-end gap-2">
          <MainButton
            @click="clearUploadingFiles"
            icon="pi pi-eye-slash"
            tooltip-tkey="UploadFile.clearFilesButton"
            severity="secondary"
            data-testid="UploadFile.clearFilesButton"
            v-if="files.length > 0"
          />
          <MainButton
            @click="chooseCallback"
            icon="pi pi-plus"
            tkey="UploadFile.uploadFileButton"
            data-testid="UploadFile.uploadFileButton"
          />
        </div>
      </div>
    </template>
    <template #content>
      <div
        class="flex flex-col p-4 gap-4 w-full border-dashed border rounded bg-(--p-button-secondary-background)"
        @click="inputFile?.click"
      >
        <p
          class="text-xl md:text-4xl opacity-50 w-full text-center"
          v-if="files.length < 1"
          data-testid="UploadFile.emptyDragndropZone"
        >
          {{ $t('UploadFile.dragNDropMessage') }}
        </p>
        <div class="flex flex-wrap gap-2">
          <div v-for="file in files" :key="file.id">
            <UploadFileItem :file="file" @abortFileUpload="abortUpload" />
          </div>
        </div>
      </div>
      <div class="w-full justify-end flex">
        <span data-testid="UploadFile.total">
          {{ t('UploadFile.totalFiles', files.length) }} ({{
            bytesToString(files.reduce((acc: number, file: UploadingFile) => acc + file.size, 0))
          }})
        </span>
      </div>
    </template>
  </FileUpload>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import { toastMessage } from '@common/services/toast-message.service';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { bytesToString } from '@common/utils/bytes-functions';
import UploadFileItem from '@origin/components/UploadFileItem.vue';
import type { UploadingFile } from '@origin/models/UploadingFile';
import { createTransferable } from '@origin/services/transferables';
import { uniqueId } from 'lodash';
import { FileUpload, type FileUploadUploaderEvent } from 'primevue';
import { onMounted, reactive, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const metadataStore = useServerMetadataStore();

const files = ref<UploadingFile[]>([]);
const { t } = useI18n();
const uploader = useTemplateRef('uploader');
const inputFile = ref<HTMLElement | null>();

const uploadFiles = (event: FileUploadUploaderEvent): void => {
  // We convert the file in event to an array
  const eventFiles: File[] = Array.isArray(event.files) ? event.files : [event.files];

  eventFiles.forEach((fileData: File) => {
    // We construct a reactive UploadingFile
    const file: UploadingFile = reactive({
      id: uniqueId(),
      name: fileData.name,
      size: fileData.size,
      progress: 0,
      status: 'uploading',
      onUploadProgress: (progress: number) => {
        file.progress = progress;
      },
      abortController: new AbortController(),
    });
    files.value.push(file);
    // This is a tweak because of a "fix" in primevue : https://github.com/primefaces/primevue/commit/85a7ad3f53d3c53df0b3108b66cdbb7fbcd229c5
    // Files were uploaded in double after Primevue update
    //@ts-expect-error Clear is not recognized as a method
    uploader.value.clear();
    createTransferable(
      fileData,
      metadataStore.getServerMetadata?.encryptionEnabled ?? false,
      file.onUploadProgress,
      file.abortController.signal,
    )
      .then(() => {
        onUploadSuccess(file);
      })
      .catch(() => {
        if (file.status !== 'aborted') {
          onUploadFail(file);
        }
      });
  });
};

const onUploadSuccess = (file: UploadingFile) => {
  file.progress = 100;
  file.status = 'uploaded';
  toastMessage(
    'UploadFile.successToast.title',
    'UploadFile.successToast.message',
    'success',
    true,
    {
      paramsMessage: { fileName: file.name },
    },
  );
};

const onUploadFail = (file: UploadingFile) => {
  file.status = 'error';
};

const abortUpload = (file: UploadingFile) => {
  file.status = 'aborted';
  file.abortController.abort();
};

const clearUploadingFiles = () => {
  files.value = files.value.filter((file: UploadingFile) => file.status === 'uploading');
};

onMounted(() => {
  // We try to get the DOM Element for file input in order to click on in from the Drag n Drop Zone
  // warn : it is only working if there is only one input type file in the fileUpload...
  for (const item of document.querySelectorAll('#fileUpload input')) {
    if (item.attributes.getNamedItem('type')?.value === 'file' && item instanceof HTMLElement) {
      inputFile.value = item;
      break;
    }
  }
});
</script>
