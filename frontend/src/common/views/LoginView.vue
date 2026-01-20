<script setup lang="ts">
import logo from '@assets/img/lyre.svg?no-inline';
import { Button, Card } from 'primevue';
const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1';

const redirectLoginSSO = () => {
  window.location.href = API_URL + '/user/login/sso';
  // this route must be handled by reverse proxy and forwarded to /api/v1/user/login
};

const redirectLoginKerberos = () => {
  window.location.href = API_URL + '/user/login/kerberos';
  // this route must be handled by reverse proxy and forwarded to /api/v1/user/login
};
</script>

<template>
  <div class="h-screen w-screen flex justify-center items-center">
    <Card class="flex text-center">
      <template #title>
        <div class="flex flex-col justify-center items-center gap-2">
          <img :src="logo" class="w-[20vh]" />
          <div class="text-3xl">Eurydice</div>
        </div>
      </template>
      <template #footer>
        <div class="flex flex-col gap-2">
          <Button label="Se connecter avec SSO" class="mt-5" @click="redirectLoginSSO" />
          <Button label="Se connecter avec Kerberos" class="mt-5" @click="redirectLoginKerberos" />
        </div>
      </template>
    </Card>
  </div>
</template>
