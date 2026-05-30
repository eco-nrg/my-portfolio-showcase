<template>
  <main v-if="isAuthorized">
    <client-only>
      <ListModal :typeModal="typeModal" :nameModal="nameModal" @buttonEvent="eventClick" />
      <StartSessionModal v-if="nameModal === 'startSessionModal'" @startSession="startSession" :space="dataSpace" />
      <SpaceStatusModal v-if="nameModal === 'spaceStatusModal'" :status="dataSpace.status" />
      <PaymentModal v-if="nameModal === 'paymentModal'" />
      <StopSessionModal v-if="nameModal === 'stopSessionModal'" />
      <CardPaymentModal v-if="nameModal === 'cardPaymentModal'" />
      <NoMoneyModal v-if="nameModal === 'noMoneyModal'" />
      <TerminalBookedModal v-if="nameModal === 'terminalBookedModal'" />
      <ErrorModal v-if="nameModal === 'errorModal'" />
    </client-only>
    <menuHeader />

    <section>
      <nuxt />
    </section>
  </main>

  <main v-else-if="!isAuthorized">
    <client-only>
      <nuxt />
    </client-only>
  </main>
</template>

<script>
import J1772 from "~/assets/connectors/j1772.svg?raw";
import IEC_62196 from "~/assets/connectors/iec_62196.svg?raw";
import TES_US from "~/assets/connectors/tesla_us.svg?raw";
import GB_T_AC from "~/assets/connectors/gb_t_ac.svg?raw";

import menuHeader from "~/components/menuHeader";
import ListModal from "~/components/listModal.vue";
import StartSessionModal from "~/components/startSessionModal.vue";
import SpaceStatusModal from "~/components/spaceStatusModal.vue";
import CardPaymentModal from "~/components/cardPaymentModal.vue";
import ErrorModal from "~/components/errorModal.vue";
import StopSessionModal from "~/components/stopSessionModal.vue";
import PaymentModal from "~/components/paymentModal.vue";
import NoMoneyModal from "~/components/noMoneyModal.vue";
import TerminalBookedModal from "~/components/terminalBookedModal.vue";

