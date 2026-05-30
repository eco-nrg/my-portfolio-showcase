<template>
  <div class="login-box">
    <div class="wrap">
      <div class="box-title">
        <div class="logo">
          <img src="~assets/logo.svg" />
        </div>
        <div class="context">
          <h2 class="title">АВТОРИЗАЦИЯ</h2>
          <p class="desck">ДОСТУП К ФУНКЦИОНАЛУ ЗАРЯДНЫХ СТАНЦИЙ</p>
        </div>
      </div>

      <div class="error-event">{{ errorMsg }}</div>

      <div v-if="!showSMSbox" class="form">
        <div class="form-box">
          <p class="number">
            введите ваш номер
          </p>

          <customInput placeholder="в формате (987) 6543210" type="tel" inputId="phone" ref="phoneInput"
            errorMessage="Неверный формат телефона" :inputKey="phoneKey" :value="phone" @input="changePhone"
            :isError="isPhoneError" @blurInput="checkPhone" />

          <customButton value="Далее" :disabled="!phoneCheck" @get="showSMSboxButton($event)" type="normal" />
        </div>
      </div>

      <div v-if="showSMSbox" class="sms-box">
        <div class="form-box">
          <p class="number"> ваш номер </p>

          <customInput placeholder="телефон" disabled type="tel" id="input-numb" :value="phone" inputId="phone" />

          <p form="input-sms" class="number sms-two">
            используйте последний код, который вы получали в SMS ранее
          </p>

          <customInput placeholder="sms code" type="pass" inputId="sms" inputKey="sms-code" errorMessage="Неверный формат"
            :value="smsCode" @input="changeSmsCode" :isError="isSmsCodeError" @blurInput="checkSmsCode" />

          <customButton class="sign-in__button" value="Войти" :type="'normal'" :disabled="signInDisabled"
            @get="getCode" />

          <customButton :value="remainSecText" type="action" :disabled="remainSec != 0" @get="getNewCode" />
        </div>
      </div>
    </div>
  </div>
</template>

<script leng="js">
import customInput from "~/components/customInput";
import customButton from "~/components/customButton";

// regex that match only digits, (, ), - and spaces
const regTell = /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
const regGrouping = /(\d{0,3})(\d{0,3})(\d{0,4})/;

const regSMS = /^[0-9]{6}$/;

