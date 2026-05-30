<template>
  <div class="edit-profile">
    <div class="backPage" @click="back">
      <div class="icon">
        <div class="arrow"></div>
      </div>
      <div class="context">Вернутся</div>
    </div>

    <div class="wrapper">
      <h3>Личные данные</h3>
      <customInput placeholder="Номер тел.:" type="number" inputId="phone" ref="phoneInput"
        errorMessage="Неверный формат телефона" :inputKey="phoneKey" :value="phone" @input="changePhone"
        :isError="isPhoneError" @blurInput="checkPhone" />
      <customInput placeholder="Имя:" type="text" inputId="name" :value="name" @input="changeName" />
      <customInput placeholder="Отчество:" type="text" inputId="middle-name" :value="middleName"
        @input="changeMiddleName" />
      <customInput placeholder="Email:" type="email" inputId="email" :value="email" @input="changeEmail"
                   :isError="isEmailError" errorMessage="Неверный формат почты" @blurInput="checkEmail"/>
    </div>

    <div class="wrapper">
      <h3>Данные машины</h3>
      <customSelect type="search" ref="manufacturer" key="manufacturer" :options="listManufacturer"
        :value="carData.manufacturer" placeholder="Марка" class="customs" @get="saveData($event)" />
      <customSelect type="search" ref="model" key="model" :options="listModels" :value="cheiseModelBy(carData.model)"
        placeholder="Модель" class="customs" />
      <customInput placeholder='гос.Номер:' type="text" inputId="car-number" errorMessage="Неверный формат гос. номера"
        :value="carNumber" @input="changeCarNumber" :isError="isCarNumberError"/>
      <customSelect placeholder="Год выпуска:" type="number" ref="year" :key="yearKey" :value="year"
        :options="yearSelect" class="customs" />
    </div>

    <div class="wrapper">
      <h3>Данные батареи</h3>
      <customSelect placeholder="Емкость батареи:" type="number" ref="batteryPower" :key="powerKey"
        :value="power" :options="batteryPower" class="customs" />
      <customSelect type="search" ref="fastType" key="fast_type" :value="batteryData.fast_type" :options="fast_choices"
        placeholder="Быстрый тип" class="customs" />
      <customSelect type="search" ref="slowType" key="slow_type" :value="batteryData.slow_type" :options="slow_choices"
        placeholder="Медленный тип" class="customs" />
    </div>

    <customButton value="Сохранить" type="normal" :disabled="isPhoneError || isEmailError" @get="requestProfile" />
  </div>
</template>

<script>
import customInput from "~/components/customInput"
import customButton from "~/components/customButton"
import customSelect from "~/components/customSelect"

