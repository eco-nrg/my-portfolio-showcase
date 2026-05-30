<template>
  <CustomButton value="Пополнить" type="action" @get="openPaymentModal" />
</template>

<script lang="js">
import CustomButton from "~/components/customButton.vue";

export default {
  name: "OpenPaymentModalButton",
  components: {
    CustomButton,
  },
  methods: {
    openPaymentModal() {
      this.$store.dispatch(
        "setModal",
        {
          name: "paymentModal",
        },
      );
    },
  }
}
</script>

<style></style>
