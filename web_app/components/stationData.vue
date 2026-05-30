<template>
  <div class="station booking" v-if="keys === 'booking'">
    <div class="box-station" v-if="!isBookingStation()">
      <h2 class="title-station">БРОНИРОВАНИЕ</h2>
      <p class="messander-station" v-if="!isBooking">
        У Вас будет ЧАС, чтобы доехать до зарядной станции
      </p>
      <p class="context-station" v-if="!isBooking">
        Стоимость услуги будет ровна цене простоя 1-го часа соответствующего терминала.
      </p>
      <div class="preloader" v-if="isBooking">
        <img class="loading" src="~/assets/loader.svg" alt="" draggable="false" />
      </div>
      <div class="button-box">
        <customButton value="Далее" type="normal" @get="filledProf" />
        <customButton value="Подробнее" type="action" @get="openModalWithSpacesData('booking')" />
      </div>
    </div>

    <div class="box-station" v-else>
      <h2 class="title-station">БРОНИРОВАНИЕ</h2>
      <p class="messander-station">
        Терминал {{ bookSpace.connector_type }} забронирован
        <span class="timer">{{ timer }}</span>
      </p>
      <p class="context-station">
        Оплата взимается с 15 минуты бронирования, бронь снимается по истечении
        {{ getTimeBook() }} минут
      </p>
      <div class="button-box">
        <customButton value="Подробнее" type="normal" @get="openModalWithSpacesData('booking')" />
        <customButton value="Отменить" type="alert" @get="cancelBookings" />
      </div>
    </div>
  </div>

  <div class="station" v-else-if="keys === 'move'">
    <div ref="fullScreen" class="fullScreen" @click="modeScreen">
      <img class="imgs" :src="data.img" alt="cam-img" ref="camImg" draggable="false" />

      <div class="responsive" ref="responsive">
        <img src="~assets/responsive.svg" draggable="false" />
      </div>
      <div class="tapScreen" ref="tap">
        <img src="~assets/tap.svg" draggable="false" />
      </div>
    </div>
  </div>

  <div class="station" v-else-if="keys === 'map'">
    <div class="box-map">
      <nuxt-link :to="{ path: 'refill/map', query: { spaces: data.id } }">
        <img
          class="img"
          :src="data.img_map"
          alt="cam-map-img"
          usemap="#image"
          width="300px"
          height="400px"
          draggable="false"
        />
      </nuxt-link>
    </div>

    <div class="box-requisites">
      Наши реквизиты: <span class="lick-modal" @click="modalRequisitesChoise">открыть</span>
    </div>
  </div>

  <div
    class="station connector"
    v-else-if="!keys.indexOf('conn')"
    :style="{ 'background-color': backgroundColor[connectorData?.status] }"
  >
    <div class="box-station">
      <div class="connect-info">
        <p class="line-info">
          Статус:
          <u
            class="status"
            @click="openModalWithStatus('terminalIsRegulatory', connectorData?.status)"
          >
            <b>{{ textStatus[connectorData?.status] }}</b></u
          >
        </p>
        <p class="line-info">
          Разъём: <b>{{ connectorTitle[connector?.type] }}</b>
        </p>
        <p class="line-info">
          Мощность: до
          <b
            >{{ connector?.power_kw }}кВт, {{ connector?.current_a }}А,
            {{ connector?.phases_count }}Ф</b
          >
        </p>

        <table>
          <tr>
            <td>стоимость зарядки</td>
            <td>
              <span>
                <b> {{ connectorData?.price_kwh }} Р/кВт/ч </b>
              </span>
            </td>
          </tr>
          <tr>
            <td>стоимость простоя</td>
            <td>
              <span>
                <b>{{ connectorData?.price_parking }} Р/час</b>
              </span>
            </td>
          </tr>
        </table>
      </div>
      <p class="context-conn">
        Внимание!!! Если ток заряда падает ниже 15А (3,5кВт/ч) кроме стоимости электроэнергии
        начисляется оплата за простой
      </p>
    </div>
  </div>
