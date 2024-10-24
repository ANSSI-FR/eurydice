<template>
  <v-menu
    class="transferable-preview-menu"
    offset-y
    transition="slide-y-transition"
    left
  >
    <template #activator="{ on, attrs }">
      <v-btn
        class="preview-btn"
        icon
        v-bind="attrs"
        :disabled="disabled"
        v-on="on"
        @click="fetchFileContent()"
      >
        <v-icon>{{ mdiEyeCircle }}</v-icon>
        <span v-if="disabled" class="tooltip"
          >Prévisualisation seulement sur les fichiers txt, md, json, xml et
          dont la taille &#060; 1Mo</span
        >
      </v-btn>
    </template>
    <v-card class="transferable-preview-card">
      <v-card-actions>
        <v-btn text> Fermer </v-btn>
        <v-btn text @click="copyFileContent"> Copier et fermer </v-btn>
      </v-card-actions>
      <v-card-text @click.stop>
        <pre>{{ fileContent }}</pre>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import { mdiEyeCircle } from "@mdi/js";
import { service } from "@common/utils/request";

export default {
  name: "TransferablePreviewButton",
  props: {
    transferable: {
      type: Object,
      required: true,
    },
    disabled: Boolean,
  },
  data: () => ({ mdiEyeCircle, fileContent: "" }),
  methods: {
    async fetchFileContent() {
      if (this.fileContent.length === 0) {
        service
          .get(`transferables/${this.transferable.id}/download`)
          .then((response) => {
            this.fileContent = response;
          });
      }
    },
    copyFileContent() {
      navigator.clipboard.writeText(this.fileContent);
    },
  },
};
</script>

<style lang="scss" scoped>
.transferable-preview-menu {
  .v-menu__content {
    height: 90vh;
    width: 100vw;
  }
}

.transferable-preview-card {
  .v-card__text {
    max-height: 60vh;
    overflow-y: scroll;
    width: 100vw;
  }
}

.preview-btn .tooltip {
  background-color: #000;
  border-radius: 3px;
  color: #fff;
  opacity: 0;
  padding: 5px 10px;

  position: absolute;
  right: 100%;
  text-align: center;

  text-transform: none;
  visibility: hidden;
  z-index: 1;
}
@keyframes grow {
  from {
    transform: scale(0.3);
  }

  to {
    transform: scale(1);
  }
}

/* Show the tooltip text when you mouse over the tooltip container */
.preview-btn:hover .tooltip {
  animation-duration: 0.3s;
  animation-name: grow;
  opacity: 1;
  transition-duration: 0.3;
  visibility: visible;
}

.preview-btn.v-btn--disabled {
  pointer-events: all;
}
</style>
