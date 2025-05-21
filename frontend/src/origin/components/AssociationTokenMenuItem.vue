<template>
  <MainButton
    severity="secondary"
    @click="isDialogVisible = true"
    data-testid="menubar-token-btn"
    icon="pi pi-link"
    tkey="MainNavBar.AssociationToken.menuBtn"
  />
  <Dialog
    v-model:visible="isDialogVisible"
    modal
    closable
    class="w-xl"
    :header="$t('MainNavBar.AssociationToken.dialogHeader')"
  >
    <div class="flex flex-col gap-5">
      <p>{{ $t('MainNavBar.AssociationToken.dialogContent') }}</p>
      <div class="flex flex-col gap-1">
        <Textarea id="token" auto-resize class="w-full" :value="associationToken" />
        <Message severity="info" size="small" variant="simple" icon="pi pi-info-circle">
          {{ $t('MainNavBar.AssociationToken.expirationInfo') }}
        </Message>
        <Message severity="info" size="small" variant="simple" icon="pi pi-info-circle">
          {{ $t('MainNavBar.AssociationToken.capsInfo') }}
        </Message>
      </div>
    </div>
    <template #footer>
      <MainButton
        :label="t('MainNavBar.AssociationToken.closeButton')"
        severity="secondary"
        @click="isDialogVisible = false"
        icon="pi pi-times"
        autofocus
      />
      <MainButton
        @click="copyToken"
        data-testid="AssociationToken_copyBtn"
        tkey="MainNavBar.AssociationToken.copyBtn"
        :icon="isTokenCopied ? 'pi pi-check' : 'pi pi-clone'"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import { getAssociationToken } from '@common/services/association.service';
import { toastMessage } from '@common/services/toast-message.service';
import { Dialog, Message, Textarea } from 'primevue';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const isDialogVisible = ref(false);
const associationToken = ref('');
const isTokenCopied = ref(false);

const copyToken = async () => {
  await navigator.clipboard.writeText(associationToken.value);
  toastMessage(
    'MainNavBar.AssociationToken.successToast.title',
    'MainNavBar.AssociationToken.successToast.message',
    'success',
  );
  isTokenCopied.value = true;
};

onMounted(async () => {
  getAssociationToken()
    .then((response) => (associationToken.value = response.token))
    .catch((error) => (associationToken.value = error));
});
</script>
