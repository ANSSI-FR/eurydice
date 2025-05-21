<template>
  <div
    class="grid grid-cols-1 place-content-center w-screen h-screen gap-5 justify-items-center p-5"
  >
    <img :src="logoImage" class="w-[20vh] max-w-full" />
    <p class="text-xl">{{ $t('Page404.errorMessage') }}</p>
    <RouterLink :to="{ name: 'home' }" data-testid="PageError404.returnHomeLink">
      <MainButton tkey="Page404.homeRedirectMessage" icon="pi pi-home" />
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import logoImage from '@assets/img/lyre.svg?no-inline';
import MainButton from '@common/components/MainButton.vue';
</script>