</template>

<script leng="js">
import TES_US from "~/assets/connectors/tesla_us.svg?raw";
import IEC_62196 from "~/assets/connectors/iec_62196.svg?raw";
import J1772 from "~/assets/connectors/j1772.svg?raw";
import GB_T_AC from "~/assets/connectors/gb_t_ac.svg?raw";

import customButton from "~/components/customButton";

export default {
  name: "stationData",
  components: {
    customButton,
  },
  props: {
    keys: {
      type: String,
      default: "",
    },
    data: {
      type: Object,
      default: {},
    },
    connectorId: {
      type: Number,
      default: 1,
    },
  },
  data: () => ({
    connectorTitle: {
      TES_US: "TESLA US (NACT)",
      IEC_62196: "IEC62196 (TYPE II)",
      J1772: "J1772 (TYPE I)",
      GB_T_AC: "GB/T (AC)",
    },
    reloadImg: false,
    connector: {},
    connectorsSvg: {
      J1772,
      IEC_62196,
      TES_US,
      GB_T_AC,
    },
    orientation: "",
    reloadTimer: false,
    timer: "00:00",
  }),
  computed: {
    bookSpace() {
      return this.$store.state.bookSpace;
    },
    connectorsStation() {
      const connectors = this.data.spaces.map((space) => ({
        space_id: space.id,
        icon: this.connectorsSvg[space.connectors[0].type],
        status: space.status,
        position: space.position,
        type: space.connectors[0].type,
        bookedUntil: space.booked_until,
        myBooking: this.isBookingStation(),
      }));
      connectors.sort((a,b) =>
        a.position >= b.position ? 1 : -1
      )

      return connectors;
    },
    sessionChargingId() {
      return this.$store.state.sessionCharging?.id || 0;
    },
    connectorData() {
      const conn = this.data.spaces.filter((item) => item.id === this.connectorId)[0];
      if (conn) {
        if (conn.connectors[0]) {
          this.connector = conn.connectors[0];
        }
        return conn;
      }
    },
    filledProfile() {
      return this.$store.state.filledProfile;
    },
    backgroundColor() {
      return this.$store.state.backgroundStatusColor;
    },
    textStatus() {
      return this.$store.state.status;
    },
    modalNameByStatus() {
      return {
        BU: "terminalIsOccupied",
        CH: "terminalIsBusy",
        DI: "terminalIsRegulatory",
        AV: "terminalIsAvailable",
        BO: "terminalBookedModal",
      };
    },
    isBooking() {
      return this.$store.state.isBooking;
    },
  },
  methods: {
    modeScreen() {
      const screenStyle = this.$refs.fullScreen;
      const tap = this.$refs.tap;
      const responsive = this.$refs.responsive;

      if (!screenStyle.classList.contains("modeScreen")) {
        screenStyle.classList.add("modeScreen");
        tap.classList.add("screen");
      } else {
        screenStyle.classList.remove("modeScreen");
        tap.classList.remove("screen");
      }

      setTimeout(() => (responsive.style.display = "none"), 3000);
    },
    filledProf() {
      if (Object.keys(this.bookSpace).length <= 0) {
        this.openModalWithSpacesData("activateTerminal");
      } else {
        this.openModal("info", "terminalIsBooking");
      }
    },
    openModal(type, name) {
      this.$store.dispatch("setModal", {
        type,
        name,
      });
    },
    openModalWithSpacesData(name) {
      this.$store.dispatch("setModal", {
        type: "info",
        name,
        data: this.connectorsStation,
      });
    },
    openModalWithStatus(name, status) {
      if (status === "BO") {
        this.openModalWithSpacesData(this.modalNameByStatus[status]);
      } else {
        this.openModal("info", !!status ? this.modalNameByStatus[status] : name);
      }
    },
    axiosReloadImg() {
      this.$refs.camImg.setAttribute(
        "src",
        `https://api.eco-nrg.store/media/camera/refill/${this.data.id}.jpg?t=${Date.now()}`,
      );
      clearTimeout(this.reloadImg);
      this.reloadImg = setTimeout(this.axiosReloadImg, 1000);
    },
    modalRequisitesChoise() {
      this.$store.dispatch("setModal", {
        type: "info",
        name: "RequisitesChoise",
      });
    },
    millisecondsToTime(timestamp) {
      const date = new Date(timestamp);
      const minutes = `0${date.getMinutes()}`.slice(-2);
      const seconds = `0${date.getSeconds()}`.slice(-2);

      return `${minutes}:${seconds}`;
    },
    timerBook() {
      this.$store.dispatch("setIsBooking", false);
      const delta = this.bookSpace.until - Date.now() / 1000;
      if (delta > 0) {
        this.timer = this.millisecondsToTime(delta * 1000);
      } else {
        this.timer = "00:00";
        this.$store.dispatch("book_space_response", {});
      }
    },
    getTimeBook() {
      return (this.bookSpace.until - this.bookSpace.created_at) / 60;
    },
    cancelBookings() {
      this.timer = "00:00";
      this.$store.dispatch("book_space_response", {});
      this.$store.dispatch("onsubmit", {
        type: "cancel_bookings",
        data: {},
      });
    },
    isBookingStation() {
      return (
        Object.keys(this.bookSpace).length &&
        this.data.spaces.find((space) => space.id === this.bookSpace.space_id)
      );
    },
  },
  mounted() {
    if (this.isBookingStation()) {
      this.reloadTimer = setInterval(() => {
        this.timerBook();
      }, 500);
    }
  },
  watch: {
    keys(newVal) {
      if (newVal === "move" && this.data?.show) {
        this.reloadImg = setTimeout(this.axiosReloadImg, 1000);
      } else {
        clearTimeout(this.reloadImg);
        this.reloadImg = false;
      }
    },
    bookSpace(newVal) {
      if (
        Object.keys(newVal).length &&
        this.data.spaces.map((spaces) => spaces.id).includes(newVal.space_id)
      ) {
        this.reloadTimer = setInterval(() => {
          this.timerBook();
        }, 500);
      }
    },
    isBooking(newVal, oldVal) {
      if (newVal !== oldVal && newVal) {
        this.reloadTimer = setInterval(this.timerBook, 500);
      }
    },
  },
  updated() {
    this.orientation = window.orientation === 0 ? "v" : "h";

    let supportsOrientationChange = "onorientationchange" in window,
      orientationEvent = supportsOrientationChange ? "orientationchange" : "resize";

    window.addEventListener(
      orientationEvent,
      () => {
        this.orientation = window.orientation === 0 ? "v" : "h";
      },
      false,
    );
  },
  destroyed() {
    clearTimeout(this.reloadImg);
    clearTimeout(this.reloadTimer);
  },
};
</script>

