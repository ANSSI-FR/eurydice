<template>
  <div class="flex flex-col gap-4 p-5">
    <div class="flex justify-between">
      <span class="text-xl">{{ $t('UploadText.title') }}</span>
      <MainButton
        icon="pi pi-upload"
        tkey="UploadText.uploadTextButton"
        @click="uploadText"
        :loading="fileUpload?.status === 'uploading'"
        :disabled="textInput === undefined"
        type="submit"
        data-testid="UploadText-sendButton"
      />
    </div>
    <Textarea
      rows="5"
      cols="30"
      class="w-full"
      v-model="textInput"
      data-testid="UploadText-textArea"
    />
    <Message
      severity="error"
      v-if="fileUpload?.status === 'aborted'"
      closable
      data-testid="UploadText-errorMessage"
    >
      {{ $t('UploadText.abortErrorMessage') }}
    </Message>
  </div>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import { toastMessage } from '@common/services/toast-message.service';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { getDateSuffix } from '@common/utils/date-functions';
import type { UploadingFile } from '@origin/models/UploadingFile';
import { createTransferable } from '@origin/services/transferables';
import { uniqueId } from 'lodash';
import { Message, Textarea } from 'primevue';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const metadataStore = useServerMetadataStore();

const fileUpload = ref<UploadingFile>();
const { t } = useI18n();
const textInput = ref<string | undefined>();

const uploadText = (): void => {
  if (textInput.value) {
    const fileData = new File(
      [textInput.value],
      t('UploadText.defaultFileName', {
        dateSuffix: getDateSuffix(),
      }),
    );
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
    fileUpload.value = file;
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
        onUploadFail(file);
      });
  }
};

const onUploadSuccess = (file: UploadingFile) => {
  textInput.value = undefined;
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
  file.abortController.abort();
  file.status = 'aborted';
};
</script>
