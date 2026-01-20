<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import { deleteApiToken, getApiToken } from '@common/services/api-token.service';
import { toastMessage } from '@common/services/toast-message.service';
import { Password } from 'primevue';
import { onMounted, ref } from 'vue';

const tokenValue = ref('');
const isTokenCopied = ref(false);

const copyToken = async () => {
  await navigator.clipboard.writeText(tokenValue.value);
  toastMessage(
    'ApiTokenDialog.successToast.title',
    'ApiTokenDialog.successToast.message',
    'success',
  );
  isTokenCopied.value = true;
};

const onRefreshToken = async () => {
  const tokenJson = await deleteApiToken();
  tokenValue.value = tokenJson.token;
};

onMounted(async () => {
  const tokenJson = await getApiToken();
  tokenValue.value = tokenJson.token;
});
</script>
<template>
  <div class="flex flex-row gap-2">
    <Password v-model="tokenValue" disabled toggleMask />
    <MainButton
      @click="copyToken"
      tkey="ApiTokenDialog.copyBtn"
      :icon="isTokenCopied ? 'pi pi-check' : 'pi pi-clone'"
    />
    <MainButton :icon="'pi pi-refresh'" tkey="ApiTokenDialog.initBtn" @click="onRefreshToken" />
  </div>
</template>