export default {
  name: "IndexPage",
  head() {
    return {
      title: "eco-energo: Авторизация/Регистрация",
      meta: [
        {
          hid: "description",
          name: "description",
          content: "My custom description",
        },
      ],
    };
  },
  data: () => ({
    phone: '',
    isPhoneError: false,
    phoneKey: 'phone-key',
    smsCode: '',
    isSmsCodeError: false,
    showSMSbox: false,
    remainSec: 0,
    repeatedSMS: false,
    signInDisabled: true,
    clearErrorTimeout: null,
  }),
  components: {
    customInput,
    customButton,
  },
  computed: {
    errorMsg() {
      return this.$store.state.errorMsg;
    },
    phoneCheck() {
      return this.$store.state.phoneCheck;
    },
    remainSecText() {
      if (this.remainSec) {
        return `Отправить SMS с новым кодом ${this.remainSec} сек`;
      }
      if (this.repeatedSMS) {
        return "Отправить SMS повторно";
      }
      return "Отправить SMS с новым кодом";
    },
  },
  methods: {
    randomString() {
      return Math.random().toString(36).substring(2);
    },
    setTimer() {
      if (this.remainSec > 0) {
        setTimeout(() => {
          this.remainSec -= 1
          this.setTimer()
        }, 1000);
      } else {
        this.repeatedSMS = true
      }
    },
    showSMSboxButton() {
      this.showSMSbox = true;
      const wrapBox = document.querySelector(".wrap");
      setTimeout(() => {
        if (wrapBox.offsetHeight + 20 >= window.innerHeight) {
          wrapBox.style.padding = 0;
        }
      }, 100);
    },
    changePhone(phone) {
      if (this.isPhoneError) {
        this.isPhoneError = false;
      }
      if (regTell.test(phone)) {
        this.$store.dispatch('__setPhoneCheck', false);
      }
      const cleanedPhone = phone.replace(/[^0-9]/gim, '');
      if (phone !== cleanedPhone && cleanedPhone === this.phone) {
        this.phoneKey = this.randomString();
        this.$nextTick(() => {
          this.$refs.phoneInput.focusInput();
        });
      }
      this.phone = cleanedPhone;
      if (regTell.test(cleanedPhone)) {
        const noCountryCodePhone = cleanedPhone.charAt(0) === '8' || cleanedPhone.charAt(0) === '7' ? cleanedPhone.substring(1).replace('+7', '') : cleanedPhone.replace('+7', '');
        if (noCountryCodePhone.length >= 0 && noCountryCodePhone.length <= 14) {
          const formattedPhone = noCountryCodePhone.replace(regGrouping, "($1) $2-$3");
          this.phone = formattedPhone;

          if (this.phone.length === 14) {
            this.$store.dispatch("get_post_request", {
              url: "auth/signup",
              data: {
                phone: `7${formattedPhone.replace(/[^0-9]/gim, '')}`,
              },
            });
          }
        }
      } else if (cleanedPhone.length >= 15) {
        this.isPhoneError = true;
      }
    },
    checkPhone() {
      this.isPhoneError = !regTell.test(this.phone);
    },
    changeSmsCode(smsCode) {
      if (this.isSmsCodeError) {
        this.isSmsCodeError = false;
      }
      this.smsCode = smsCode;
      this.signInDisabled = !regSMS.test(smsCode);
    },
    checkSmsCode() {
      this.isSmsCodeError = !regSMS.test(this.smsCode);
    },
    getCode() {
      this.$store.dispatch("get_post_request", {
        url: "auth/login",
        data: {
          phone: `7${this.phone.replace(/[^0-9]/gim, '')}`,
          code: this.smsCode,
        }
      });
    },
    getNewCode() {
      this.$store.dispatch("get_post_request", {
        url: "auth/resend_code",
        data: {
          phone: `7${this.phone.replace(/[^0-9]/gim, '')}`,
        },
      });
    },
  },
  watch: {
    errorMsg() {
      if (this.clearErrorTimeout) {
        clearTimeout(this.clearErrorTimeout);
      }
      this.clearErrorTimeout = setTimeout(() => {
        this.$store.dispatch("clearErrorMsg");
      }, 3000);
    },
  },
};
</script>

<style lang="scss">
.login-box {
  width: 100%;
  height: 100%;

  .wrap {
    width: 100%;
    min-height: 100%;
    margin: 4em 0 0 0;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;

    .error-event {
      width: 100%;
      color: var(--red-dark-fon);
      text-align: center;
    }

    .box-title {
      margin-bottom: 2em;
      display: flex;
      width: 100%;
      align-items: center;
      justify-content: center;

      .logo {
        margin: 0 0.5em 0 0;
        display: inline-block;
        width: 50px;
      }

      .context {
        color: var(--white-text);
        display: inline-block;
        width: fit-content;

        .title {
          font-size: 1.8em;
          font-family: "myriadBold";
        }

        .desck {
          font-size: 0.6em;
          font-family: "myriadRegular";
        }
      }
    }

    .form,
    .sms-box {
      color: var(--white-text);
      width: 100%;
      display: flex;
      justify-content: center;

      .form-box {
        display: flex;
        align-items: center;
        flex-direction: column;
        justify-content: space-around;
        height: 100%;
        width: 90%;

        .timer-sms {
          font-size: 1.1em;
          font-family: "myriadRegular";
          color: var(--dark-grey);
        }

        .sms-button {
          font-size: 0.9em;
        }
      }

      .number {
        font-family: "myriadRegular";
        font-size: 2em;
        margin: 0 0 1em 0;
      }

      .sms-two {
        color: var(--red-dark-fon);
        width: 100%;
        font-size: 1.1em;
        text-align: center;
      }
    }
  }

  .sign-in__button {
    margin-top: 1em;
  }
}
</style>
