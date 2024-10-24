<template>
  <div>
    <v-card outlined>
      <v-data-table
        :headers="headers"
        :items="transferables.results"
        hide-default-footer
        disable-sort
        disable-filtering
        :loading="isLoading"
      >
        <template #top>
          <v-toolbar flat>
            <v-toolbar-title>Transferts</v-toolbar-title>
            <v-spacer />
            <v-scale-transition>
              <v-btn
                v-show="showRefresh"
                color="primary"
                depressed
                @click="getFreshFirstPage"
              >
                <v-icon left>{{ mdiRefresh }}</v-icon> Nouveaux fichiers
              </v-btn>
            </v-scale-transition>
          </v-toolbar>
        </template>

        <template
          v-for="header in headers"
          #[`item.${header.value}`]="{ item }"
        >
          <slot :name="header.value" :transferable="item">
            {{ item[header.value] }}
          </slot>
        </template>

        <template #footer>
          <PaginatorControls
            ref="paginatorControls"
            :loading="isLoading"
            :num-pages="numPages"
            @next="getTransferableFrom('next')"
            @previous="getTransferableFrom('previous')"
            @goto-page="getTransferablesPage"
          />
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
// eslint-disable-next-line no-unused-vars
import { mdiRefresh } from "@mdi/js";
import { listTransferables } from "@common/api/transferables";
import { transferablesPerPage } from "@common/settings";
import PaginatorControls from "@common/components/TransferableTable/PaginatorControls";
import AutoRefreshMixin from "@common/utils/AutoRefreshMixin";

export default {
  name: "TransferableTable",
  components: { PaginatorControls },
  mixins: [AutoRefreshMixin],
  props: {
    states: {
      type: Object,
      required: true,
    },
    headers: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      transferables: {},
      isLoading: true,
      numPages: 0,
      timer: null,
      showRefresh: false,
      listTransferablesAbortController: null,
      mdiRefresh,
    };
  },
  watch: {
    /**
     * Compute the page count from the API response
     * @param  {Object} val  The API response as received from fetching transferables.
     */
    transferables(val) {
      if (val.count !== null) {
        this.numPages = Math.ceil(val.count / transferablesPerPage);
      }
    },
  },
  async created() {
    await this.getFreshFirstPage();
    this.setupAutoRefresh();
  },
  methods: {
    cancelLastAutomaticRequest() {
      if (this.listTransferablesAbortController) {
        this.listTransferablesAbortController.abort();
      }
    },
    async refresh() {
      await this.getTransferableFrom("current", false, false);
    },
    /**
     * Get transferables from a page linked in the transferables' request JSON.
     * @param  {String} linkKey  One of "previous", "current" or "next".
     * @param  {Boolean} [loading=true] Whether to mark the table as loading while getting transferables.
     */
    async getTransferableFrom(linkKey, loading = true, manual = true) {
      this.isLoading = loading;
      if (manual) {
        this.cancelLastAutomaticRequest();
        this.transferables = await listTransferables({
          page: this.transferables.pages[linkKey],
          pageSize: transferablesPerPage,
        });
      } else {
        this.listTransferablesAbortController = new AbortController();
        try {
          this.transferables = await listTransferables(
            {
              page: this.transferables.pages[linkKey],
              pageSize: transferablesPerPage,
            },
            this.listTransferablesAbortController.signal
          );
        } catch (error) {
          if (error.message !== "canceled") {
            throw error;
          }
        }
      }
      if (this.transferables.newItems) {
        this.$store.commit("setOngoingTransfer", false);
      }
      if (!this.showRefresh) {
        this.showRefresh = this.transferables.newItems;
      }
      this.isLoading = false;
    },
    /**
     * Get transferables from the given page number.
     * @param  {Number} pageNumber  Page number to get transferables from.
     */
    async getTransferablesPage(pageNumber) {
      this.isLoading = true;
      this.cancelLastAutomaticRequest();
      const currentPage = this.transferables.offset / transferablesPerPage + 1;
      this.transferables = await listTransferables({
        delta: pageNumber - Math.floor(currentPage),
        from: this.transferables.pages.current,
        pageSize: transferablesPerPage,
      });

      this.isLoading = false;
    },
    /**
     * Get the latest available transferables and make the refresh button disappear.
     */
    async getFreshFirstPage() {
      this.isLoading = true;
      this.cancelLastAutomaticRequest();
      this.transferables = await listTransferables({
        pageSize: transferablesPerPage,
      });

      this.showRefresh = false;
      this.$refs.paginatorControls.page = 1;

      this.isLoading = false;
    },
  },
};
</script>
