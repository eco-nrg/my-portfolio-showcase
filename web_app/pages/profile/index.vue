<template>
  <div class="profile">
    <h2>ПРИВЕТСТВУЕМ В НАШЕЙ СЕТИ</h2>
    <aside v-if="showAlertMSG.page === $route.name">
      <alertBox :marker="showAlertMSG.icon">
        <p>
          {{ showAlertMSG.messanger }}
        </p>
      </alertBox>
    </aside>

    <div class="box box-bonus">
      <div class="wrap">
        <div class="box-line" :style="{ color: colorCash }">
          <span class="text">Баланс:</span>
          <span class="value cash">{{ cashData.money }}
            <span class="money"></span>
          </span>
        </div>
        <div class="box-line last" style="color: var(--blue);">
          <span class="text">Бонусы:</span>
          <span class="value">{{ cashData.bonus }}</span>
        </div>

        <openPaymentPageButton />
      </div>
    </div>


    <div class="box">
      <div class="wrap">
        <div class="box-line"><span class="text">Логин:</span> <span class="value">{{ formatTel(profileData.phone)
            }}</span>
        </div>
        <div class="box-line">
          <span class="text">Профиль:</span>
          <customButton :value="profileDatas[profileFill]" type="action" size="min"
            :classList="profileFill == 1 ? 'indicator-profile' : ''" @get="editProfile" />
        </div>

<!--        <div class="box-line" ref="boxLine">-->
<!--          <span class="text box-text-size" ref="line" :style="{ fontSize: fontSize }">Бесплатное время:</span>-->
<!--          <span class="value" ref="value">{{ secondsTo(cashData.freeTime) }}</span>-->
<!--        </div>-->

        <div class="box-line">
          <span class="text">Текущая сессия:</span>
          <span class="value">
            <customButton :type="isSessionChargeType" :value="isSessionChargeValue" @get="isSessionCharge" size="min" />
          </span>
        </div>
      </div>
    </div>

    <div class="box" v-if="isData(profileData)"><!-- box info profile -->
      <div class="wrap">
        <div class="box-line" v-if="profileData.first_name"><span class="text">Имя:</span><span class="value">{{
      profileData.first_name }}</span></div>
        <div class="box-line" v-if="profileData.middle_name"><span class="text">Отчество:</span><span class="value">{{
      profileData.middle_name }}</span></div>
        <div class="box-line" v-if="profileData.email"><span class="text">Email:</span><span class="value">{{
            profileData.email }}</span></div>
      </div>
    </div>
    <div class="box" v-if="isData(carData)"><!-- box info car -->
      <div class="wrap">
        <div class="box-line" v-if="carData.model"><span class="text">Модель:</span><span class="value">{{ carData.model
            }}</span></div>
        <div class="box-line" v-if="carData.manufacturer"><span class="text">Марка:</span> <span class="value">{{
      carData.manufacturer }}</span></div>
        <div class="box-line" v-if="carData.number"><span class="text">гос.Номер:</span><span class="value">{{
      carData.number }}</span></div>
        <div class="box-line" v-if="carData.year"><span class="text">год:</span><span class="value">{{ carData.year
            }}</span></div>
      </div>
    </div>
    <div class="box" v-if="isData(batteryData)"><!-- box info battery -->
      <div class="wrap">
        <div class="box-line" v-if="batteryData.power"><span class="text">Ёмкость:</span><span class="value">{{
      batteryData.power }} кВт/ч</span></div>
        <div class="box-line" v-if="batteryData.fast_type"><span class="text">Быстрый тип:</span> <span class="value">{{
      batteryData.fast_type }}</span></div>
        <div class="box-line" v-if="batteryData.slow_type"><span class="text">Медленный тпи:</span><span
            class="value">{{
      batteryData.slow_type }}</span></div>
      </div>
    </div>

    <div class="requisites box">
      <div class="wrap box-data">
        <h3 class="requis-title">
          Информационный сервис предоставляет:
        </h3>
        <div class="box-requisit">
          OOO {{ requisites?.name }}
          адрес: {{ requisites?.address }}
          ОГРН: {{ requisites?.ogrn }}
          ИНН: {{ requisites?.inn }}
          КПП: {{ requisites?.kpp }}
          Тел.:
          {{ requisites?.extra_information?.phone }}<br>
        </div>
        <a :href="'mailto:' + requisites?.extra_information?.email">{{ requisites?.extra_information?.email }}</a>
      </div>
    </div>

    <ContactUsButton />
    <customButton type="alert" value="Выход" @get="logout" />
    <Loading :loading="cashData.freeTime === undefined" />
  </div>
</template>

<script>
import alertBox from "~/components/alertBox";
import customButton from "~/components/customButton";
import Loading from "~/components/loading";
import ContactUsButton from "~/components/contactUsButton.vue";
import openPaymentPageButton from "@/components/openPaymentPageButton.vue";

