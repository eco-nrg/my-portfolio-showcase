<template>
  <client-only>
    <div class="charging">
      <table>
        <tbody>
          <tr>
            <td>

              <div class="cell-table">
                <div class="connector h2">
                  <div class="img" :class="['AV', { 'loading-x2': !sessionCharging.connector_type }]"
                    v-html="connectorsSVG(sessionCharging.connector_type)"></div>
                  <div class="conn-type" :class="{ 'loading': !sessionCharging.connector_type }">
                    {{ sessionCharging.connector_type }}
                  </div>
                </div>

                <div v-for="(connector, index) in listRefillSpaces.connectors" :key="index" class="red">
                  <div v-if="connector.type === sessionCharging.connector_type">
                    {{ connector.phases_count }} фазы {{ connector.current_a }}А {{ connector.power_kw }}кВт/ч макс.
                  </div>
                </div>
              </div>

            </td>
            <td>

              <div class="cell-table">
                <div :class="{ 'loading': !listRefillSpaces?.price_kwh }">
                  1 кВт/ч = <span class="money green">{{ listRefillSpaces.price_kwh }}</span>
                </div>
                <div :class="{ 'loading': !listRefillSpaces?.price_parking }">
                  простой = <span class="green">{{ listRefillSpaces.price_parking }} &#8381;/ч</span>
                </div>
                <div class="red">
                  При токе заряда менее {{ sessionCharging.idle_amperage_threshold }}А дополнительно начисляется оплата за простой.
                </div>
              </div>

            </td>
          </tr>

          <tr>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  <span v-if="sessionCharging?.start_payed">Прошло времени</span>
                  <span v-else>Осталось времени</span>
                </h3>
                <p class="h2">
                  {{ timer }}
                </p>
              </div>

            </td>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  Сумма,
                  <span class="money green"></span>
                </h3>
                <p class="h2" :class="{ 'loading': !sessionCharging?.cash?.toFixed(2) }">
                  {{ sessionCharging?.cash?.toFixed(2) }}
                </p>
              </div>

            </td>
          </tr>

          <tr>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  Использовано, <span class="green">кВт</span>
                </h3>
                <p class="h2" :class="{ 'loading': !sessionCharging?.total_kwh?.toFixed(2) }">
                  {{ sessionCharging.total_kwh?.toFixed(2) }}
                </p>
              </div>

            </td>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  Текущий ток, <span class="green">А</span>
                </h3>
                <p class="h2" :class="{ 'loading': !sessionCharging?.am?.toFixed(2) }">
                  {{ sessionCharging.am?.toFixed(2) }}
                </p>
              </div>

            </td>
          </tr>

          <tr>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  Текущая мощность, <span class="green">кВт/ч</span>
                </h3>
                <p class="h2" :class="{ 'loading': !sessionCharging?.current_kwh?.toFixed(2) }">
                  {{ sessionCharging.current_kwh?.toFixed(2) }}
                </p>
              </div>

            </td>
            <td>

              <div class="cell-table">
                <h3 class="red">
                  Текущее напряжение, <span class="green">В</span>
                </h3>
                <p class="h2" :class="{ 'loading': !sessionCharging?.current_v?.toFixed(2) }">
                  {{ sessionCharging.current_v?.toFixed(2) }}
                </p>
              </div>

            </td>
          </tr>
        </tbody>
      </table>

      <div class="camm">
        <div class="box-controll-camm">
          <img v-if="!showCamers" class="img" src="~/assets/move-icon.svg" alt="show/hide cammers">
          <customButton v-else-if="showCamers" value="X" @get="showCamers = !showCamers" type="normal" />

          <customButton value="cam.1" v-if="isCamera(1)" @get="changeCamm(1)" type="normal"
            :class="{ 'visited': isActive(1) }" />
          <customButton value="cam.2" v-if="isCamera(2)" @get="changeCamm(2)" type="normal"
            :class="{ 'visited': isActive(2) }" />
        </div>
        <div class="box-camm" v-show="showCamers">
          <div ref="fullScreen" class="fullScreen" @click="modeScreen">
            <img class="imgs" :src="choiceCam()" alt="loock camera" ref="camImg">
            <div class="responsive" ref="responsive">
              <img src="~assets/responsive.svg" />
            </div>
            <div class="tapScreen" ref="tap">
              <img src="~assets/tap.svg" />
            </div>
          </div>
        </div>
      </div>

      <customButton v-if="sessionCharging.status === 'ACT'" value="Завершить зарядку" @get="stopSession" type="attention" />
      <ContactUsButton />
    </div>
  </client-only>
