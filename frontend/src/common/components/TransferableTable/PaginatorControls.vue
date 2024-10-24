<template>
  <div class="Paginator-controls mt-3" :style="cssProps">
    <v-btn
      outlined
      :disabled="page === 1 || disabled"
      color="grey darken-2"
      class="ml-2"
      @click="previous"
    >
      <v-icon>{{ mdiChevronLeft }}</v-icon>
    </v-btn>
    <v-text-field
      :value="page"
      label="Page"
      :suffix="suffixString"
      dense
      outlined
      :disabled="disabled"
      class="shrink mx-2"
      :rules="rules"
      @keyup.enter="goToPage"
    />
    <v-btn
      outlined
      :disabled="page === numPages || disabled"
      color="grey darken-2"
      class="mr-4"
      @click="next"
    >
      <v-icon>{{ mdiChevronRight }}</v-icon>
    </v-btn>
  </div>
</template>

<script>
import { mdiChevronLeft, mdiChevronRight } from "@mdi/js";

export default {
  name: "PaginatorControls",
  props: {
    numPages: {
      type: Number,
      required: true,
      default: 0,
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      page: 1,
      mdiChevronLeft,
      mdiChevronRight,
    };
  },
  computed: {
    suffixString() {
      return `sur ${this.numPages}`;
    },
    rules() {
      return [
        (v) => (v && v >= 1) || "Doit être supérieur à 0",
        (v) =>
          (v && v <= this.numPages) || `Doit être inférieur à ${this.numPages}`,
      ];
    },
    /**
     * Compute the text input CSS width from the largest string that could credibly be inputted.
     * @return  {Object} val  The CSS computed CSS props as an object.
     */
    cssProps() {
      return {
        "--text-field-width": `${
          this.numPages.toString().length + this.suffixString.length + 3
        }ch`,
      };
    },
    disabled() {
      return this.loading || this.numPages === 0;
    },
  },
  methods: {
    async next() {
      this.page += 1;
      this.$emit("next");
    },
    async previous() {
      this.page -= 1;
      this.$emit("previous");
    },
    goToPage(event) {
      const pageNumber = parseInt(event.target.value, 10);
      if (pageNumber && pageNumber >= 1 && pageNumber <= this.numPages) {
        this.page = pageNumber;
        this.$emit("goto-page", this.page);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.v-btn:not(.v-btn--round).v-size--default {
  height: 40px;
  min-width: 0;
  width: 10px;
}

.v-text-field.v-text-field--enclosed {
  // input validation messages take up more than one line if smaller
  min-width: 16ch;
  // just the right size to allow inputting the largest page number without any overflow
  width: var(--text-field-width);
}

.Paginator-controls {
  align-items: flex-start;
  display: flex;
  justify-content: flex-end;
}
</style>
