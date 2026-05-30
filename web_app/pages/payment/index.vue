
<template>
  <div class="payment-card-wrapper">
    <div class="payment-card">
      <h1 class="payment-card__header-text">Доступно</h1>

      <div class="payment-card__balance">
        <p class="balance__text-line"><span class="balance__name">Рублей:</span> <span class="balance__value">{{ cashData.money }}</span></p>
        <p class="balance__text-line"><span class="balance__name">Бонусов:</span> <span class="balance__value">{{ cashData.bonus }}</span></p>
      </div>

      <div class="payment-card__balance-input">
        <p class="balance-input__text">Пополнить баланс</p>
        <div class="balance-input__input-group">
          <label class="balance-input__label">Введите сумму пополнения</label>
          <CustomInput class="balance-input__input" placeholder="0,00" type="number" inputId="amount" ref="amountInput" :inputKey="amountKey"
                       :value="amount" @input="changeAmount" :isError="isAmountError" :errorMessage="amountErrorMessage" />
        </div>
      </div>

      <div class="payment-card__payment-options">
        <p class="payment-options__header-text">Выберите источник<br> пополнения</p>
        <div class="payment-options__icons">
          <img class="payment-options__img payment-options__img--clickable" src="~/assets/payment-icon.svg"
               alt="Карта" @click="onPayClick('card')" />
          <img class="payment-options__img payment-options__img--clickable" src="~/assets/bonus-icon.svg"
               alt="Бонусы" @click="onPayClick('bonus')" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import CustomInput from "@/components/customInput.vue";

  export default {
    name: 'PaymentPage',
    components: {
      CustomInput,
    },
    data: () => ({
      amount: '',
      amountKey: 'amount',
      isAmountError: false,
      amountErrorMessage: ''
    }),
    computed: {
      cashData() {
        return this.$store.state.cashData;
      },
      email(){
        return this.$store.state.profileData?.email;
      }
    },
    methods: {
      userHasEmailFilled(){
        return this.email !== undefined && this.email !== '' && this.email !== null && this.email.length !== 0;
      },
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
        if (amount < 5.0) {
          this.isAmountError = true;
          this.amountErrorMessage = 'Минимальная сумма платежа 5 рублей';
          return;
        }
        if (amount > 500000.0) {
          this.isAmountError = true;
          this.amountErrorMessage = 'Максимальная сумма платежа 500 000 рублей';
          return;
        }

        if(!this.userHasEmailFilled()){
          this.$store.dispatch(
              'setModal',
              {
                name: "notifyAboutEmailField",
                type: "alert",
              },
          )
        }

        if (type === 'card' && this.userHasEmailFilled()) {
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

        // this.$store.dispatch(
        //     'get_post_request',
        //     {
        //       url: 'payment_url',
        //       data: {
        //         amount,
        //         type,
        //       },
        //     },
        // );
      },
    }
  }
</script>

<style scoped lang="scss">
.payment-card-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.payment-card {
  margin-top: 45px;
  padding: 28px 22px 20px 22px;
  box-sizing: border-box;
  height: fit-content;
  width: 94.375%;
  background-color: #fff;
  border: 2px solid #00AAFF;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  font-family: 'myriadBold', sans-serif;
}

.payment-card__header-text {
  color: #575756;
  font-size: 24px;
  font-weight: 700;
  text-transform: uppercase;
}

.payment-card__balance {
  color: #00AAFF;
  margin-top: 14px;
  font-size: 24px;
}

.balance__text-line {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.balance__name {
  display: inline-block;
}

.balance__value {
  display: inline-block;
  right: 0;
}

.payment-card__balance-input {
  margin-top: 34px;
  font-size: 20px;
  font-weight: 400;
  font-family: 'myriadRegular', sans-serif;
}

.balance-input__text {
  color: #575756;
  font-weight: 600;
}

.balance-input__input-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.balance-input__label {
  color: #E84E0F;
  max-width: 130px;
}

.balance-input__input {
  max-width: 120px;
  margin-left: 20px;
}

.payment-card__payment-options{
  margin-top: 34px;
  font-size: 20px;
  font-family: 'myriadRegular', sans-serif;
}

.payment-options__header-text {
  color: #E84E0F;
}
.payment-options__icons {
  margin-top: 3px;
  display: flex;
  flex-direction: row;
  align-items: baseline;
  column-gap: 8px;
}

.payment-options__img {
  width: 26.8%;
  max-width: 82px;
}
</style>