</template>

<script>
import J1772 from "~/assets/connectors/j1772.svg?raw";
import IEC_62196 from "~/assets/connectors/iec_62196.svg?raw";
import TES_US from "~/assets/connectors/tesla_us.svg?raw";
import GB_T_AC from "~/assets/connectors/gb_t_ac.svg?raw";

import customButton from "~/components/customButton";
import ContactUsButton from "~/components/contactUsButton.vue";

export default {
  name: 'sessionChargingPage',
  components: {
    customButton,
    ContactUsButton,
  },
  data: () => ({
    reloadImg: false,
    lastImg: '',
    timer: 0,
    selected_camera: 1,
    reloadTimer: false,
    connectorSvg: {
      J1772,
      IEC_62196,
      TES_US,
      GB_T_AC,
    },
    showCamers: false,
  }),
  computed: {
    spaceId() {
      return parseInt(this.$route.params.id);
    },
    freeTime() {
      return this.$store.state.cashData.freeTime | 0;
    },
    listRefill() {
      return this.$store.state.listRefill;
    },
    listRefillSpaces() {
      return this.listRefill
      .map(item => item.station)
      .reduce((acc, it) => [...acc, ...it], [])
      .map(item => item.spaces)
      .reduce((ac, i) => [...ac, ...i], [])
      .find(item => item.id === parseInt(this.sessionCharging.id)) || { status: 'AV' };
    },
    sessionCharging() {
      return this.$store.state.sessionCharging;
    },
    sessionReceived() {
      return this.$store.state.sessionReceived;
    },
    getRefill() {
      const Id = parseInt(this.sessionCharging.id);
      return this.listRefill.map(refill =>
        refill.station.map(station =>
          station.spaces.map(spaces =>
            (spaces.id === Id ? { refilId: station.id, spacesId: spaces.id, name: spaces.name, status: spaces.status, addressFull: refill.name + " " + station.address } : undefined)
          )
        ).flat()
      ).flat().filter(item => item !== undefined)[0];
    }
  },
  methods: {
    choiceCam() {
      const img = this.sessionCharging[`cam_${this.selected_camera}`];
      if (this.lastImg !== img && img !== '')
        this.lastImg = img;

      return this.lastImg;
    },
    times() {
      const created_at = this.sessionCharging.created_at;
      const start_payed = this.sessionCharging.start_payed;

      if (!start_payed) {
        this.timer = this.secondsTo(this.freeTime - (Date.now() - created_at) / 1000);
      }
      else {
        this.timer = this.secondsTo((Date.now() - start_payed) / 1000);
      }
    },
    isActive(camId) {
      return this.selected_camera === camId && this.showCamers;
    },
    stopSession() {
      this.$store.dispatch(
        'setModal',
        {
          name: 'stopSessionModal',
        },
      );
    },
    isCamera(camId) {
      return this.sessionCharging[`cam_${camId}`]?.length > 0;
    },
    changeCamm(camId) {
      this.showCamers = true;
      this.selected_camera = camId;
      clearTimeout(this.reloadImg);
      this.reloadImg = setTimeout(this.axiosReloadImg, 1000);
    },
    secondsTo(date) {
      const d = Number(date);
      const h = Math.floor(d / 3600);
      const m = Math.floor(d % 3600 / 60);
      const s = Math.floor(d % 3600 % 60);
      const hour = (!parseInt(h / 10) ? '0' + h : h);
      const minuts = (!parseInt(m / 10) ? '0' + m : m);
      const seconds = (!parseInt(s / 10) ? '0' + s : s);

      return `${hour}:${minuts}:${seconds}`;
    },
    modeScreen() {
      const screenStyle = this.$refs.fullScreen;
      const tap = this.$refs.tap;

      if (!screenStyle.classList.contains('modeScreen')) {
        screenStyle.classList.add('modeScreen')
        tap.classList.add('screen')
      } else {
        screenStyle.classList.remove('modeScreen')
        tap.classList.remove('screen')
      }
    },
    connectorsSVG(type) {
      return this.connectorSvg[type]
    },
    axiosReloadImg() {
      if (this.selected_camera === 1) {
        this.$refs.camImg.setAttribute('src', `https://api.eco-nrg.store/media/camera/refill/${this.getRefill.refilId}.jpg?t=${Date.now()}`);
      } else {
        this.$refs.camImg.setAttribute('src', `https://api.eco-nrg.store/media/camera/space/${this.getRefill.spacesId}.jpg?t=${Date.now()}`);
      }
      clearTimeout(this.reloadImg);
      if (this.showCamers) {
        this.reloadImg = setTimeout(this.axiosReloadImg, 1000);
      }
    },
    checkSession() {
      if (!this.sessionReceived) {
        setTimeout(() => {
          this.checkSession();
        }, 200);
        return;
      }
      if (parseInt(this.sessionCharging?.id) !== this.spaceId) {
        this.$router.push('/profile');
      }
    },
  },
  created() {
    this.reloadTimer = setInterval(() => {
      this.times()
    }, 500);

    this.checkSession();
  },
  destroyed() {
    clearTimeout(this.reloadImg);
    clearTimeout(this.reloadTimer);
  }
}
</script>

