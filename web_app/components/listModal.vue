<template>
  <!-- Modal window -->
  <div v-if="typeModal === 'alert'"><!-- Alert Modal Windows -->
    <!-- -->
    <CustomModal v-if="nameModal === 'showPayFail'" @closeModal="closeModal" class="box-modal-alert">
      <div slot="header">
        Упс!
      </div>
      <div slot="body">
        Не удалось пополнить баланс
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'profileFull'" @closeModal="closeModal" class="box-modal-alert">
      <div slot="body">
        <p>Данный сервис доступен только пользователям с заполненной анкетой!</p>
      </div>
      <div slot="footer">
        <customButton value="заполнить" type="action" @get="buttonClick($event, 'profileFull')" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'unavailable'" @closeModal="closeModal" class="box-modal-alert">
      <div slot="body">
        Данный сервис временно недоступен
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'spacerIsCharging'" @closeModal="closeModal" class="box-modal-alert">
      <div slot="body">
        <p>
          Вы уже поставили машину на зарядку.
        </p>
      </div>
      <div slot="footer">
        <customButton value="понятно" type="action" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'newTabOpen'" class="box-modal-alert">
      <div slot="body">
        <p>
          Закройте дублирующие вкладки.
        </p>
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'serverResponseExpected'" @closeModal="closeModal" class="box-modal-alert">
      <div slot="body">
        Сервер не доступен,<br />
        попробуйте чуть позже.
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="action" @get="buttonClick($event)" />
      </div>
    </CustomModal>
    <!-- Modal window to warn people about filling out their emails before topping up balance -->
    <CustomModal v-if="nameModal === 'notifyAboutEmailField'" class="box-modal-info" @closeModal="closeModal">
      <div slot="header">
        Поле email вашего профиля не заполнено
      </div>
      <div slot="body">
        <p class="center-text">
          Перед созданием платежа необходимо указать почту на которую будут отправляться фискальные чеки
        </p>
      </div>
      <div slot="footer">
        <CustomButton value="Добавить почту" type="normal" @get="buttonClick($event, 'notifyAboutEmailField')" />
      </div>
    </CustomModal>
    <!-- Modal window for user to fill in the email field -->
    <CustomModal v-if="nameModal === 'changeEmailField'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header">
        Заполните email
      </div>
      <div slot="body">
        <customInput placeholder="Email:" type="email" inputId="email" :value="email" @input="changeEmail"
                     :isError="isEmailError" errorMessage="Неверный формат почты" @blurInput="checkEmail"/>
      </div>
      <div slot="footer">
        <CustomButton value="Сохранить" type="normal" :disabled="isEmailError" @get="requestProfile" />
      </div>
    </CustomModal>
  </div>

  <div v-else-if="typeModal === 'chart'">
    <!-- -->
    <CustomModal v-if="nameModal === 'chart-modal'" @closeModal="closeModal" class="box-modal-chart">
      <div slot="header"></div>
      <div slot="body">
        <ChartSVG />
      </div>
      <div slot="footer"></div>
    </CustomModal>
    <!-- -->
  </div>

  <div v-else-if="typeModal === 'bonus'"><!-- Bonus Modal Windows -->
    <!-- -->
    <CustomModal v-if="nameModal === 'saveDateProfile'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        Данные успешно сохранены
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
  </div>


  <div v-else-if="typeModal === 'info'"><!-- Info Modal Windows -->
    <!-- -->
    <CustomModal v-if="nameModal === 'showPaySuccess'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header">
        Ура!
      </div>
      <div slot="body">
        <p class="green">Баланс пополнен, деньги поступят в ближайшее время!</p>
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'showBonusSuccess'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header">
        Ура!
      </div>
      <div slot="body">
        <p class="green">{{ dataModal }}</p>
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'terminalIsAvailable'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>Данный терминал свободен и готов к использованию вы можете его забронировать для зарядки электромобиля.</p>
      </div>
      <div slot="footer">
        <customButton value="Забронировать" type="action" @get="buttonClick($event, 'terminalIsAvailable')" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'terminalIsBusy'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>Терминал используется другим пользователем. Когда он освободится мы можем уведомить Вас по SMS</p>
      </div>
      <div slot="footer">
        <customButton value="Уведомить в SMS" type="action" @get="buttonClick($event, 'terminalIsBusy', dataModal)" />
        <customButton value="Ok" type="normal" @get="buttonClick($event)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'terminalIsOccupied'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>Терминал занят другим пользователем. Когда он освободится мы можем уведомить Вас по SMS</p>
      </div>
      <div slot="footer">
        <customButton value="Уведомить в SMS" type="action" @get="buttonClick($event, 'terminalIsOccupied', dataModal)" />
        <customButton value="Ok" type="normal" @get="buttonClick($event)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'terminalIsRegulatory'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>На данном терменале ведутся регламентные работы. Плановый запуск терминала
          <!-- <span class="time">21 Ноября 19:00.</span> -->
        </p>
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, 'terminalIsRegulatory')" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'terminalIsBooking'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>Вы забронировали другой терминал, что бы активировать этот необходимо отменить бронь на предыдущем.</p>
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'activateTerminal'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p>Активируйте услугу на свободном терминале</p>
      </div>
      <div slot="footer" class="connector-footer">
        <span v-for="conn in dataModal" :key="conn.space_id" :class="conn.status"
          @click="buttonClick($event, 'activateTerminal', conn)" v-html="conn.icon"></span>
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'booking'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header">
        Бронирование.
      </div>
      <div slot="body">
        <p>Услуга предоставляется авторизованным пользователям. Период брони 60 минут. В этом режиме терминал блокируется
          (статус индикатор терминала горит <u class="orang">оранжевым</u> ). Разблокировать его может только пользователь
          заказавший услугу. По прибытии на станцию пользователю необходимо отсканировать QR-код с экрана терминала и
          перейти по ссылке. В зависимости от статуса пользователя <b>оплата за данный сервис списывается через 15 или 30
            минут, для пользователей уровня 4 и 3 соответственно, а для уровней 2 и 1 услуга предоставляется
            бесплатно.</b> <span class="green">Цена услуги соответствует стоимости 1-го часа простоя станции.</span>
          Посмотреть стоимость простоя можно нажав кнопку с изображением нужного разъёма.</p>
      </div>
      <div slot="footer" class="connector-footer">
        <span v-for="spaces in dataModal" :key="spaces.space_id" :class="spaces.status" @click="buttonClick($event, 'booking')"
          v-html="spaces.icon"></span>
        <customButton value="Ok" type="normal" @get="buttonClick($event)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'session'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header"></div>
      <div slot="body">
        <div class="list">
          <span class="numeric-li">1</span>
          <p class="text-li">
            Выберите свободный терминал с нужным разъёмом
          </p>
        </div>
        <div class="list">
          <span class="numeric-li">2</span>
          <p class="text-li">
            Отсканируйте QR-код с экрана терминала
          </p>
        </div>
        <div class="list">
          <span class="numeric-li">3</span>
          <p class="text-li">
            Перейдите по ссылке
          </p>
        </div>
        <div class="list">
          <span class="numeric-li">4</span>
          <p class="text-li">
            Активируйте зарядку в WEB-приложении на вашем смартфоне
          </p>
        </div>
      </div>
      <div slot="footer"></div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'costSession'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <div class="details-session">
          <p>Бронь: {{ dataModal.cost_booking }} <span class="money"></span></p>
          <p>Простой: {{ dataModal.cost_idle }} <span class="money"></span></p>
          <p>Зарядка: {{ dataModal.cost_kw }} <span class="money"></span></p>
          <p class="fin-summ">Итого: <b>{{ dataModal.cost_total }}</b> <span class="money"></span></p>
        </div>
      </div>
      <div slot="footer">
        <customButton value="Понятно" type="normal" @get="buttonClick($event, false)" />
        <customButton value="График" type="alert" @get="buttonClick($event, 'chart-modal', dataModal.uuid)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'RequisitesChoise'" @closeModal="closeModal" class="box-modal-info requisites">
      <div slot="header">
        <h2 class="title">Наши реквизиты:</h2>
      </div>
      <div slot="body">
        <div class="info">
          <div class="repres">
            организация предоставляющая услуги
          </div>
          <div class="servic">
            обслуживающая организация
          </div>
        </div>
        <div class="command">
          <customButton value="Открыть" type="normal" @get="buttonClick($event, 'requisites-representative')" />
          <customButton value="Открыть" type="normal" @get="buttonClick($event, 'requisites-service')" />
        </div>
      </div>
      <div slot="footer">
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'requisites-representative'" @closeModal="closeModal"
      class="box-modal-info requisites check">
      <div slot="header">
        <h2 class="header">Организация предоставляющая услуги</h2>
      </div>
      <div slot="body" class="inform">
        {{ PROVIDING.name }}
        адрес: {{ PROVIDING.address }}
        ОГРН: {{ PROVIDING.ogrn }}
        ИНН: {{ PROVIDING.inn }}
        КПП: {{ PROVIDING.kpp }}
        {{ PROVIDING.branch_office }}
        {{ PROVIDING.pao }}
        БИК: {{ PROVIDING.bik }}
        р/с: {{ PROVIDING.correspondent_account }}
        к/с: {{ PROVIDING.payment_account }}
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-else-if="nameModal === 'requisites-service'" @closeModal="closeModal"
      class="box-modal-info requisites check">
      <div slot="header">
        <h2 class="header">Обслуживающая организация</h2>
      </div>
      <div slot="body" class="inform">
        {{ SERVICE.name }}
        адрес: {{ SERVICE.address }}
        ОГРН: {{ SERVICE.ogrn }}
        ИНН: {{ SERVICE.inn }}
        КПП: {{ SERVICE.kpp }}
        {{ SERVICE.branch_office }}
        {{ SERVICE.pao }}
        БИК: {{ SERVICE.bik }}
        р/с: {{ SERVICE.correspondent_account }}
        к/с: {{ SERVICE.payment_account }}
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'notChartData'" @closeModal="closeModal" class="box-modal-info">
      <div slot="body">
        <p class="justife">
          к сожалению, к данной сессии нет телеметрических данных
        </p>
      </div>
      <div slot="footer">
        <customButton value="Понятно)" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
    <!-- -->
    <CustomModal v-if="nameModal === 'serverResponseExpected'" @closeModal="closeModal" class="box-modal-info">
      <div slot="header">
        Дождитесь ответа от сервера
      </div>
    </CustomModal>
    <!-- -->
