<template>
  <v-container class="UserAssociation-Card">
    <h1 class="mb-2">👋 Bienvenue</h1>
    <p>
      Il semble que vous n'ayez pas encore associé votre compte utilisateur côté
      destination avec votre compte côté origine.
    </p>
    <p>Cette étape est nécessaire pour pouvoir accéder à vos transferts.</p>
    <p>Réalisez l'association de vos comptes en quelques instants :</p>
    <ol>
      <li>
        Connectez-vous à l'interface utilisateur côté origine. Cliquez ensuite
        sur le bouton "Jeton d'Association" situé en haut à droite de la page.
      </li>
      <li>Prenez note du jeton d'association.</li>
      <li>Entrez le jeton d'association dans le formulaire ci-dessous.</li>
    </ol>
    <v-form
      id="UserAssociation-TokenForm"
      ref="tokenForm"
      v-model="tokenIsValid"
      class="pa-4 pt-6"
      @keyup.native.enter="tokenIsValid && submitAssociationTokenForm()"
      @submit.prevent="submitAssociationTokenForm"
    >
      <v-textarea
        id="UserAssociation-TextArea"
        v-model="token"
        class="mb-2"
        label="Jeton d'association"
        :error-messages="tokenSubmissionErrorMessages"
        :success-messages="tokenSubmissionSuccessMessages"
        outlined
        :clearable="!tokenSubmissionSuccess"
        persistent-hint
        no-resize
        auto-grow
        :readonly="tokenSubmissionSuccess"
        :rules="tokenRules"
        hint="⚠️ Attention aux majuscules, la casse du texte est prise en compte."
        @input="resetTokenSubmissionMessages()"
        @keydown.enter.prevent="tokenIsValid && submitAssociationTokenForm"
      />

      <v-btn
        v-if="tokenSubmissionSuccess"
        id="UserAssociation-ContinueButton"
        color="primary"
        href="/"
        ><v-icon left>{{ mdiArrowRight }}</v-icon
        >Continuer</v-btn
      >
      <v-btn
        v-else
        id="UserAssociation-SubmitButton"
        :disabled="!tokenIsValid"
        :loading="submittingToken"
        color="primary"
        type="submit"
      >
        <v-icon left> {{ mdiHumanGreetingProximity }} </v-icon>
        Associer
      </v-btn>
    </v-form>
  </v-container>
</template>

<script>
import { mdiArrowRight, mdiHumanGreetingProximity } from "@mdi/js";
import { postAssociationToken } from "@destination/api/association";
import { associationTokenWordCount } from "@destination/settings";

export default {
  name: "UserAssociation",
  data() {
    return {
      token: null,
      tokenIsValid: false,
      submittingToken: false,
      tokenSubmissionSuccess: null,
      tokenSubmissionErrorMessages: [],
      tokenSubmissionSuccessMessages: [],
      tokenRules: [
        (token) =>
          (typeof token === "string" &&
            token.split(/\s+/).filter((i) => i).length ===
              associationTokenWordCount) ||
          `Le jeton doit être composé d'exactement ${associationTokenWordCount} mots.`,
        (token) =>
          /^[a-zA-Z ]+$/.test(token) ||
          `Le jeton ne doit contenir que des lettres et des espaces.`,
      ],
      mdiArrowRight,
      mdiHumanGreetingProximity,
    };
  },
  methods: {
    async submitAssociationTokenForm() {
      try {
        await this.submitAssociationToken();
      } catch (error) {
        this.handleTokenSubmissionFailure(error);
      }
      this.submittingToken = false;
      if (this.tokenSubmissionSuccess) {
        this.tokenSubmissionSuccessMessages.push(
          "Votre compte est maintenant associé."
        );
      }
    },
    async submitAssociationToken() {
      this.submittingToken = true;
      await postAssociationToken(this.token);
      this.tokenSubmissionSuccess = true;
    },
    handleTokenSubmissionFailure(error) {
      this.tokenSubmissionSuccess = false;
      this.tokenSubmissionErrorMessages.push(
        ...Object.values(error.response.data)
      );
    },
    resetTokenSubmissionMessages() {
      this.tokenSubmissionErrorMessages = [];
    },
  },
};
</script>
<style scoped>
.UserAssociation-Card {
  margin: auto;
  max-width: 600px;
}
</style>
