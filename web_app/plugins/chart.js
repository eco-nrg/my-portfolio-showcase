import Vue from 'vue'
import { Line } from 'vue-chartjs'

Vue.component('LineChart', {
  extends: Line,
  props: {
    data: {
      type: Object,
      required: true,
    },
    options: {
      type: Object,
      required: false,
      default: () => ({
        responsive: true,
        defaultFontColor: "#FFFFFF",
        maintainAspectRatio: false,
        legend: {
          display: true,
          position: 'bottom'
        },
        scales: {
          xAxes: [{
            position: 'bottom',
            gridLines: {
              color: '#676766',
              lineWidth: 0.5
            },
            scaleLabel: {
              fontSize: 12,
              fontColor: '#FFFFFF',
              display: true,
              labelString: 'время'
            }
          }],
          yAxes: [{
            position: 'left',
            gridLines: {
              color: '#676766',
              lineWidth: 0.5
            },
            scaleLabel: {
              fontSize: 12,
              fontColor: '#FFFFFF',
              display: true,
              labelString: 'ток А'
            }
          }]
        },

      }),
    },
  },
  watch: {
    data() {
      this.renderChart(this.data, this.options)
    },
  },
  mounted() {
    this.renderChart(this.data, this.options)
  },
})