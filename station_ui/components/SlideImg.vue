<template>
  <div class="slider">
    <div class="slider-wrapper">
      <div class="box-img" :ref="`slider-${slide}`" v-for="slide of sliderCounts" :key="slide"
        :class="{ 'active': slide == 1 }">
        <img :src="require(`~/assets/img/${status}/${slide}.jpg`)" :alt="`slide-${slide}`" />
      </div>
    </div>
  </div>
</template>

<script leng="js">
export default {
  name: 'SlideImg',
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
    timerSlideChange() {
      return this.$store.state.timerSlideChange
    },
    sliderCounts(){
      return this.$store.state.sliderCounts
    }
  },
  methods: {
    slider() {
      if (this.$refs.hasOwnProperty(`slider-${this.sliderIndex + 1}`)) {
        this.activeSlider = this.$refs[`slider-${this.sliderIndex + 1}`]
      }

      if (this.sliderIndex === 0) {
        this.activeSlider = this.$refs[`slider-${this.activeIndex}`]
        this.timeout = setTimeout(() => {
          if (this.activeIndex >= this.sliderCounts) {
            this.activeIndex = 1
          } else {
            this.activeIndex += 1
          }

          Object.values(this.$refs).forEach(item => {
            item[0]?.classList.remove('active')
          })

          // console.log(this.$refs);
          this.$refs[`slider-${this.activeIndex}`][0]?.classList.add('active')

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
