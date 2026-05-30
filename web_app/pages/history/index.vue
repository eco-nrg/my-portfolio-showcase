<template>
  <div class="history">
    <div v-if="historyData" class="not-session">
      <h2 class="title">У&nbsp;вас&nbsp;еще&nbsp;не&nbsp;было сессии&nbsp;зарядки</h2>
      <h3 class="title">После&nbsp;завершения каждой&nbsp;сессии&nbsp;они будут&nbsp;показанны в&nbsp;этом&nbsp;окне.</h3>
    </div>

    <div class="box-history" :class="{ 'border-color': hist.status !== 'ACT' }" v-for="hist in filterBySession"
      :key="hist.uuid">
      <div class="title-box"
        :class="{ 'border': hist.show, 'active-session': hist.status === 'ACT', 'not-session': hist.status === 'NOM' }"
        @click="showContext(hist)">
        <div class="box-data-time">
          <span class="date">{{ getDate(hist.created_at)[0] }}</span>
          <span class="time">{{ getDate(hist.created_at)[1] }}</span>
        </div>
        <span class="city">{{ hist.lot.city }}</span>
      </div>

      <div class="context-box" v-show="hist.show">
        <div class="line-conn-add">
          <div class="left">
            <div class="icon-conn" v-html="iconCinnector(hist.connector_type)"></div>
            {{ hist.connector_type }}
          </div>
          <div class="right">
            {{ hist.lot.name }}
          </div>
        </div>

        <div class="context-title-box">
          <span>Длительность:</span>
          <span>Расход:</span>
        </div>

        <div class="line-conn-add">
          <div class="left">
            {{ secondsTo(hist.duration) }}
          </div>
          <div class="right">
            {{ hist.kw }} кВт
          </div>
        </div>

        <div class="context-title-box">
          <span>Стоимость:</span>
          <span>График:</span>
        </div>

        <div class="line-conn-add">
          <div class="left sum-chart" @click="showMSG(hist)">
            {{ hist.cost_total }}
          </div>
          <div class="right sum-chart" @click="getChart(hist)">
            Посмотреть
          </div>
        </div>

      </div>
    </div>
    <Loading :loading="!historyData && !history.length > 0" />
  </div>
</template>

<script leng="js">

import J1772 from "~/assets/connectors/j1772.svg?raw";
import IEC_62196 from "~/assets/connectors/iec_62196.svg?raw";
import TES_US from "~/assets/connectors/tesla_us.svg?raw";
import GB_T_AC from "~/assets/connectors/gb_t_ac.svg?raw";

export default {
  name: 'HistoryPage',
  data: () => ({
    connectors: {
      J1772,
      IEC_62196,
      TES_US,
      GB_T_AC,
    },
  }),
  computed: {
    historyData() {
      return this.$store.state.historyData;
    },
    history() {
      return this.$store.state.history;
    },
    filterBySession() {
      const arr = this.unionRelatedSessions(JSON.parse(JSON.stringify(this.history)));
      const index = arr.findIndex((item) => item.status === 'ACT');

      if (index > 0) {
        arr.splice(0, 0, arr.splice(index, 1)[0]);
      }
      return arr;
    },
  },
  methods: {
    getDate(timestamp) {
      const date = new Date(timestamp * 1000).toLocaleString([], { year: 'numeric', month: 'numeric', day: 'numeric' });
      const time = new Date(timestamp * 1000).toLocaleString([], { hour: '2-digit', minute: '2-digit' });
      return [date, time];
    },
    iconCinnector(type) {
      return this.connectors[type]
    },
    secondsTo(date) {
      let d = Number(date),
        h = Math.floor(d / 3600),
        m = Math.floor(d % 3600 / 60)
      if (d === 0)
        return '0ч 0м'
      return `${h}ч ${m}м`;
    },
    showContext(context) {
      if (context.status === 'FIN' || context.status === 'NOM' || context.status === 'FPR') {
        this.$store.dispatch("showContext", context)
      } else {
        this.$router.push(`/spaces/${context.space.id}`)
      }
    },
    showMSG(hist) {
      this.$store.dispatch(
        'setModal',
        {
          name: 'costSession',
          type: 'info',
          data: {
            cost_booking: hist.cost_booking,
            cost_idle: hist.cost_idle,
            cost_kw: hist.cost_kw,
            cost_total: hist.cost_total,
            uuid: hist.uuid,
          },
        },
      );
    },
    getChart(hist) {
      this.$store.dispatch(
        'onsubmit',
        {
          type: 'session_chart',
          data: {
            order_uuid: hist.uuid,
          },
        },
      )
    },
    // when user finishes charging session new parking session is initialized
    // and both of them written to history page as separate entities
    // here we combine them together
    unionRelatedSessions(sessions){
      let combinedSessions = [];
      const allowedTimeDelta = 60*2;

      let i = 0;
      while(i  < sessions.length) {
        if (
            i + 1 < sessions.length &&
            sessions[i].status === "FPR" &&
            sessions[i+1].status === "FIN" &&
            this.checkIfFromSameSpace(sessions[i], sessions[i+1]) &&
            this.checkTimeDeltaBetween(sessions[i], sessions[i+1], allowedTimeDelta)
        ) {
          let combinedSession = this.combineSessions(sessions[i], sessions[i+1]);
          combinedSessions.push(combinedSession);
          i++;
        }
        else {
          combinedSessions.push(sessions[i]);
        }
        i++;
      }

      return combinedSessions;
    },
    combineSessions(parkingSession, chargingSession){
      let cost_idle = parseFloat(parkingSession.cost_idle) + parseFloat(chargingSession.cost_idle);
      let cost_booking = parseFloat(parkingSession.cost_booking) + parseFloat(chargingSession.cost_booking);
      let cost_kw = parseFloat(parkingSession.cost_kw) + parseFloat(chargingSession.cost_kw);
      let cost_total = parseFloat(parkingSession.cost_total) + parseFloat(chargingSession.cost_total);
      let sessionClone = { ...chargingSession };

      sessionClone.cost_idle = cost_idle;
      sessionClone.cost_booking = cost_booking;
      sessionClone.cost_kw = cost_kw;
      sessionClone.cost_total = cost_total;
      sessionClone.duration = parkingSession.finished_at - chargingSession.created_at;
      sessionClone.created_at = chargingSession.created_at;
      sessionClone.finished_at = parkingSession.finished_at;

      return sessionClone;
    },
    checkIfFromSameSpace(parkingSession, chargingSession){
      return parkingSession.space.id === chargingSession.space.id;
    },
    checkTimeDeltaBetween(parkingSession, chargingSession, allowedTimeDelta){
      return (parkingSession.created_at - chargingSession.finished_at) <= allowedTimeDelta;
    },
  },
}
</script>

