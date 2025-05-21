import * as serverMetadataService from '@common/services/server-metadata.service';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useServerMetadataStore = defineStore('serverMetadataStore', () => {
  const serverMetadata = ref<ServerMetadata>();

  const getServerMetadata = computed(() => serverMetadata.value);
  const setServerMetadata = (metadata: ServerMetadata | undefined) => {
    serverMetadata.value = metadata;
  };
  const fetchServerMetadata = async () => {
    await serverMetadataService.getServerMetadata().then((fetchedServerMetadata) => {
      setServerMetadata(fetchedServerMetadata);
    });
  };
  const $reset = () => {
    serverMetadata.value = undefined;
  };
  return {
    getServerMetadata,
    setServerMetadata,
    fetchServerMetadata,
    $reset,
  };
});
