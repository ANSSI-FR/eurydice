<template>
  <DefaultLayout>
    <template #navbar>
      <MainNavbar />
    </template>
    <template #main>
      <div class="p-5 flex gap-5 flex-col w-screen">
        <StatusBanner />
        <DestinationTransferableTable />
      </div>
    </template>
    <template #footer>
      <FooterComponent />
    </template>
  </DefaultLayout>
</template>

<script setup lang="ts">
import FooterComponent from '@common/components/FooterComponent.vue';
import MainNavbar from '@common/components/MainNavbar.vue';
import StatusBanner from '@common/components/StatusBanner.vue';
import DefaultLayout from '@common/layouts/DefaultLayout.vue';
import DestinationTransferableTable from '@destination/components/DestinationTransferableTable.vue';
</script>
