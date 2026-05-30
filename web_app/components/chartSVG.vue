<template>
  <div class="chartSVG" ref="boxChart">
    <svg class="chart" xmlns="http://www.w3.org/2000/svg" :viewBox="`0 0 ${widthBox} ${heightBox}`" preserveAspectRatio="xMinYMin meet" @click="showLegend = !showLegend">
      <g class="center-chart">
        <rect class="area-green" :width="bookingArea[1]" :height="heightBox-20" x="3" y="0"/>
        <rect class="area-red" :width="widthBox-10" :height="getPositionAmper(3) - 10" x="0" :y="heightBox-getPositionAmper(3) - 10"/>
        <g class="zome-idle">
          <rect class="area-yellow" :width="zone.width" :height="heightBox-20" :x="zone.x" y="0" v-for="zone in idleZone"/>
        </g>

        <text class="start-time" x="30" y="40" stroke="none" >{{ startTime }}</text>
        <text class="end-time" :x="widthBox-90" y="40" stroke="none" >{{ endTime }}</text>

        <defs>
          <pattern id="p10" :width="getGredWidth()" :height="getGredHeight()" patternUnits="userSpaceOnUse">
            <path :d="`M  ${getGredWidth()} 0 L 0 0 0 ${getGredHeight()}`" fill="none" stroke="#989898" stroke-width="0.9"/>
          </pattern>
        </defs>
        <rect class="gred" :height="`${heightBox - 10}px`" :width="`${widthBox - 20}px`" fill="url(#p10)" />

        <g class="grid-amper" dominant-baseline="middle" text-anchor="right" font-weight="normal">
          <text x="0" :y="(index>0? getPositionAmper(index) : 10)" fill="#FEFEFE" v-for="(item, index) in pointAmper.slice().reverse()" :key="item+index" stroke="none" v-html="index>0 ? item : getToLine(item)"></text>
        </g>

        <g class="grid-time" dominant-baseline="middle" text-anchor="middle" ref="points" font-weight="normal">
          <text :x="(index<pointTime.length-1? getPositionTime(index) : widthBox-50)" :y="heightBox - 5" fill="#FEFEFE" stroke="none" v-for="(point, index) in pointTime" :key="index">{{ point }}</text>
        </g>

        <polyline
          :style="`transform: translate(20px, ${heightBox - 20}px) scale(1, -1);`"
          pathLength="10"
          fill="none"
          stroke="#00A3D3"
          stroke-dasharray=""
          stroke-dashoffset="0.00"
          stroke-width="2.5"
          points=""
          ref="polyline"/>

        <line x1="20" y1="0" x2="20" :y2="heightBox-20" stroke-width="2" stroke="#00A658"></line>
        <line :x1="parseInt(widthBox)-2" y1="0" :x2="parseInt(widthBox)-2" :y2="heightBox-20" stroke-width="2" stroke="#DD2A1B"></line>
      </g>
    </svg>

    <div class="legind" v-show="showLegend">
      <div class="leg">
        <div class="square green"></div>
        зона бронирования
      </div>
      <div class="leg">
        <div class="square red"></div>
        зона активации простоя
      </div>
      <div class="leg">
        <div class="square yellow"></div>
        зона простоя
      </div>
    </div>
  </div>
</template>

<script leng="js">

