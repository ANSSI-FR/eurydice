<template>
  <div class="user-association text-center">
    <v-dialog v-model="dialogVisible" width="500">
      <template #activator="{ on, attrs }">
        <v-btn outlined v-bind="attrs" v-on="on">Jeton d'association</v-btn>
      </template>
      <v-card>
        <v-card-title>Jeton d'association des comptes</v-card-title>

        <v-card-text>
          Associer votre compte utilisateur côté destination est nécessaire pour
          transférer des fichiers. Pour réaliser l'association, entrez le texte
          présent ci-dessous dans l'interface utilisateur côté destination.
        </v-card-text>
        <v-card-text class="align-center">
          <v-textarea
            v-model="token"
            label="Jeton d'association"
            outlined
            readonly
            persistent-hint
            no-resize
            auto-grow
            :hint="tokenHint"
            :loading="token === null"
            :disabled="token === null"
          >
            <template #append>
              <v-btn class="ma-0" icon @click="copyTokenToClipboard">
                <v-icon v-if="copiedToClipboard">{{
                  mdiClipboardCheck
                }}</v-icon>
                <v-icon v-else>{{ mdiClipboard }}</v-icon>
              </v-btn>
            </template>
          </v-textarea>
        </v-card-text>
        <v-card-text>
          <v-icon small>{{ mdiAlert }}</v-icon>
          Attention aux majuscules, la casse du texte est prise en compte.
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" text @click="dialogVisible = false"
            >Fermer</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mdiAlert, mdiClipboard, mdiClipboardCheck } from "@mdi/js";
import { getAssociationToken } from "@origin/api/association";

export default {
  name: "UserAssociation",
  data() {
    return {
      dialogVisible: false,
      token: null,
      tokenExpiresAt: null,
      copiedToClipboard: false,
      mdiAlert,
      mdiClipboard,
      mdiClipboardCheck,
    };
  },
  computed: {
    tokenHint() {
      return this.tokenExpiresAt
        ? `Ce jeton expire ${this.tokenExpiresAt.fromNow()}`
        : null;
    },
  },
  watch: {
    async dialogVisible(visible) {
      if (visible) {
        const { token, expiresAt } = await getAssociationToken();
        this.token = token;
        this.tokenExpiresAt = this.$date(expiresAt);
      }
    },
  },
  methods: {
    copyTokenToClipboard() {
      navigator.clipboard.writeText(this.token);
      this.copiedToClipboard = true;
      setTimeout(() => {
        this.copiedToClipboard = false;
      }, 3 * 1000);
    },
  },
};
</script>

<style scoped>
@media only screen and (max-width: 680px) {
  .user-association {
    margin: auto !important;
  }
}
</style>
