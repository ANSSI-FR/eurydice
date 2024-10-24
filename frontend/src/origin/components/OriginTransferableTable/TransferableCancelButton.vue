<template>
  <div class="TransferableCancelButton">
    <v-icon v-if="!CANCELLABLE_STATES.includes(transferable.state)" disabled>{{
      mdiMinus
    }}</v-icon>
    <v-btn v-else icon target="_blank" :loading="clicked" @click="cancel">
      <v-icon>{{ mdiCancel }}</v-icon>
    </v-btn>
  </div>
</template>

<script>
import { mdiCancel, mdiMinus } from "@mdi/js";
import { TRANSFERABLE_STATES } from "@origin/constants";
import { cancelTransferable } from "@origin/api/transferables";

export default {
  name: "TransferableCancelButton",
  props: {
    transferable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      clicked: false,
      CANCELLABLE_STATES: [
        TRANSFERABLE_STATES.PENDING,
        TRANSFERABLE_STATES.ONGOING,
      ],
      mdiCancel,
      mdiMinus,
    };
  },
  methods: {
    async cancel() {
      try {
        this.clicked = true;
        await cancelTransferable(this.transferable.id);
      } catch (error) {
        if (error.response && error.response.status === 400)
          this.$alert(error.response.data.detail, "error");
        this.clicked = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@use "sass:map";
/* stylelint-disable */
@import "~vuetify/src/components/VBtn/_variables";
/* stylelint-enable */
.TransferableCancelButton {
  display: flex;
  justify-content: center;
  width: map.get($btn-sizes, "default") + px;
}
</style>