<style lang="scss" scoped>
.title-modal {
  font-size: 1.2em;
  color: var(--blue);
}

.edit-profile {
  color: var(--red-dark-fon);
}

.body-modal {
  font-size: 0.7em;
  color: var(--blue);
  text-align: left;
  font-family: "myriadRegular";

  .orang {
    color: var(--orange-rad);
  }

  .green {
    color: var(--green-light-fon);
  }
}

.footer-modal {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
}

.station {
  color: black;
  display: flex;
  flex-flow: column wrap;
  align-items: center;
  overflow: hidden;

  a img {
    object-fit: contain;
  }

  .box-map {
    width: 100%;
    border-bottom: 3px solid var(--blue);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .box-requisites {
    height: 2.5em;
    font-family: "myriadRegular";
    color: var(--orange-rad);
    font-size: 1.2em;
    line-height: 1em;
    display: flex;
    align-items: center;

    .lick-modal {
      margin-left: 10px;
      color: var(--blue);
      text-decoration: underline;
    }
  }

  .fullScreen {
    width: 100%;
    height: 100%;
    cursor: pointer;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;

    .responsive {
      display: none;
    }

    .tapScreen {
      width: 30px;
      position: absolute;
      animation: 1s linear 0.5s infinite alternate tap;
    }

    .screen {
      @media screen and (orientation: portrait) {
        right: calc(100vh / 8);
        bottom: calc(100vh / 3.5);
      }

      @media screen and (orientation: landscape) {
        right: calc(100vw / 8.3);
        bottom: 5px;
      }
    }

    @keyframes tap {
      from {
        transform: scale(1.5);
      }

      to {
        transform: scale(1);
      }
    }
  }

  .modeScreen {
    position: fixed;
    top: 0;
    width: 100vh;
    height: 100%;
    z-index: 1;
    background: var(--dark-fon);

    .responsive {
      width: 60px;
      position: absolute;
      background: radial-gradient(var(--white-text), transparent 60%);
      border-radius: 50%;
      padding: 10px;

      @media screen and (orientation: portrait) {
        display: block;
      }

      @media screen and (orientation: landscape) {
        display: none;
      }
    }

    .imgs {
      border: 1px solid var(--blue);

      @media screen and (orientation: portrait) {
        height: calc(100vw - 4px);
      }

      @media screen and (orientation: landscape) {
        height: calc(100vh - 4px);
      }
    }

    @media screen and (orientation: portrait) {
      transform: rotate(90deg);
      margin: auto;
    }

    @media screen and (orientation: landscape) {
      width: 100%;
    }
  }

  .box-station {
    width: calc(100% - 32px);
    padding: 10px 16px;

    .img {
      width: 100%;
      height: 100%;
    }
  }
}

.booking {
  background-color: var(--light-grey);

  .title-station {
    font-family: "myriadBold";
    font-size: 1.6em;
    text-align: center;
  }

  .messander-station {
    color: var(--white-text);
    font-family: "myriadBold";
    display: flex;
    justify-content: space-between;
    padding: 0 20px;

    & > span {
      color: var(--green-dark-fon);
      font-size: 1.2em;
      padding: 2px 2px 10px;
      height: fit-content;
    }
  }

  .preloader {
    display: flex;
    justify-content: center;
    height: 100%;
    padding: 7.5px 0;

    img {
      height: 40px;
      animation: rotating 1.5s linear infinite;
    }

    @keyframes rotating {
      from {
        -webkit-transform: rotate(0deg);
        -o-transform: rotate(0deg);
        transform: rotate(0deg);
      }

      to {
        -webkit-transform: rotate(360deg);
        -o-transform: rotate(360deg);
        transform: rotate(360deg);
      }
    }
  }

  .context-station {
    padding: 0 6px;
  }

  .button-box {
    width: 100%;
    display: flex;
    padding: 20px 0 0 0;
    display: flex;
    justify-content: space-evenly;
  }

  .connector-button {
    margin-right: 10px;
    background-color: var(--dark-grey);
    padding: 0 12px;
    display: flex;
    align-items: center;
    border-radius: 6px;
    margin-bottom: 10px;
    justify-content: center;
  }

  .connector-footer {
    width: 70px;
    height: 70px;
    margin-right: 10px;
    background-color: var(--dark-grey);
    padding: 10px 6px 6px;
    display: flex;
    align-items: center;
    border-radius: 6px;
    margin-bottom: 10px;
  }
}

.connector {
  color: var(--white-text);
  font-family: "myriadRegular";
  font-size: 1.1em;

  .connect-info {
    width: 100%;

    .status {
      cursor: pointer;
    }

    table {
      margin: 10px auto;

      td {
        padding: 2px 4px;
      }
    }

    table,
    th,
    td {
      border: 1px solid var(--white-text);
      border-spacing: 0;
    }
  }
}
</style>
