<template>
    <div class="slider">
      <div class="slider-wrapper">
        <div class="box-img active"  :ref="`slider-1`">
          <img :src="require(`~/assets/img/charging/${status}.jpg`)" :alt="status"/>
        </div>
        <div class="box-img" :ref="`slider-2`">
          <img :src="require(`~/assets/img/charging/conn-${chargingStation}.jpg`)" :alt="status"/>
        </div>
      </div>
    </div>
</template>

<script leng="js">
export default {
  name: 'CustomImg',
  data: () => ({
    timeout: false,
    activeSlider: {},
    activeIndex: 1,
    sliderIndex: 0,
  }),
  computed: {
    status() {
      return this.$store.state.response
    },
    chargingStation(){
      return this.$store.state.chargingStation
    },
    timerSlideChange(){
      return this.$store.state.timerSlideChange
    },
  },
  methods: {
    slider() {
      if (this.$refs.hasOwnProperty(`slider-${this.sliderIndex + 1}`)) {
        this.activeSlider = this.$refs[`slider-${this.sliderIndex + 1}`]
      }

      if (this.sliderIndex === 0) {
        this.activeSlider = this.$refs[`slider-${this.activeIndex}`]
        this.timeout = setTimeout(() => {

          if (this.activeIndex >= 2) {
            this.activeIndex = 1
          } else {
            this.activeIndex += 1
          }

          // console.log(1111111, Object.values(this.$refs));
          Object.values(this.$refs).forEach(item => {
            // console.log(11111111, item.classList );
            item.classList.remove('active')
          })

          this.$refs[`slider-${this.activeIndex}`].classList.add('active')

          this.slider()
        }, this.timerSlideChange);
      }
    }
  },
  mounted() {
    this.slider()
  },
  destroyed() {
    clearTimeout(this.timeout)
    this.timeout = false
  }
}
</script>

<style scoped lang="scss">
.slider {
  min-width: 100vw;
  min-height: 100vh;

  .slider-wrapper {
    position: relative;
    display: flex;
    justify-content: center;
    align-content: center;

    .box-img {
      position: absolute;
      width: 100vw;
      height: 100vh;
      opacity: 0;
      /* transition: opacity .5s ease; */
      display: flex;
      align-items: center;
      justify-content: center;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .active {
      display: block;
      opacity: 1;
    }
  }
}
</style>
