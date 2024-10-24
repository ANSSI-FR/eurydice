<template>
  <div
    @drop.prevent="uploadFilesFromEvent"
    @dragover.prevent
    @dragenter.prevent
  >
    <v-tabs bg-color="primary">
      <v-tab @click="changeTab('files')">Fichiers</v-tab>
      <v-tab @click="changeTab('text')">Texte</v-tab>
    </v-tabs>
    <v-file-input
      v-if="formatTab == 'files'"
      v-model="files"
      :clearable="false"
      chips
      counter
      multiple
      outlined
      show-size
      prepend-icon
      :webkitdirectory="allowDirectoryUpload"
      :allowdirs="allowDirectoryUpload"
      :disabled="disableDropZone"
      :placeholder="
        disableDropZone
          ? 'Le transfert de fichiers n\'est pas opérationnel'
          : 'Cliquez ou déposez vos fichiers ici'
      "
      @change="uploadFiles"
    >
      <template v-if="files.length === 0" #prepend-inner>
        <v-icon v-if="disableDropZone" large>{{ mdiTrafficCone }}</v-icon>
        <v-icon v-else large>{{ mdiUpload }}</v-icon>
      </template>
      <template #selection="{ file }">
        <DropZoneFile
          :name="file.name"
          :progress="file.progress"
          :finished="file.state === STATES.SUCCESS"
          :error="file.state === STATES.FAILURE"
        ></DropZoneFile>
      </template>
      <template v-if="files.length !== 0" #append>
        <div class="DropZone-icons">
          <v-tooltip left>
            <template #activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on" @click="removeFinished">{{
                mdiCheckAll
              }}</v-icon>
            </template>
            <span>Masquer les transferts terminés</span>
          </v-tooltip>
        </div>
      </template>
    </v-file-input>
    <TextTransferZone v-if="formatTab == 'text'" @send_text="uploadFile" />
  </div>
</template>

<script>
import {
  mdiUpload,
  mdiCheckAll,
  mdiDeleteSweep,
  mdiTrafficCone,
} from "@mdi/js";
import { mapGetters } from "vuex";
import DropZoneFile from "@origin/components/DropZoneFile";
import {
  createTransferable,
  validateTransferable,
} from "@origin/api/transferables";
import axios from "axios";
import TextTransferZone from "@origin/components/TextTransferZone";

const STATES = {
  ONGOING: "ongoing",
  SUCCESS: "success",
  FAILURE: "failure",
  CANCELED: "canceled",
};

export default {
  name: "DropZone",
  components: { DropZoneFile, TextTransferZone },
  data: () => {
    return {
      files: [],
      oldFiles: [],
      STATES,
      allowDirectoryUpload: false,
      fileUploadPromises: [],
      mdiUpload,
      mdiCheckAll,
      mdiDeleteSweep,
      mdiTrafficCone,
      formatTab: "files",
    };
  },
  computed: {
    ...mapGetters(["serverDown", "maintenance"]),
    disableDropZone() {
      return !this.maintenance && this.serverDown;
    },
  },
  methods: {
    beforeUnloadListener(event) {
      event.preventDefault();
      /* eslint-disable-next-line no-param-reassign */ /* eslint-disable-next-line no-return-assign */
      return (event.returnValue =
        "Attention, les téléversements en cours depuis cet onglet vers le guichet origine seront annulés.");
    },
    uploadFilesFromEvent(event) {
      const items = Array.from(event.dataTransfer.items);

      // anticipate potential rename of webkitGetAsEntry to getAsEntry
      // https://developer.mozilla.org/en-US/docs/Web/API/DataTransferItem/webkitGetAsEntry
      const getAsEntry = (item) =>
        item.webkitGetAsEntry?.() || item.getAsEntry?.();

      const newFiles = items
        .filter((item) => getAsEntry(item)?.isFile)
        .map((file) => file.getAsFile());

      this.uploadFiles(newFiles);

      if (items.some((item) => getAsEntry(item)?.isDirectory)) {
        this.$alert(
          "Il n'est pas possible d'envoyer des dossiers, ceux-ci ont été ignorés.",
          "warning"
        );
      }
    },
    uploadFiles(newFiles) {
      window.addEventListener("beforeunload", this.beforeUnloadListener, {
        capture: true,
      });

      if (newFiles === this.oldFiles) return;

      this.files = [...this.oldFiles, ...newFiles];
      this.oldFiles = this.files;

      this.fileUploadPromises.push(
        Promise.all(newFiles.map((file) => this.uploadFile(file)))
      );
    },
    async uploadFile(fileReference) {
      const file = fileReference;
      this.annotateFile(file);

      try {
        validateTransferable(file);
        const data = await createTransferable(file);
        file.state =
          data && data.submissionSucceeded ? STATES.SUCCESS : STATES.FAILURE;
      } catch (error) {
        if (error?.response) {
          file.state = STATES.FAILURE;
          // Request was throttled or the file's size exceeds the limit
          if ([413, 429].includes(error?.response.status)) {
            this.$alert(error.response.data.detail, "error");
          }
        } else if (error instanceof axios.Cancel) {
          file.state = STATES.CANCELED;
          this.removeOne(this.files.indexOf(file));
          this.$alert("Le transfert a été interrompu", "info");
        }
      } finally {
        file.progress = 100;
        this.refreshFile(file);

        Promise.all(this.fileUploadPromises).then(() => {
          window.removeEventListener(
            "beforeunload",
            this.beforeUnloadListener,
            {
              capture: true,
            }
          );
        });
      }
    },
    annotateFile(fileReference) {
      const file = fileReference;
      file.progress = 0;
      file.state = STATES.ONGOING;
      file.abortController = new AbortController();
      file.progressUpdater = this.generateFileProgressUpdater(file);
      this.refreshFile(file);
    },
    generateFileProgressUpdater(fileReference) {
      const file = fileReference;
      return (progress) => {
        file.progress = Math.round((progress.loaded * 100) / progress.total);
        this.refreshFile(file);
      };
    },
    refreshFile(file) {
      // Required for Vue to notice a change to `this.files`
      const index = this.files.indexOf(file);
      if (index !== -1) this.$set(this.files, index, file);
    },
    removeOne(index = 0) {
      const removed = this.files.splice(index, 1)[0];
      this.oldFiles = this.files;

      if (removed.state === STATES.ONGOING) removed.abortController.abort();
    },
    removeAll() {
      while (this.files.length) this.removeOne();
    },
    removeFinished() {
      this.files = this.files.filter((f) => f.state === STATES.ONGOING);
      this.oldFiles = this.files;
    },
    changeTab(currentTab) {
      this.formatTab = currentTab;
    },
  },
};
</script>

<style lang="scss" scoped>
::v-deep {
  .v-input__append-inner {
    align-self: center;
    margin-top: 0;
  }

  .v-input__prepend-inner {
    left: calc(50% - 18px);
    position: absolute;
    top: 12px;
  }

  .v-file-input__text--placeholder {
    align-content: center !important;
    font-size: 1.2em;
    justify-content: center;
    padding-top: 40px;
  }

  .v-file-input__text {
    align-content: flex-start;
    align-items: flex-start;
    min-height: 120px;
  }

  .DropZone-icons {
    display: flex;
    flex-flow: column nowrap;
    gap: 16px;
  }
}
</style>
