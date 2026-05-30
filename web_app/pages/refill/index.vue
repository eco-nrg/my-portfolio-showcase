<template>
  <div class="list">
    <div class="title-select">
      <label class="title-city">выбрать город</label>
      <customSelect class="select-input" type="search" key="map" @get="getOptions($event)" :value="valueSelect"
        :options="optionsCity" placeholder="все" />
    </div>
    <client-only>
      <div class="stations">
        <div class="box-station" v-for="(refill, index) in listRefill" :key="index">
          <h1 class="box-title">{{ refill.name }}</h1>

          <div class="box-tabs" v-for="(station, index) in refill.station" :key="station.id"
            :class="{ 'active': station.show }">
            <h2 class="box-address">{{ station.address }}</h2>

            <div class="box-button">
              <div class="line-box">
                <div class="item-button" @click="setData('booking', station, index)"
                  :class="{ 'booking': showData.value === 'booking' && showData.address === station.address && station.show }">
                  <img class="img" src="~assets/booking-icon.svg" alt="booking-icon" draggable="false" />
                </div>
                <div class="item-button" @click="setData('move', station, index)"
                  :class="[{ 'map-move': showData.value === 'move' && showData.address === station.address && station.show }, { 'hide-button': !station.img_cam.length > 0 }]">
                  <img class="img" src="~assets/move-icon.svg" alt="move-icon" draggable="false" />
                </div>
                <div class="item-button" @click="setData('map', station, index)"
                  :class="[{ 'map-move': showData.value === 'map' && showData.address === station.address && station.show }, { 'hide-button': station.img_map.indexOf('None.png') !== -1 }]">
                  <img class="img" src="~assets/marker-icon.svg" alt="marker-icon" draggable="false" />
                </div>
                <div class="item-button" :class="setBackgroundConn(spaces)"
                  @click="setData('conn-' + spaces.id, station, index)" v-for="spaces in sortingSpaces(station.spaces)"
                  :key="spaces.id" :ref="'conn-' + spaces.id">

                  <div :class="[spaces.status, { 'double': doubleConnectors(spaces.connectors) }]"
                    v-html="getAllConnectors(spaces.connectors)"></div>
                </div>
              </div>
            </div>

            <div class="box-values" v-show="station.show">
              <stationData :keys="showData.value" :data="station" :connectorId="showData.id" />
            </div>
          </div>
        </div>
      </div>
    </client-only>
  </div>
</template>

<script lang="js">

import customSelect from "~/components/customSelect"
import stationData from "~/components/stationData"

/* connectors svg img */
import J1772 from "~/assets/connectors/j1772.svg?raw";
import IEC_62196 from "~/assets/connectors/iec_62196.svg?raw";
import TES_US from "~/assets/connectors/tesla_us.svg?raw";
import GB_T_AC from "~/assets/connectors/gb_t_ac.svg?raw";

import J1772IEC_62196 from "~/assets/connectors/j1772-iec_62196.svg?raw";
import J1772TES_US from "~/assets/connectors/j1772-tesla_us.svg?raw";
import IEC_62196J1772 from "~/assets/connectors/iec_62196-j1772.svg?raw";
import IEC_62196TES_US from "~/assets/connectors/iec_62196-tesla_us.svg?raw";
import TES_USJ1772 from "~/assets/connectors/tesla_us-j1772.svg?raw";
import TES_USIEC_62196 from "~/assets/connectors/tesla_us-iec_62196.svg?raw";
/* // connectors svg img */

