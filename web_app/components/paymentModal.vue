<template>
  <CustomModal class="box-modal-info payment-modal" @closeModal="closeModal">
    <header slot="header" class="payment-modal__header">
      <h1 class="payment-modal__header-text">
        Доступно
      </h1>
    </header>

    <body slot="body" class="payment-modal__body">

      <div class="payment-modal__balance-info">
        <p class="balance-info__text-line">
          Рублей: {{ cashData.money }}
        </p>

        <p class="balance-info__text-line">
          Бонусов: {{ cashData.bonus }}
        </p>
      </div>

      <div class="payment-modal__balance-input">
        <p class="balance-input__text">Пополнить баланс</p>
        <label class="balance-input__label">Введите сумму пополнения</label>
        <CustomInput placeholder="0,00" type="number" inputId="amount" ref="amountInput" :inputKey="amountKey"
          :value="amount" @input="changeAmount" :isError="isAmountError" :errorMessage="amountErrorMessage" />
      </div>
    </body>

    <footer slot="footer" class="box-icons payment-modal__footer">
      <p class="payment-modal__footer-text">Выберите источник пополнения</p>
      <div class="payment-modal__footer-buttons">
        <img class="payment-modal__footer-img payment-modal__footer-img--clickable" src="~/assets/payment-icon.svg"
          alt="Карта" @click="onPayClick('card')" />
        <img class="payment-modal__footer-img payment-modal__footer-img--clickable" src="~/assets/bonus-icon.svg"
          alt="Бонусы" @click="onPayClick('bonus')" />
      </div>
    </footer>
  </CustomModal>
</template>

<script lang="js">
import CustomInput from "~/components/customInput.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: 'paymentModal',
  components: {
    CustomInput,
    CustomModal,
  },
  data: () => ({
    amount: '',
    amountKey: 'amount',
    isAmountError: false,
    amountErrorMessage: '',
  }),
  computed: {
    cashData() {
      return this.$store.state.cashData;
    },
  },
  methods: {
    randomString() {
      return Math.random().toString(36).substring(2);
    },
    changeAmount(newAmount) {
      const positiveAmount = newAmount.replaceAll('-', '');
      if (positiveAmount === this.amount) {
        this.amountKey = this.randomString();
        this.$nextTick(() => {
          this.$refs.amountInput.focusInput();
        });
      }
      this.amount = positiveAmount;
      const amount = parseFloat(positiveAmount);
      this.amountWithCommission = (1.03 * amount).toFixed(2);
    },
    onPayClick(type) {
      if (!this.amount || this.amount.length === 0) {
        this.isAmountError = true;
        this.amountErrorMessage = 'Поле не должно быть пустым';
        return;
      }
      const amount = parseFloat(this.amount);
      if (amount < 1.0) {
        this.isAmountError = true;
        this.amountErrorMessage = 'Минимальная сумма платежа 1 рубль';
        return;
      }
      if (amount > 500000.0) {
        this.isAmountError = true;
        this.amountErrorMessage = 'Максимальная сумма платежа 500 000 рублей';
        return;
      }

      if (type === 'card') {
        this.$store.dispatch(
          'setModal',
          {
            name: 'cardPaymentModal',
            data: { amount },
          },
        );
        return;
      }

      if (type === 'bonus') {
        this.$store.dispatch(
          'get_post_request',
          {
            url: 'convert_bonuses',
            data: { amount },
          },
        );
        return;
      }

      this.$store.dispatch(
        'get_post_request',
        {
          url: 'payment_url',
          data: {
            amount,
            type,
          },
        },
      );
    },
    closeModal() {
      this.$store.dispatch('closeModal');
    },
  },
}
</script>

<style lang="scss" scoped>
.payment-modal__header-text {
  font-family: 'myriadBold';
  font-size: 24px;
  line-height: 24px;
  font-weight: 700;
  text-transform: uppercase;
}

.payment-modal__body {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.payment-modal__balance-info {
  display: flex;
  width: 100%;
  flex-direction: column;
}

.balance-info__text-line {
  font-family: 'myriadBold';
  font-size: 24px;
  line-height: 24px;
  font-weight: 700;
  color: var(--blue);

  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.payment-modal__balance-input {
  display: flex;
  flex-direction: column;
}

.balance-input__text {
  font-family: "myriadBold";
  font-size: 20px;
  line-height: 24px;
  font-weight: 600;
  color: var(--gray);
}

.balance-input__label,
.payment-modal__footer-text {
  font-family: "myriadRegular";
  font-size: 20px;
  line-height: 24px;
  font-weight: 400;
  color: var(--orange);
  text-align: center;
}

.payment-modal__footer {
  display: flex;
  flex-direction: column;
}

.payment-modal__footer-buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
}

.payment-modal__footer-img {
  width: 30%;
  max-width: 150px;

  &--clickable {
    cursor: pointer;
  }

  &--disabled {
    filter: grayscale(1);
  }
}
</style>