export default {
  components: {
    menuHeader,
    ListModal,
    StartSessionModal,
    SpaceStatusModal,
    CardPaymentModal,
    ErrorModal,
    StopSessionModal,
    PaymentModal,
    NoMoneyModal,
    TerminalBookedModal,
  },
  head() {
    return {
      title: `${this.serverName}: ${this.titlePage}`,
      meta: [],
    }
  },
  data: () => ({
    dateRefill: {},//Данные станции из url
    getDateRefill: [],// Список данных станций
    connectorsSvg: {
      J1772,
      IEC_62196,
      TES_US,
      GB_T_AC,
    },
    isBooking: false,
  }),
  computed: {
    nameModal() {
      return this.$store.state.nameModal
    },
    typeModal() {
      return this.$store.state.typeModal
    },
    sessionCharging() {
      return this.$store.state.sessionCharging
    },
    titlePage() {
      switch (this.$route.path) {
        case "/profile":
          return "Профиль";
        case "/profile/pay-success":
          this.showPaySuccess()
          return "Профиль";
        case "/profile/pay-fail":
          this.showPayFail()
          return "Профиль";
        case "/profile/edit":
          return "Редактировать профиль";
        case "/refill":
          if (this.$route.query?.q) {
            return `Станция - ${this.$route.query?.q}`;
          }
          return "Станции";
        case "/refill/map":
          if (this.$route?.query?.spaces) {
            return `Станция: ${this.$route.query?.spaces}`;
          }
          return "Карта станций";
        case "/history":
          return "История зарядки";
        case "/history/transaction":
          return "Транзакции средств";
        case "/spaces":
          if (this.$route?.query?.id) {
            return `Станция - ${this.$route.query?.id}`;
          }
          return "";
        case "/payment":
          return "Платежи"

        default:
          if (this.$route.path.indexOf("spaces") > 0) {
            return "Сессия зарядки";
          }
          if (this.$route.path.indexOf("orders") > 0) {
            return "Детализация заказа";
          }
          return "404 Page not found";
      }
    },
    getRefill() {
      return this.$store.getters.getDateRefill || []
    },
    connectorsType() {
      return this.dateRefill?.connectors ? this.dateRefill?.connectors[0] : {}
    },
    dataSpace() {
      return {
        icon: this.connectorsSvg[this.connectorsType?.type],
        name: `терминал № ${this.dateRefill?.name}`,
        addres: this.dateRefill?.addressFull,
        type: `разъём: ${this.connectorsType?.type}, до ${this.connectorsType?.power_kw} кВт / ч.`,
        status: this.dateRefill?.status
      }
    },
    isAuthorized() {
      return !!this.$cookies.get("auth");
    },
    bookSpace() {
      return this.$store.state.bookSpace
    },
    serverName() {
      return process.env.API_SERVER_NAME.slice(0, process.env.API_SERVER_NAME.lastIndexOf("."))
    },
    chartHistory() {
      return this.$store.state.chartHistory
    },
    filledProfile() {
      return this.$store.state.filledProfile
    },
    errorMsg() {
      return this.$store.state.errorMsg;
    },
    sessionChargingAndDateRefill() {
      return {
        sessionCharging: this.sessionCharging,
        dateRefill: this.dateRefill,
      };
    },
    cashData() {
      return this.$store.state.cashData;
    },
  },
  methods: {
    choiseSpaces(id) {
      const Id = parseInt(id)
      this.dateRefill = this.getDateRefill.map(refill =>
        refill.station.map(station =>
          station.spaces.map(spaces =>
            (spaces.id === Id ? { id: spaces.id, name: spaces.name, status: spaces.status, connectors: spaces.connectors, addressFull: `${refill.name} ${station.address}` } : undefined)
          )
        ).flat()
      ).flat().filter(item => item !== undefined)[0]
    },
    startSession() {
      if (this.cashData.money < 0) {
        this.$router.replace("/");
        this.$store.dispatch(
          "setModal",
          {
            name: "noMoneyModal",
          },
        );
        return;
      }
      const id = this.$route.query?.id;
      this.$store.dispatch(
        "onsubmit",
        {
          type: "start_session",
          data: {
            id,
            type: this.connectorsType?.type,
          },
        },
      );
      this.$store.dispatch("closeModal");
    },
    getChart(hist) {
      this.uuidSelect = hist.uuid;

      this.$store.dispatch(
        "onsubmit",
        {
          type: "session_chart",
          data: {
            order_uuid: hist.uuid,
          },
        },
      )
    },
    eventClick(data) {
      switch (data.event) {
        case "chart-modal":
          this.$store.dispatch("closeModal");
          this.getChart({ uuid: data.data });
          break;
        case "terminalIsBusy":
          if (!this.filledProfile) {
            this.$store.dispatch(
              "setModal",
              {
                type: "alert",
                name: "profileFull",
              },
            );
          } else {
            this.$store.dispatch("closeModal");
          }
          break;
        case "profileFull":
          this.$store.dispatch("closeModal");
          this.$router.push("/profile/edit");
          break;
        case "activateTerminal":
          this.$store.dispatch("closeModal");
          this.$store.dispatch("setIsBooking", true);
          this.$store.dispatch(
            "onsubmit",
            {
              type: "book_space",
              data: {
                space_id: data.data.space_id,
                connector_type: data.data.type,
              },
            },
          )
          break;
        case "requisites-representative":
          this.$store.dispatch(
            "setModal",
            {
              type: "info",
              name: "requisites-representative",
            },
          );
          break;
        case "requisites-service":
          this.$store.dispatch(
            "setModal",
            {
              type: "info",
              name: "requisites-service",
            },
          );
          break;
        case "terminalIsAvailable":
          this.$store.dispatch("closeModal");
          this.$store.dispatch("setCommand", "booking");
          break
        case "notifyAboutEmailField":
          this.$store.dispatch("closeModal");
          this.$store.dispatch(
              "setModal",
              {
                type: "alert",
                name: "changeEmailField"
              }
          );
          break;

        default:
          this.$store.dispatch("closeModal");
          break;
      }
    },
    showPaySuccess() {
      this.$store.dispatch(
        "setModal",
        {
          name: "showPaySuccess",
          type: "info",
        },
      );
    },
    showPayFail() {
      this.$store.dispatch(
        "setModal",
        {
          name: "showPayFail",
          type: "alert",
        },
      );
    },
  },
  watch: {
    $route (to, from) {
      if (to.fullPath.includes('/spaces/') && this.sessionCharging.status === 'PAR') {
        this.$store.dispatch(
            'setModal',
            {
              name: 'notifyAboutChargingEnd',
              type: 'info',
            },
        )
      }
    },
    getRefill: {
      handler: function (newVal) {
        this.getDateRefill = newVal
        this.choiseSpaces(this.$route.query?.id)
      },
      deep: true,
      immediate: true,
    },
    bookSpace(newVal) {
      if (Object.keys(this.bookSpace).length && newVal?.space_id == this.$route.query?.id) {
        this.isBooking = true;
        this.$store.dispatch(
          "setModal",
          {
            name: "startSessionModal",
          },
        );
      }
    },
    chartHistory: {
      handler: function (newVal) {
        if (newVal && Object.keys(newVal).length > 0) {
          this.$store.dispatch(
            "setModal",
            {
              name: "chart-modal",
              type: "chart",
              data: {
                ...newVal,
              },
            },
          );

        }
      },
      deep: true,
    },
    errorMsg(errorMsg) {
      if (errorMsg && errorMsg.length > 0 && errorMsg.indexOf("войти") === -1) {
        this.$store.dispatch(
          "setModal",
          {
            name: "errorModal",
          },
        );
      }
    },
    sessionChargingAndDateRefill: {
      handler: function (sessionChargingAndDateRefill) {
        if (!this.$route.query?.id) {
          return;
        }
        const { sessionCharging, dateRefill } = sessionChargingAndDateRefill;
        if (sessionCharging?.id) {
          if (this.$route.query.id == sessionCharging.id) {
            this.$router.replace(`/spaces/${sessionCharging.id}`);
            return;
          }
          this.$store.dispatch(
            "setModal",
            {
              name: "spacerIsCharging",
              type: "alert",
            },
          );
          return;
        }
        if (dateRefill?.status === "AV" || dateRefill?.status === "BU") {
          this.$store.dispatch(
            "setModal",
            {
              name: "startSessionModal",
            },
          );
          return;
        }
        if (!this.isBooking) {
          this.$store.dispatch(
            "setModal",
            {
              name: "spaceStatusModal",
            },
          );
          return;
        }
      },
      deep: true,
    },
  },
  created() {
    if (process.client) {
      document.querySelector("meta[name='viewport']").setAttribute("content", `height=${window.innerHeight}px, width=${window.innerWidth}px, initial-scale=1.0`)
    }
  },
  mounted() {
    this.$store.dispatch("openWebsocket");
    var currentTabId = parseInt(Math.random() * 1000);
    localStorage.setItem("currentTabId", currentTabId);

    setInterval(() => {
      var newTabId = localStorage.getItem("currentTabId");
      if (currentTabId != newTabId) {
        (this.$route.path !== "/index" ? this.$router.replace("/index") : null);
        this.$store.dispatch(
          "setModal",
          {
            name: "newTabOpen",
            type: "alert",
          },
        );
        currentTabId = newTabId;
      }
    }, 300);
  },
}
</script>

<style lang="scss" scoped>
main {
  width: 100%;
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  user-select: none;

  &::after {
    background-color: var(--dark-blue);
    background: url("~assets/background-HD-blu.webp");
    background-size: cover;
    background-repeat: no-repeat;
    background-clip: padding-box;
    background-position: 30% 0;
    background-attachment: scroll;
    content: "";
    width: 100%;
    height: 100%;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: -1;
  }

  @keyframes lazyBackground {
    0% {
      opacity: 0;
    }

    100% {
      opacity: 1;
    }
  }

  section {
    color: var(--white-text);
    height: 100%;
    width: 100%;
    max-width: 100%;
  }
}
</style>