const regTell = /^7[489][0-9]{9}$/;
const regCarNumber = /^(а|в|е|к|м|н|о|р|с|т|у|х){1}[0-9]{3}(а|в|е|к|м|н|о|р|с|т|у|х){2}$/;
export const regEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default {
  meta: [
    {
      hid: 'robots',
      name: 'robots',
      content: 'noindex',
    }
  ],
  components: {
    customInput,
    customButton,
    customSelect,
  },
  data: () => ({
    phone: '',
    phoneKey: 'phone',
    isPhoneError: false,
    isEmailError: false,
    name: '',
    middleName: '',
    email: '',
    carNumber: '',
    isCarNumberError: false,
    selectModel: '',
    yearKey: 'car',
    powerKey: 'power'
  }),
  computed: {
    batteryPower() {// Список вольт от 1 Квт до 150 Квт
      return [...Array(150).keys()].map(i => ({ selected: false, value: `${i + 1} кВт` }));
    },
    yearSelect() {
      return [...Array(new Date().getFullYear() - 1999).keys()].map(i => ({ selected: false, value: 2000 + i }));
    },
    listModel() {
      return this.$store.state.listModel;
    },
    listModelAll() {
      return this.$store.state.listModelAll;
    },
    listModels() {
      return this.selectModel.length <= 0 ? this.listModelAll : this.listModel[this.selectModel]
    },
    listManufacturer() {
      return this.$store.state.listManufacturer
    },
    profileData() {
      this.phone = this.$store.state.profileData.phone ?? '';
      this.name = this.$store.state.profileData.first_name ?? '';
      this.middleName = this.$store.state.profileData.middle_name ?? '';
      this.email = this.$store.state.profileData.email ?? '';
      return this.$store.state.profileData
    },
    carData() {
      this.carNumber = this.$store.state.carData.number ?? '';
      return this.$store.state.carData;
    },
    batteryData() {
      return this.$store.state.batteryData;
    },
    fast_choices() {
      return this.$store.state.fast_choices
    },
    slow_choices() {
      return this.$store.state.slow_choices
    },
    getFastKey() {
      return this.$store.getters.getKeyFastChoices
    },
    getSlowKey() {
      return this.$store.getters.getKeySlowChoices
    },
    power() {
      if (this.$store.state.batteryData.power) {
        this.powerKey = this.randomString();
        return `${this.$store.state.batteryData.power} кВт`;
      }
      return '';
    },
    year() {
      if (this.$store.state.carData.year) {
        this.yearKey = this.randomString();
        return this.$store.state.carData.year;
      }
      return '';
    },
  },
  methods: {
    randomString() {
      return Math.random().toString(36).substring(2);
    },
    changePhone(phone) {
      if (this.isPhoneError) {
        this.isPhoneError = false;
      }
      const cleanedPhone = phone.replace(/[^0-9]/gim, '');
      if (phone !== cleanedPhone && cleanedPhone === this.phone) {
        this.phoneKey = this.randomString();
        this.$nextTick(() => {
          this.$refs.phoneInput.focusInput();
        });
      }
      this.phone = cleanedPhone;
      if (cleanedPhone && !regTell.test(cleanedPhone) && cleanedPhone.length >= 15) {
        this.isPhoneError = true;
      }
    },
    checkPhone() {
      this.isPhoneError = !regTell.test(this.phone);
    },
    checkEmail(){
      this.isEmailError = !regEmail.test(this.email);
    },
    changeName(name) {
      this.name = name;
    },
    changeMiddleName(middleName) {
      this.middleName = middleName;
    },
    changeEmail(email){
      this.email = email;
    },
    changeCarNumber(carNumber) {
      this.carNumber = carNumber;
    },
    checkCarNumber() {
      this.isCarNumberError = !regCarNumber.test(this.carNumber);
    },
    cheiseModelBy(manufacturer) {
      const val = (this.selectModel.length > 0 ? ' ' : manufacturer)
      return val
    },
    saveData(e) {
      this.selectModel = e;
    },
    requestProfile() {
      const profileSave = {
        phone: this.phone,
        first_name: this.name,
        middle_name: this.middleName,
        email: this.email,
        manufacturer: this.$refs.manufacturer.$refs.input.value,
        model: this.$refs.model.$refs.input.value,
        number: this.carNumber,
        year: this.$refs.year.$refs.input.value ? parseInt(this.$refs.year.$refs.input.value) : 2000,
        power: this.$refs.batteryPower.$refs.input.value ? parseInt(this.$refs.batteryPower.$refs.input.value) : 1,
        fast_type: Object.keys(this.getFastKey).find(key => this.getFastKey[key] === this.$refs.fastType.$refs.input.value) || '',
        slow_type: Object.keys(this.getSlowKey).find(key => this.getSlowKey[key] === this.$refs.slowType.$refs.input.value) || '',
        filledProfile: false,
      };

      if (this.isData(profileSave)) {
        profileSave.filledProfile = true
      }

      // отправляем на сервер
      this.$store.dispatch('onsubmit', {
        type: 'edit_profile',
        data: profileSave
      })
    },
    isData(data) {
      return Object.values(data).filter(i => i !== '' && i !== 0 && i !== NaN && i !== undefined).length > 10 ? true : false
    },
    back() {
      this.$router.back()
    }
  },
  watch: {
    profileData(profileData) {
      this.phone = profileData.phone ?? '';
      this.name = profileData.first_name ?? '';
      this.middleName = profileData.middle_name ?? '';
      this.email = profileData.email ?? '';
    },
    carData(carData) {
      this.carNumber = carData.number ?? '';
    },
  }
}
</script>

<style lang="scss">
.edit-profile {
  width: 100%;


  .backPage {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: "myriadLight";
    font-size: 1.5em;
    margin: 10px 0 0 0;
    padding: 0 0 20px;

    .icon {
      position: relative;
      transform: rotate(180deg) translateX(-20px);
      width: 30px;
      height: 100%;
      cursor: pointer;

      .arrow {
        position: absolute;
        width: 80%;
        height: 4px;
        background-color: var(--white-text);
        box-shadow: 0 3px 5px var(--dark-fon);
        animation: arrow 700ms linear infinite;

        &:after,
        &:before {
          content: "";
          position: absolute;
          width: 60%;
          height: 4px;
          right: -2px;
          background-color: var(--white-text);
        }

        &:after {
          top: -4px;
          transform: rotate(45deg);
        }

        &:before {
          top: 4px;
          box-shadow: 0 3px 5px var(--dark-fon);
          transform: rotate(-45deg);
        }
      }

    }

    .box-img {
      width: 30px;
      padding: 16px 24px;
      cursor: pointer;
    }

    .context {
      width: 100%;
      text-align: center;
    }
  }

  .wrapper {
    width: 80%;
    display: flex;
    flex-direction: column;
    margin: 0 auto 20px;
    background-color: var(--white-text);
    border: 2px solid var(--blue);
    padding: 30px 20px;
    border-radius: 10px;

    .customs {
      margin-bottom: .5em;

      ::-webkit-input-placeholder {
        color: var(--light-grey);
      }

      :-moz-placeholder {
        color: var(--light-grey);
        opacity: 1;
      }

      ::-moz-placeholder {
        color: var(--light-grey);
        opacity: 1;
      }

      :-ms-input-placeholder {
        color: var(--light-grey);
      }

      ::-ms-input-placeholder {
        color: var(--light-grey);
      }

      ::placeholder {
        color: var(--light-grey);
      }
    }

    h3 {
      margin-bottom: 10px;
      font-family: 'myriadRegular';
      color: var(--black-text);
    }
  }
}
</style>