<style lang="scss" scoped>
.not-session {
  width: 70%;
  margin: 53px auto 0;

  .title {
    text-align: left;
    margin: 10px auto 0;

  }
}

.history {
  padding-top: 40px;
  text-align: center;
  font-family: "myriadRegular";

  .box-history {
    margin: 0 auto 10px;
    width: 90%;
    background-color: var(--white-text);
    border-radius: 10px;


    .title-box {
      width: calc(100% - 24px);
      margin: 0 0 0 -2px;
      background: var(--white-text);
      color: var(--black-text);
      padding: 10px 12px;
      font-style: normal;
      font-weight: 400;
      line-height: 20px;
      font-size: .9em;
      display: flex;
      justify-content: space-between;
      border-radius: 10px;
      border-left: 2px solid var(--blue);
      border-right: 2px solid var(--blue);
      cursor: pointer;


      .box-data-time {
        width: 50%;
        display: flex;
        justify-content: space-between;
        flex-basis: 50%;

        .time {
          color: var(--blue);
        }
      }

      .city {
        text-align: right;
        flex-basis: 50%;
      }

    }

    .border {
      border-bottom: 2px solid var(--blue);
    }

    .active-session {
      background-color: var(--orange-rad);
      color: var(--white-text);
      border: 2px solid var(--white-text);

      .time {
        color: var(--green-dark-fon) !important;
      }
    }

    .not-session {
      background-color: var(--light-grey);
      color: var(--white-text);

      .time {
        color: var(--dark-grey) !important;
      }
    }


    .context-box {
      background-color: var(--white-text);
      color: var(--black-text);
      border-radius: 0 10px 10px 10px;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      font-style: normal;
      font-weight: 400;
      font-size: 18px;
      line-height: 20px;
      text-align: right;
      color: var(--black-text);

      .line-conn-add {
        width: 100%;
        max-height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        align-items: stretch;

        .left {
          height: 100%;
          flex-basis: 50%;
          border-right: 1px solid var(--blue);
          padding: 4px 5px 4px 10px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
        }

        .right {
          flex-basis: 50%;
          border-left: 1px solid var(--blue);
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding: 4px 10px 4px 5px;
          cursor: pointer;
        }

        .sum-chart {
          font-style: normal;
          font-weight: 400;
          font-size: 18px;
          line-height: 20px;
          color: var(--orange-rad);
          text-decoration: underline;
        }
      }

      .context-title-box {
        height: 20px;
        background-color: var(--blue);
        color: var(--white-text);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 10px;
        font-style: normal;
        font-weight: 400;
        font-size: .9em;
        line-height: 20px;
      }


      .icon-conn {
        fill: var(--blue);
        max-width: 40%;
        width: 40px;
      }
    }
  }

  .border-color {
    border: 2px solid var(--blue);
  }


}
</style>
