<template>
  <CustomModal class="box-modal-info card-payment-modal" @closeModal="onAgreeClick">
    <header slot="header" class="card-payment-modal__header">
      <h1 class="card-payment-modal__header-text">
        Важно!
      </h1>
    </header>

    <body class="card-payment-modal__body" slot="body">
      <p class="card-payment-modal__body-text">
        При оплате картой взимается комиссия 3%<br>
        При оплате с помощью СБП комиссия не взимается
      </p>
    </body>

    <footer class="card-payment-modal__footer" slot="footer">
      <CustomButton value="Понятно" type="normal" @get="onAgreeClick" />
    </footer>
  </CustomModal>
</template>

<script lang="js">
import CustomButton from "~/components/customButton.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: 'cardPaymentModal',
  comments: {
    CustomButton,
    CustomModal,
  },
  computed: {
    amount() {
      return this.$store.state.dataModal.amount;
    }
  },
  methods: {
    onAgreeClick() {
      this.$store.dispatch(
        'get_post_request',
        {
          url: 'payment_url',
          data: {
            amount: this.amount,
            type: 'card',
          },
        },
      );
    },
  },
}
</script>

<style lang="scss" scoped>
.card-payment-modal__header-text {
  font-family: 'myriadRegular';
  font-weight: 400;
  font-size: 20px;
  line-height: 24px;
  color: var(--dark-blue);
  text-align: center;
}

.card-payment-modal__body-text {
  font-family: 'myriadRegular';
  font-weight: 400;
  font-size: 20px;
  line-height: 24px;
  color: var(--drak-green);
  text-align: center;
}
</style>
