<template>
  <CustomModal @closeModal="closeModal" class="box-modal-alert space-status-modal">

    <body slot="body" class="space-status-modal__body">
      <p class="space-status-modal__body-text">
        Данная станция <u>{{ textStatus[status] }}</u>.
      </p>
      <p class="space-status-modal__body-text">
        Приносим свои извинения
      </p>
    </body>
    <footer slot="footer">
      <CustomButton value="понятно" type="action" @get="closeModal" />
    </footer>

  </CustomModal>
</template>

<script lang="js">
import CustomButton from '~/components/customButton.vue';
import CustomModal from '~/components/customModal.vue';

export default {
  name: 'spaceStatusModal',
  components: {
    CustomButton,
    CustomModal,
  },
  props: {
    status: {
      type: String,
    },
  },
  computed: {
    textStatus() {
      return this.$store.state.status;
    },
  },
  methods: {
    closeModal() {
      this.$router.replace('/profile');
      this.$store.dispatch('closeModal');
    }
  }
}
</script>

<style lang="scss" scoped></style>