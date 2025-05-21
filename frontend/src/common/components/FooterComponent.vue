<template>
  <div class="flex flex-col gap-2">
    <ScrollToTopButton
      data-testid="Footer.scrollButton"
      class="pointer-events-auto"
    ></ScrollToTopButton>
    <div class="w-full grid grid-cols-2 gap-4 p-1" data-testid="Footer">
      <a
        :href="apiUrl"
        target="_blank"
        rel="noopener"
        data-testid="footer-api-docs"
        class="justify-self-end pointer-events-auto"
      >
        <MainButton
          severity="secondary"
          icon="pi pi-book"
          tkey="FooterComponent.documentationLinkText"
          class="shadow-lg shadow-(color:--p-content-hover) !bg-(--p-content-background) hover:!bg-(--p-content-hover-background)"
        />
      </a>
      <MainButton
        severity="secondary"
        data-testid="footer-contact"
        icon="pi pi-info-circle"
        tkey="FooterComponent.contactLinkText"
        class="justify-self-start shadow-lg shadow-(color:--p-content-hover) !bg-(--p-content-background) hover:!bg-(--p-content-hover-background) pointer-events-auto"
        @click="isDialogVisible = true"
      />
    </div>
  </div>
  <Dialog
    v-model:visible="isDialogVisible"
    :header="t('FooterComponent.contactLinkText')"
    modal
    closable
    class="w-sm"
    data-testid="footer-contact-dialog"
  >
    <p>
      {{
        $t('FooterComponent.contactText', {
          contactMethod: serverMetadataStore.getServerMetadata?.contact,
        })
      }}
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import ScrollToTopButton from '@common/components/ScrollToTopButton.vue';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { Dialog } from 'primevue';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const isDialogVisible = ref(false);
const apiUrl = import.meta.env.VITE_API_DOCS_URL ?? '/api/docs';
const serverMetadataStore = useServerMetadataStore();
</script>
