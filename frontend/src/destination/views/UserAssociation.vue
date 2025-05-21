<template>
  <DefaultLayout>
    <template #navbar><MainNavbar /></template>
    <template #main>
      <div class="flex justify-center items-center p-10 sm:p-20">
        <Panel :header="t('UserAssociationView.header')" class="max-w-[600px]">
          <div class="flex flex-col gap-4 size-full">
            <p v-for="info in $t('UserAssociationView.content.infos').split('\n')" :key="info">
              {{ info }}
            </p>
            <ol class="list-decimal list-inside indent-2">
              <li v-for="step in $t('UserAssociationView.content.steps').split('\n')" :key="step">
                {{ step }}
              </li>
            </ol>
            <form data-testid="TokenForm" @submit.prevent="handleUserAssociation" class="flex-col">
              <Textarea
                valid
                class="w-full"
                v-model="token"
                autoResize
                rows="5"
                cols="30"
                data-testid="TokenTextArea"
                placeholder="Jeton d'association"
                :invalid="!valid"
                @input="isTokenValid"
              ></Textarea>
              <Message
                v-if="errorMsg"
                data-testid="TokenErrorMsg"
                severity="error"
                size="small"
                variant="simple"
                icon="pi pi-exclamation-triangle"
              >
                {{ errorMsg }}
              </Message>
              <Message
                v-if="infoMsg"
                data-testid="TokenSuccessMsg"
                severity="success"
                size="small"
                variant="simple"
              >
                {{ infoMsg }}
              </Message>
              <Message severity="info" size="small" variant="simple" icon="pi pi-info-circle">
                {{ $t('UserAssociationView.content.helpMsg') }}
              </Message>
              <div class="w-full flex justify-end gap-2 pt-10">
                <MainButton
                  v-if="!isTokenVerified"
                  :disabled="!valid"
                  type="submit"
                  data-testid="AssociationBtn"
                  icon="pi pi-link"
                  tkey="UserAssociationView.associateButton"
                />
                <RouterLink :to="{ name: 'home' }">
                  <MainButton
                    v-if="isTokenVerified"
                    data-testid="ContinueBtn"
                    icon="pi pi-arrow-right"
                    tkey="UserAssociationView.continueButton"
                  />
                </RouterLink>
              </div>
            </form>
          </div>
        </Panel>
      </div>
    </template>
    <template #footer><FooterComponent /></template>
  </DefaultLayout>
</template>

<script setup lang="ts">
import FooterComponent from '@common/components/FooterComponent.vue';
import MainButton from '@common/components/MainButton.vue';
import MainNavbar from '@common/components/MainNavbar.vue';
import DefaultLayout from '@common/layouts/DefaultLayout.vue';
import { validateAssociationToken } from '@common/services/association.service';
import { Message } from 'primevue';
import Panel from 'primevue/panel';
import Textarea from 'primevue/textarea';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

const { t } = useI18n();
const token = ref('');
const infoMsg = ref('');
const errorMsg = ref('');
const valid = ref(false);
const isTokenVerified = ref(false);
const tokenNbWords = Number(import.meta.env.VITE_TOKEN_WORD_COUNT ?? '18');

const isTokenValid = () => {
  valid.value = true;
  errorMsg.value = '';
  if (token.value.split(' ').length !== tokenNbWords) {
    valid.value = false;
    errorMsg.value = t('UserAssociationView.TokenError.invalidWordSize', {
      tokenNbWords: tokenNbWords,
    });
  }
  if (token.value.length == 0) {
    errorMsg.value = t('UserAssociationView.TokenError.empty');
    valid.value = false;
  }
};

const handleUserAssociation = async () => {
  isTokenValid();
  if (valid.value) {
    await validateAssociationToken(token.value)
      .then(() => {
        isTokenVerified.value = true;
        infoMsg.value = t('UserAssociationView.verifiedTokenMessage');
      })
      .catch((error) => {
        if (error.status == 400) {
          errorMsg.value = t('Error.UserAssociationView.400.message');
        } else if (error.status == 409) {
          infoMsg.value = t('Error.UserAssociationView.409.message');
          isTokenVerified.value = true;
        } else {
          errorMsg.value = t('Error.500.message');
        }
      });
  }
};
</script>