export default {
  name: 'ProfilePage',
  components: {
    alertBox,
    customButton,
    Loading,
    ContactUsButton,
    openPaymentPageButton,
  },
  data: () => ({
    profileDatas: ['заполнить', 'продолжить', 'редактировать'],
    line: [],
    requisites: {},
  }),
  computed: {
    listRefill() {
      return this.$store.state.listRefill
    },
    isSessionChargeType() {
      if (this.$store.state.isSessionCharging) {
        return 'action';
      }
      if (Object.keys(this.bookSpace).length) {
        return 'attention';
      }
      return 'normal';
    },
    bookSpace() {
      return this.$store.state.bookSpace
    },
    isSessionChargeValue() {
      return this.$store.state.isSessionCharging ? 'активна' : (Object.keys(this.bookSpace).length ? 'бронь' : 'начать')
    },
    sessionCharging() {
      return this.$store.state.sessionCharging
    },
    alertMessanger() {
      return this.$store.state.alertMessanger
    },
    showAlertMSG() {
      let alert = {}
      for (const key in this.alertMessanger) {
        if (Object.hasOwnProperty.call(this.alertMessanger, key)) {
          const element = this.alertMessanger[key];
          if (element.page === this.$route.name) {
            alert = element
          }
        }
      }
      return alert
    },
    fontSize() {
      if (process.client) {
        return `${this.line[0]?.widthLine / this.line[0]?.textLength / (this.line[0]?.fontSizeLine / 1.9)}em` //".8em"
      }
    },
    profileFill() {
      const fill = ((this.isData(this.profileData) ? 1 : 0) + (this.isData(this.carData) ? 1 : 0) + (this.isData(this.batteryData) ? 1 : 0)) - 1
      return fill >= 0 ? fill : 0
    },
    cashData() {
      return this.$store.state.cashData;
    },
    profileData() {
      return this.$store.state.profileData
    },
    carData() {
      return this.$store.state.carData
    },
    batteryData() {
      return this.$store.state.batteryData
    },
    colorCash() {
      return this.$store.state.colorCash
    },
  },
  methods: {
    isSessionCharge() {
      if (this.sessionCharging?.id) {
        this.$router.push(`/spaces/${this.sessionCharging?.id}`);
      } else if (Object.keys(this.bookSpace).length) {
        const station = this.listRefill.map(ref => ref.station.map(station => station.spaces.filter(spaces => spaces.id == this.bookSpace.space_id)).filter(item => item.length > 0)).filter(item => item.length > 0).flat(3)[0];
        this.$store.dispatch('__setShowStation', station);
        this.$router.push(`/refill/`);
      } else {
        this.$store.dispatch(
          'setModal',
          {
            type: 'info',
            name: 'session',
          },
        );
      }
    },
    isData(data) {
      return Object.values(data).filter(i => i !== '' && i !== 0 && i !== null).length >= 3 ? true : false
    },
    secondsTo(date) {
      let d = Number(date),
        h = Math.floor(d / 3600),
        m = Math.floor(d % 3600 / 60),
        s = Math.floor(d % 3600 % 60)
      if (d === 0)
        return '0ч 0м 0с'
      return `${h}ч ${m}м ${s}с`;
    },
    editProfile() {
      this.$router.push('/profile/edit')
    },
    formatTel(value) {
      return value?.replace(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,4})/, "+$1 ($2) $3-$4")
    },
    logout() {
      this.$store.dispatch('onsubmit', {// отправляем на сервер
        type: 'logout',
        data: {},
      });
      this.$store.dispatch('__resetState');
    },
  },
  mounted() {
    if (process.client) {
      this.line.push({
        widthLine: this.$refs?.line?.clientWidth,
        fontSizeLine: parseFloat(window?.getComputedStyle(this.$refs?.line, null).getPropertyValue('font-size')),
        textLength: this.$refs?.line.innerText.length
      })
    }
  },
  async created() {
    if (process.client) {
      try {
        this.requisites = await this.$axios.$get(`${process.env.API_SERVER}/main/api/v1/legal_info`)
      } catch (error) {
        console.log(error);
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.bank-box {
  .text {
    min-height: 40px;
    padding: 0 9em 0 23px;
    text-align: justify;
    margin: 0 0 1em 0;
    color: var(--orange-rad);
    font-weight: normal;
    font-family: 'myriadRegular';
  }
}

.type-sum {
  width: 50%;
  min-height: 40px;
  text-align: left;
  margin: 0 0 1em 0;
  color: var(--orange-rad);
  font-weight: normal;
  font-family: 'myriadRegular';
}

.money {
  position: relative;
}

.money-modal {
  color: var(--green-light-fon);
}

.box-summ {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1em 0;

  .input-summ {
    max-width: 100px;
  }
}

.profile {
  color: var(--orange-rad);

  aside {
    margin-bottom: 1.6em;
  }

  &>h2 {
    text-align: center;
    font-size: 1.1em;
    font-family: "myriadBold";
    color: var(--white-text);
    line-height: 2.5em;
  }

  .box {
    color: var(--black-text);
    font-family: 'myriadRegular';
    font-size: 1em;
    user-select: none;
    background: var(--white-text);
    border-radius: 10px;
    border: 2px solid var(--red-dark-fon);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    width: 80%;
    color: var(--orange-rad);
    margin: 0 auto 30px auto;

    .wrap {
      width: calc(100% - 40px);
      margin: 10px 0 !important;

      .box-line {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;

        .value {
          font-size: 1.1em;
          min-width: fit-content;
          color: var(--black-text);
        }

        .cash {
          margin-right: 15px;
        }

      }

      .last {
        margin-bottom: 20px;
      }
    }

  }

  .box-bonus {
    font-family: 'myriadBold';

    .text {
      font-size: 1.2em;
    }

    .value {
      color: inherit !important;
      font-size: 1.2em;
    }
  }

  .requisites {
    // width: 100%;
    color: var(--black-text);
    font-size: 1.1em;
    font-family: 'myriadRegular';
    display: flex;
    align-items: center;
    justify-content: center;

    .box-data {
      text-align: start;
      padding: 2em 0;
      display: flex;
      flex-direction: column;
      user-select: text;


      .box-requisit {
        white-space: pre-line;
        text-align: left;
        padding-bottom: 20px;
        line-height: 1.2em;
      }

      a[href^="mailto:"] {
        color: var(--black-text);
        text-decoration: underline;
      }
    }
  }
}
</style>