<style lang="scss" scoped>
.charging {
  width: 100%;

  .box-loader {
    width: 100%;
    height: 80vh;
    display: flex;
    align-items: stretch;
    justify-content: center;
    background-color: #001145;
    position: relative;

    .loader {
      position: absolute;
      top: 40%;
      font-family: 'myriadRegular';
      text-shadow: 3px 1px var(--dark-blue);
    }
  }

  table {
    border-collapse: collapse;
    font-family: 'myriadRegular';
    font-size: 1.2em;
    width: inherit;

    tr {

      td {
        width: 50%;
        border: 2px solid var(--white-text);
        background-color: var(--dark-blue);

        .loading {
          min-width: 100px;
          height: 13px;
          background: var(--dark-blue);
          color: rgb(255 255 255 / 0%) !important;
          border: 3px solid rgba(255, 255, 255, 0);
          margin: 4px 0;
          border-radius: 4px;
          display: inline-block;

          div,
          span {
            color: rgb(255 255 255 / 0%) !important;
          }
        }

        .loading-x2 {
          min-width: 40px;
          height: 40px;
          background: var(--dark-blue);
          color: rgb(255 255 255 / 0%) !important;
          border: 3px solid rgba(255, 255, 255, 0);
          margin: 4px 0;
          border-radius: 4px;
          display: inline-block;
        }

        .cell-table {
          width: fit-content;
          padding: .8rem 1rem;
          display: flex;
          justify-content: flex-start;
          align-items: flex-start;
          flex-flow: column wrap;
          font-size: .8em;

          .h2 {
            font-size: 1em;
          }

          .connector {
            width: 100%;
            display: flex;
            justify-content: space-between;

            .img {
              margin-right: 10px;
            }
          }

          .red {
            color: var(--red-dark-fon);
            font-size: .8em;
          }

          .green {
            color: var(--green-dark-fon);
          }

        }
      }

      td:first-child {
        border-right: 4px solid var(--white-text);
      }
    }
  }

  .camm {
    width: 100%;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    padding-top: 20px;

    .box-controll-camm {
      display: flex;
      align-items: center;
      width: 100%;
      justify-content: space-evenly;
    }

    .box-camm {
      width: 100%;
      padding: 30px 0 10px;
      height: fit-content;
      display: flex;
      align-items: center;
      justify-content: center;

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
          animation: 1s linear .5s infinite alternate tap;
        }

        .screen {
          @media screen and (orientation:portrait) {
            right: calc(100% / 5);
            bottom: calc(100% / 3.2);
          }

          @media screen and (orientation:landscape) {
            right: calc(100% / 6);
            bottom: calc(100% / 12);
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

          @media screen and (orientation:portrait) {
            display: block;
          }

          @media screen and (orientation:landscape) {
            display: none;
          }
        }

        .imgs {
          border: 1px solid var(--blue);

          @media screen and (orientation:portrait) {
            height: calc(100vw - 4px);
          }

          @media screen and (orientation:landscape) {
            height: calc(100vh - 4px);
          }
        }

        @media screen and (orientation:portrait) {
          transform: rotate(90deg);
          margin: auto;
        }

        @media screen and (orientation:landscape) {
          width: 100%;
        }
      }

    }

    .img {
      height: 2.5em;
      margin: 0 0 auto 1em;
    }
  }

}
</style>