<!--    <NotifyAboutChargingEndModal v-if="nameModal === 'notifyAboutChargingEnd'" class="box-modal-info" />-->
    <CustomModal v-if="nameModal === 'notifyAboutChargingEnd'" class="box-modal-info" @closeModal="closeModal">
      <div slot="body">
        <notifyAboutChargingEnd />
      </div>
      <div slot="footer">
        <customButton value="Понятно" type="normal" @get="buttonClick($event, false)" />
      </div>
    </CustomModal>
  </div>
</template>

<script lang="js">
import ChartSVG from "~/components/chartSVG.vue";
import CustomModal from "~/components/customModal.vue";
import notifyAboutChargingEnd from "@/components/notifyAboutChargingEnd.vue";
import {regEmail} from "@/pages/profile/edit.vue";

export default {
  name: 'listModal',
  components: {
    ChartSVG,
    CustomModal,
    notifyAboutChargingEnd,
  },
  props: {
    nameModal: {
      type: String,
      default: ''
    },
  },
  data: () => ({
    PROVIDING: [],
    SERVICE: [],

    email: '',
    isEmailError: false,
  }),
  computed: {
    providersStation() {
      return this.$store.state.listRefill.map(ref => ref.station.map(station => station.providers)).flat(3).filter(item => item?.PROVIDING !== undefined || item?.SERVICE !== undefined)
    },
    bookSpace() {
      return this.$store.state.bookSpace;
    },
    dataModal() {
      return this.$store.state.dataModal;
    },
    typeModal() {
      return this.$store.state.typeModal;
    },
    email() {
      this.email = this.$store.state.profileData.email ?? '';
      return this.$store.state.profileData.email;
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
  },
  watch: {
    email(email) {
      this.email = email ?? '';
    }
  },
  methods: {
    closeModal() {
      this.$store.dispatch('closeModal');
    },
    buttonClick(e, event, data = null) {
      this.$emit('buttonEvent', { e, event, data });
    },
    changeEmail(email){
      this.email = email;
    },
    checkEmail(){
      this.isEmailError = !regEmail.test(this.email);
    },
    getFastKey() {
      return this.$store.getters.getKeyFastChoices
    },
    getSlowKey() {
      return this.$store.getters.getKeySlowChoices
    },
    requestProfile() {
      const profileSave = {
        phone: this.profileData.phone,
        first_name: this.profileData.first_name,
        middle_name: this.profileData.middle_name,
        email: this.email,
        manufacturer: this.carData.manufacturer,
        model: this.carData.model,
        number: this.carData.number,
        year: this.carData.year? parseInt(this.carData.year) : 2000,
        power: this.batteryData.power ? parseInt(this.batteryData.power) : 1,
        fast_type: Object.keys(this.getFastKey).find(key => this.getFastKey[key] === this.batteryData.fast_type) || '',
        slow_type: Object.keys(this.getSlowKey).find(key => this.getSlowKey[key] === this.batteryData.slow_type) || '',
        filledProfile: false,
      };

      console.log(JSON.stringify(profileSave));

      if (this.isData(profileSave)) {
        profileSave.filledProfile = true
      }

      this.$store.dispatch('onsubmit', {
        type: 'edit_profile',
        data: profileSave
      })
    },
    isData(data) {
      return Object.values(data).filter(i => i !== '' && i !== 0 && i !== NaN && i !== undefined).length > 10 ? true : false
    },
  },
  mounted() {
    if (process.client) {
      this.providersStation.forEach(item => {
        this.PROVIDING = item.PROVIDING
        this.SERVICE = item.SERVICE
      })
    }

  }
}
</script>

<style lang="scss" scoped>
.AV,
.DI,
.CH,
.BU,
.BO {
  width: auto;
  height: auto;
  cursor: pointer;
}

.text-details {
  display: flex;
  align-items: flex-end;
  font-size: 1.1em;
}

.details-session {
  display: flex;
  flex-direction: column;
  width: 80%;
  margin: 0 auto;
  font-style: normal;
  font-weight: 400;
  font-size: 20px;
  line-height: 24px;

  .money {
    color: var(--black-text);
    font-size: .9em;
    font-weight: 400;
  }

  .fin-summ {
    color: var(--orange-rad);

    .money {
      color: var(--orange-rad);
    }
  }
}

.center-text {
  width: 100%;
  text-align: center;
}

.justife {
  padding-top: 10px;
}

.money {
  color: var(--blue);
  font-weight: 900;
  font-size: 1.1em;
}

.orang {
  color: var(--orange-rad);
}

.green {
  color: var(--green-light-fon);
}

.list {
  display: table;
  margin-bottom: 0.4em;

  .numeric-li {
    font-size: 2em;
    color: var(--orange-rad);
    font-weight: 900;
    margin-right: 0.5em;
    margin-bottom: 0.4em;
  }

  .text-li {
    color: var(--dark-blue);
    font-size: 1.1em;
    display: table-cell;
    vertical-align: middle;
  }
}

.header-bonus {
  display: flex;
  width: 100%;
  flex-direction: column;
  align-items: center;

  .money {
    justify-self: self-end;
    width: fit-content;
    margin: 0 0 0 70px;
  }
}

.bonus {
  padding: 20px 0 0 0;
  display: flex;
  justify-content: space-evenly;
  align-items: center;

  &>p {
    width: 50%;
    padding: 0 1.4em 0 0;
    font-size: 1.2em;
  }

  .add-cash {
    width: fit-content;
    max-width: 110px;
    display: inline-flex;
  }
}
</style>