export default {
  name: 'RefillListTab',
  async asyncData(context) {
    return {
      query: context.route.query.q
    }
  },
  components: {
    customSelect, stationData
  },
  data: () => ({
    stationDestroyed: {},
    showData: {},
    valueSelect: '',
    connectors: {
      TES_US,
      J1772,
      IEC_62196,
      GB_T_AC,
      "J1772-IEC_62196": J1772IEC_62196,
      "J1772-TES_US": J1772TES_US,
      "IEC_62196-J1772": IEC_62196J1772,
      "IEC_62196-TES_US": IEC_62196TES_US,
      "TES_US-J1772": TES_USJ1772,
      "TES_US-IEC_62196": TES_USIEC_62196,
    },
  }),
  computed: {
    listRefillAll() {
      return this.$store.state.listRefill
    },
    listRefill() {
      return this.$route.query?.q ? this.$store.state.listRefill.filter(item => item.name.toLowerCase() === this.$route.query.q?.toLowerCase()) : this.$store.state.listRefill
    },
    backgroundColor() {
      return this.$store.state.backgroundStatusColor;
    },
    optionsCity() {
      const query = this.$route.query?.q || '',
        arr = [{ value: 'все', selected: query.length ? false : true }]

      this.listRefillAll.forEach(item => {
        arr.push({ value: item.name, selected: query.toLowerCase() === item.name.toLowerCase() });
      })
      return arr
    },
    bookSpace() {
      return this.$store.state.bookSpace;
    },
    command() {
      return this.$store.state.command;
    },
  },
  methods: {
    sortingSpaces(arr) {
      if (arr.length > 1) {
        let tmp = [...arr]
        return tmp.sort((a, b) => {
          if (a.position >= b.position) return 1
          else return -1
        })
      }
      return arr
    },
    doubleConnectors(conn) {
      return conn.length > 1
    },
    getAllConnectors(svg) {
      if (svg.length === 1)
        return this.connectors[svg[0].type]
      else {
        const arr = []
        for (const i in svg) {
          arr.push(svg[i].type)
        }
        return this.connectors[arr.join('-')];
      }
    },
    setBackgroundConn(spaces) {
      return this.showData.id === spaces.id ? spaces.status + '-back' : ''
    },
    setData(id, station, index) {
      const active = index === this.showData.index;
      const spaces = station.spaces.find(item => item.id === parseInt(id.replace(/\D/g, '') || 0, 10))

      Object.values(this.$refs).map(item => {
        if (item[0]) {
          item[0].classList.remove('DI-back', 'AV-back', 'CH-back', 'BU-back', 'BO-back')
        }
      })

      if ((this.showData.address !== station.address) || (this.showData.address === station.address && this.showData.value === id && this.showData.id === parseInt(id.replace(/\D/g, '') || 0, 10)) || (!station.show && active)) {
        this.$store.dispatch('__setShowStation', station)
      }

      this.stationDestroyed = station
      this.showData = {}
      this.showData.active = active
      this.showData.index = index
      this.showData.address = station.address
      this.showData.id = parseInt(id.replace(/\D/g, '') || 0, 10)
      this.showData.value = id
      this.showData.class = spaces?.status

      if (active && station.show) {
        if (parseInt(id.replace(/\D/g, '') || 0, 10)) {
          this.$refs[id][0].classList.add(this.setBackgroundConn(spaces))
        }
      }
    },
    getOptions(e) {
      if (e === undefined) return

      if (e?.value && e?.value !== 'все') {
        this.$router.push({ query: { q: e.value } })
        this.valueSelect = e.value
      } else if (typeof e === 'string' && e !== 'все') {
        this.$router.push({ query: { q: e } })
        this.valueSelect = e
      } else {
        this.$router.push('refill')
      }
    },
  },
  mounted() {
    if (this.listRefillAll.map(ref => ref.station.map(station => station.spaces.find(spaces => spaces.id === this.bookSpace.space_id)).filter(item => item != undefined)).filter(item => item.length).flat(2).length) {
      this.showData.active = false
      this.showData.index = 0
      this.showData.id = 0
      this.showData.value = "booking"
      this.stationDestroyed = this.showData
    }
  },
  destroyed() {
    this.$store.dispatch('__setShowStation', this.stationDestroyed)
  },
  created() {
    this.getOptions(this.$route.query?.q)
  },
  watch: {
    command(newValue) {
      if (newValue && newValue.length > 0) {
        this.setData(newValue, this.stationDestroyed, this.showData.index)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.list {
  width: 100%;
  height: 100%;

  .title-select {
    width: 100%;
    height: 2.6em;
    color: var(--white-text);
    font-family: "myriadRegular";
    display: flex;
    align-items: baseline;
    justify-content: space-evenly;
    font-size: 1em;
    padding: 20px 0 0 0;

    .title-city {
      margin: 0 auto;
    }

    .select-input {
      max-width: 60%;
    }
  }

  .stations {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    flex-wrap: nowrap;
    padding-top: 40px;

    .box-station {
      width: 100%;
      margin: 0 0 20px;

      .box-title {
        font-family: "myriadRegular";
        font-size: 1.6em;
        color: var(--orange-rad);
        margin: 0 auto 10px auto;
        max-width: 480px;
        padding: 0 0 0 10px;

      }

      .box-tabs::-webkit-scrollbar {
        width: 0;
        height: 0;
      }

      .box-tabs {
        height: fit-content;
        overflow: hidden;
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;


        border: 3px solid var(--orange-rad);
        border-radius: 6px;
        margin: 0 auto 20px;
        max-width: 486px;
        position: relative;


        .box-address {
          width: calc(100% - 32px);
          color: var(--dark-grey);
          background-color: var(--white-text);
          font-family: 'myriadRegular';
          font-size: 1.4em;
          padding: 6px 16px;
        }

        .box-button {
          width: 100%;
          overflow-x: auto;
          overflow-y: hidden;
          -ms-overflow-style: none;
          position: relative;
          background-color: var(--white-text);

          &::-webkit-scrollbar {
            width: .1px;
            height: .1px;
          }

          .double {
            width: 4em;
          }

          .line-box {
            border: none;
            /* width: max-content; */
            display: flex;

            .item-button {
              max-width: calc(100% / 6);
              background-color: var(--dark-grey);
              border-top: none;
              border-bottom: 1px solid var(--white-text);
              border-left: 1px solid var(--white-text);
              border-right: 1px solid var(--white-text);
              /* padding: 1em 1.5em; */
              padding: 0.55em 0.55em;
              display: flex;
              align-items: center;
              justify-content: center;
              cursor: pointer;
              float: left;

              .img {
                width: 2em;
                height: 2em;
              }
            }

            .hide-button {
              display: none;
            }

            .map-move {
              background-color: var(--blue) !important;
              border-bottom: 1px solid var(--blue) !important;
            }

            .booking {
              background-color: var(--light-grey);
              border-bottom: 1px solid var(--light-grey);
            }

            .DI-back {
              //Необслуживается
              background-color: var(--black-text) !important;
              border-bottom: 1px solid var(--black-text) !important;
            }

            .AV-back {
              //Свободно
              background-color: var(--green-light-fon) !important;
              border-bottom: 1px solid var(--green-light-fon) !important;
            }

            .CH-back {
              //Заряжается
              background-color: var(--blue-fon-button) !important;
              border-bottom: 1px solid var(--blue-fon-button) !important;
            }

            .BU-back {
              //Занято
              background-color: var(--conn-BU) !important;
              border-bottom: 1px solid var(--conn-BU) !important;
            }

            .BO-back {
              //Забронированно
              background-color: var(--conn-BO) !important;
              border-bottom: 1px solid var(--conn-BO) !important;
            }
          }

        }


        .box-values {
          width: 100%;
          overflow: hidden;
          background-color: var(--white-text);
          border: none;
        }

        .box-button .item-button:first-child {
          border-left: none;
        }

        .box-button .item-button:last-child {
          border-right: none;
        }
      }

      .active {
        border: 3px solid var(--blue);
      }
    }
  }
}
</style>
