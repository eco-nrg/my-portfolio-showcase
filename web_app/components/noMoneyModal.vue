<template>
  <CustomModal class="box-modal-alert" @closeModal="closeModal">
    <div slot="body">
      <p>У вас недостаточно средств на счету! Пополните свой лицевой счёт!</p>
    </div>
    <div slot="footer">
      <openPaymentPageButton />
    </div>
  </CustomModal>
</template>

<script lang="js">
import CustomModal from "~/components/customModal.vue";
import openPaymentPageButton from "@/components/openPaymentPageButton.vue";

export default {
  name: "NoMoneyModal",
  components: {
    CustomModal,
    openPaymentPageButton,
  },
  methods: {

    closeModal() {
      this.$router.replace("/profile");
      this.$store.dispatch("closeModal");
    }
  }
}
</script>

<style></style>
