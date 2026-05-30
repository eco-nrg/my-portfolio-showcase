<template>
  <CustomModal class="box-modal-alert stop-session-modal" @closeModal="closeModal">

    <body slot="body" class="stop-session-modal__body">
      Завершить зарядку?
    </body>

    <footer slot="footer" class="stop-session-modal__footer">
      <div class="stop-session-modal__button-block">
        <CustomButton value="да" type="action" @get="stopSession" />
        <CustomButton value="нет" type="attention" @get="closeModal" />
      </div>
    </footer>

  </CustomModal>
</template>

<script lang="js">
import CustomButton from "~/components/customButton.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: 'stopSessionModal',
  comments: {
    CustomButton,
    CustomModal,
  },
  methods: {
    stopSession() {
      this.$store.dispatch('closeModal');
      this.$store.dispatch(
        'onsubmit',
        {
          type: 'stop_session',
          data: {},
        },
      );
      this.$router.push('/profile');
    },
    closeModal() {
      this.$store.dispatch('closeModal');
    },
  },
}
</script>

<style lang="scss" scoped>
.stop-session-modal__button-block {
  display: flex;
  justify-content: space-around;
  width: 100%;
}
</style>
