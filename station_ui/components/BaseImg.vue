<template>
  <div v-if="status === 'charging_start'" class="box-img">
    <div class="wrapp-grid">
      <img :src="require(`../assets/img/${status}/${ampers}`)" :alt="status" style="width: 100px; height: 100vh;" />

      <div>
        <p v-if="start_payed" >Прошло времени</p>
        <p v-else>Осталось времени</p>

        <span>{{ timer }}</span>
      </div>

      <div>
        Использовано, кВт:
        <span>{{ kWt.toFixed(2) }}</span>
      </div>

      <div>
        Ток, А:
        <span>{{ am.toFixed(2) }}</span>
      </div>

      <div>
        Мощность, кВт:
        <span>{{ Wt.toFixed(2) }}</span>
      </div>
    </div>
  </div>

  <div v-else-if="status !== 'charging_start'" class="box-img">
    <img preload :src="require(`~/assets/img/${status}.jpg`)" :alt="status"/>
  </div>
</template>

<script leng="js">
export default {
  name: 'baseImg',
  data: () => ({
    timer: 0,
    reloadTimer: false,
  }),
  computed: {
    // created_at: 1677832100000,//Время начала платной зарядки таймер считаем в перед -> Date.now() - start_payed title=Прошло времени
    // start_payed: null,// 1677833717912,//Время считаем в обратную сторону от state.cashData.freeTime -  (Date.now() - created_at) title=Осталось времени
    // freeTime: null || 1800 // Бесплатное время пользователя
    // total_kwh: 56.012,
    // am: 72.5,
    // current_kwh: 17.52,

    status() {
      return this.$store.state.response
    },
    am() {
      return this.$store.state.am
    },
    kWt() {
      return this.$store.state.total_kwh
    },
    Wt() {
      return this.$store.state.current_kwh
    },
    created_at(){
      return this.$store.state.created_at
    },
    start_payed(){
      return this.$store.state.start_payed
    },
    freeTime(){
      return this.$store.state.freeTime
    },
    ampers() {
      if (this.am <= 10) {
        return '0-10.gif'
      } else if (this.am <= 25 && this.am >= 11) {
        return '10-25.gif'
      } else if (this.am <= 30 && this.am >= 26) {
        return '25-30.gif'
      } else if (this.am <= 35 && this.am >= 29) {
        return '30-35.gif'
      } else if (this.am >= 36) {
        return '35-40.gif'
      }
    }
  },
  methods: {
    secondsTo(date) {
      let d = Number(date),
        h = Math.floor(d / 3600),
        m = Math.floor(d % 3600 / 60),
        s = Math.floor(d % 3600 % 60),
        hour = (!parseInt(h / 10) ? '0' + h : h),
        minuts = (!parseInt(m / 10) ? '0' + m : m),
        seconds = (!parseInt(s / 10) ? '0' + s : s)

      return `${hour}:${minuts}:${seconds}`;
    },
    times() {
      const created_at = this.created_at,
        start_payed = this.start_payed

      if (!start_payed)
        this.timer = this.secondsTo(this.freeTime - (Date.now() - created_at) / 1000)
      else
        this.timer = this.secondsTo((Date.now() - start_payed) / 1000)
    },
  },
  created(){
    this.reloadTimer = setInterval(() => {
      this.times()
    }, 500);
  }
}
</script>

<style scoped lang="scss">
.box-img {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .wrapp-grid {
    width: 100%;
    height: 100%;
    padding: 0 3.5%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-flow: wrap row;

    & div {
      width: 40%;
      height: 44%;
      background: #D1490F;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      font-size: 2em;
      font-family: Arial;

      span {
        font-size: 4rem;
      }
    }

    img {
      position: absolute;
      left: 0;
      right: 0;
      margin: 0 auto;
    }
  }
}
</style>
