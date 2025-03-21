<template>
  <div class="text-transfer-zone">
    <v-textarea
      v-model="text"
      :disabled="ongoingTransfer"
      placeholder="Collez votre texte ici"
    >
    </v-textarea>
    <p>
      <button :disabled="disableSendingText" @click="transferText">
        Envoyer le texte
      </button>
      <span v-if="ongoingTransfer">Texte en cours d'envoi</span>
    </p>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "TextTransferZone",
  data() {
    return {
      text: "",
    };
  },
  computed: {
    ...mapGetters(["ongoingTransfer"]),
    disableSendingText() {
      return this.text.length < 1 || this.ongoingTransfer;
    },
  },
  watch: {
    ongoingTransfer(value) {
      if (!value) {
        this.text = "";
      }
    },
  },
  methods: {
    transferText() {
      this.$store.commit("setOngoingTransfer", true);
      const filename = `presse-papier_${this.getFormattedDate()}.txt`;
      const file = new File([this.text], filename, { type: "text/plain" });
      this.$emit("send_text", file);
    },
    getFormattedDate() {
      const now = new Date();

      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are 0-based
      const day = String(now.getDate()).padStart(2, "0");
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");

      return `${year}-${month}-${day}_${hours}-${minutes}`;
    },
  },
};
</script>

<style>
.text-transfer-zone {
  .v-textarea {
    margin: 0;
    min-height: 120px;
    padding: 6px 0;
  }

  .v-text-field__details {
    display: none;
  }

  .v-textarea textarea {
    border-collapse: collapse;
    border-color: currentColor;
    border-radius: 4px;
    border-style: solid;
    border-width: 1px;
  }

  textarea:disabled {
    background-color: #eee;
  }

  .v-input.v-textarea > .v-input__control > .v-input__slot::before {
    border: 0;
  }

  button {
    align-self: flex-end;
    background-color: #fd095d;
    border-radius: 4px;
    color: #fff;
    margin: 5px;
    padding: 10px;
  }

  button:hover {
    background-color: #bc1742;
  }

  button:disabled {
    background-color: #777;
  }
}
</style>
