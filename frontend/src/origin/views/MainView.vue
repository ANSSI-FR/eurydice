<template>
  <DefaultLayout>
    <template #navbar>
      <MainNavbar>
        <template #navbarAction>
          <AssociationTokenMenuItem />
        </template>
      </MainNavbar>
    </template>
    <template #main>
      <div class="p-5 flex gap-5 flex-col w-screen">
        <StatusBanner />
        <div
          class="p-2 border rounded-(--p-content-border-radius) border-(--p-content-border-color) bg-(--p-content-background)"
        >
          <Tabs value="0">
            <TabList>
              <Tab value="0" id="fileUploadTab">
                <div class="flex gap-2 justify-center items-center">
                  <i class="pi pi-file-arrow-up" />
                  <span>{{ $t('UploadFile.tabTitle') }}</span>
                </div>
              </Tab>
              <Tab value="1">
                <div class="flex gap-2 justify-center items-center">
                  <i class="pi pi-pencil" />
                  <span>{{ $t('UploadText.tabTitle') }}</span>
                </div>
              </Tab>
            </TabList>
            <TabPanels>
              <TabPanel value="0">
                <UploadFile />
              </TabPanel>
              <TabPanel value="1">
                <UploadText />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </div>
        <OriginTransferableTable />
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
import AssociationTokenMenuItem from '@origin/components/AssociationTokenMenuItem.vue';
import OriginTransferableTable from '@origin/components/OriginTransferableTable.vue';
import UploadFile from '@origin/components/UploadFile.vue';
import UploadText from '@origin/components/UploadText.vue';
import Tab from 'primevue/tab';
import TabList from 'primevue/tablist';
import TabPanel from 'primevue/tabpanel';
import TabPanels from 'primevue/tabpanels';
import Tabs from 'primevue/tabs';
</script>