export default {
  name: 'chartSVG',
  components: {
  },
  data: () => ({
    bookingArea: 0,
    idleZone: [],
    showLegend: false,
    startTime: '',
    endTime: [],
    widthBox: 0,
    heightBox: 0,
    maxPoind: 12,
    pointTime: [],
    pointAmper: ['&nbsp;&nbsp;5', '10', '15', '20', '25', '30', '35', '&nbsp;&nbsp;', 'Ток A']
  }),
  computed:{
    chartHistory(){
      return this.$store.state.chartHistory
    }
  },
  methods:{
    getToLine(item){
      const text = item.split(' ')
      return `<tspan x="0" dy="0em">${text[0]}</tspan><tspan x="0.5em" dy="1em">${text[1]}</tspan>`
    },
    getGredWidth(){
      return Math.round(this.widthBox / this.maxPoind)
    },
    getGredHeight(){
      return Math.round(this.heightBox / this.pointAmper.length-1)
    },
    getPositionAmper(point){
      return (this.getGredHeight()  * point)
    },
    getPositionTime(point){
      return (this.getGredWidth()  * point) - 10
    },
    getDate(timestamp){
      let date = new Date(timestamp*1000).toLocaleString([], {year: 'numeric', month: 'numeric', day: 'numeric'}),
        time = new Date(timestamp*1000).toLocaleString([], {hour: '2-digit', minute: '2-digit'})
      return [date, time];
    },
    calculateZoneIdle(xValues, yValues) {
      this.idleZone = []
      const coordinates = [];
      const intervalWidth = (this.widthBox - 10) / xValues.length
      let startZone = null,
      chakZone = false;

      for (let i = 0; i < xValues.length; i++) {
        if(yValues[i] >= 20 || chakZone){
          chakZone = true
          if (yValues[i] < 15 && startZone === null) {
            startZone = i;
          } else if (yValues[i] >= 15 && startZone !== null) {
            coordinates.push({ x1: startZone * intervalWidth, x2: (i - 1) * intervalWidth });
            startZone = null;
          }
        }
      }

      if (startZone !== null) { // add zone for last segment
        coordinates.push({ x1: startZone * intervalWidth, x2: (xValues.length - 1) * intervalWidth });
      }

      coordinates.forEach(item => {
        this.idleZone.push({x: Math.round(item.x1), width: Math.round(item.x2 - item.x1)})
      })
    },
    calculatePoints(Xx, Yy) {
      const height = (this.heightBox-20)
      const numPoints = Xx.length
      const intervalWidth = (this.widthBox - 10) / numPoints
      const scale = height / (45.5 - Math.min(...Yy))
      const points = []

      for (let i = 0; i < numPoints; i++) {
        const x = i * intervalWidth;
        const y = Yy[i] * scale;
        points.push(`${x},${y}`);
      }

      return points.join(' ')
    },
    getTimeLabels(timeArray) {
      const timePeriod = Math.round(((timeArray[timeArray.length-1] - timeArray[0] ) / 60) / this.maxPoind)

      const labels = []
      let currTime = timeArray[0];
      while (currTime <= timeArray[timeArray.length-1] && labels.length < this.maxPoind) {
        labels.push(this.getDate(currTime)[1]);
        currTime += timePeriod * 60;
      }
      labels[labels.length-1] = 'время'
      
      return labels;
    },
    getOrientation(){
      return window.innerWidth > window.innerHeight ? "Landscape" : "Portrait"
    },
    init(){
      if(this.getOrientation() === 'Portrait'){
        this.widthBox = (window.innerHeight - 40)
        this.heightBox = (window.innerWidth / 1.2)
      } else {
        this.widthBox = (window.innerWidth - 80)
        this.heightBox = (window.innerHeight - 100)
      }

      const timeLine = this.chartHistory.labels,
        amperLine = this.chartHistory.current_a
      this.startTime = this.getDate(timeLine[0])[1]
      this.endTime = this.getDate(timeLine[timeLine.length-1])[1]
      this.pointTime = this.getTimeLabels(timeLine)
      this.calculateZoneIdle(timeLine, amperLine)
      this.$refs.polyline?.setAttribute('points', this.calculatePoints(timeLine, amperLine))
    }
  },
  mounted(){
    this.init()
    window.addEventListener('resize', this.init)
  },
  watch: {
    chartHistory:{
      handler: function(newVal, oldVal){
        if(newVal?.labels?.length !== oldVal?.labels?.length){
          this.init()
        }
      },
      deep: true,
      immediate: true,
    },
  }
}
</script>

<style lang="scss" scoped>
.chartSVG{
  position: relative;
  font-family: 'myriadRegular';
  color: var(--white-text);
  font-weight: 400;
  font-size: 1em;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  .chart{
    width: fit-content;
    height: fit-content;
   
    .area-green{
      fill: #328E2E80;
      transform: translate(20px, 0);
    }
    .area-red{
      fill: #FF000066;
      transform: translate(20px, 0);
    }
    .area-yellow{
      fill: #FFDC2766;
      transform: translate(20px, 0);
    }
    .center-chart{
      .gred{
        transform: translate(20px, 0);
      }
      .grid-amper{
        font-size: 0.6em;
        color: white;
      }
      .grid-time{
        font-size: 0.6em;
        color: white;
        transform: translate(30px, 0px);
      }
    }
    .start-time{
      font-size: 1.3em;
      fill: #00A658;
    }
    .end-time{
      font-size: 1.3em;
      fill: #DD2A1B;
    }
  }
  .legind{
    display: flex;
    justify-content: space-between;
    font-size: .8em;
    padding: 0 40px 0 0px;
    width: -webkit-fill-available;

    .square{
      min-width: 10px;
      min-height: 10px;
      display: inline-flex;
    }
    .green{
      background-color: #328E2E;
    }
    .red{
      background-color: #E52A12;
    }
    .yellow{
      background-color: #FFDC27;
    }
  }
}
</style>
