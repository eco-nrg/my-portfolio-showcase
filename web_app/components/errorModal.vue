<template>
  <CustomModal class="box-modal-alert error-modal" @closeModal="closeModal">

    <body slot="body" class="error-modal__body">
      <p class="error-modal__error-text">
        {{ errorMsg }}
      </p>
    </body>

    <div slot="footer" class="error-modal__footer">
      <CustomButton value="Понятно)" type="action" @get="closeModal()" />
    </div>

  </CustomModal>
</template>

<script lang="js">
import CustomButton from "~/components/customButton.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: 'errorModal',
  components: {
    CustomButton,
    CustomModal,
  },
  computed: {
    errorMsg() {
      return this.$store.state.errorMsg;
    },
  },
  methods: {
    closeModal() {
      this.$store.dispatch('clearErrorMsg');
      this.$store.dispatch('closeModal');
    },
  },
};
</script>

<style lang="scss" scoped></style>