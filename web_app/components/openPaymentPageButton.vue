<script>
import CustomButton from "@/components/customButton.vue";

export default {
  name: "openPaymentPageButton",
  components: {
    CustomButton,
  },
  methods: {
    redirectPaymentPage() {
      this.$router.push("/payment");
    }
  }
}
</script>

<template>
  <CustomButton value="Пополнить" type="action" @get="redirectPaymentPage" />
</template>

<style scoped lang="scss">

</style>
