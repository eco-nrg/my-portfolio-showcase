<template>
  <div class="wrap">
    <!-- TEST RESPONSE SERVER -->
    <iframe v-if="mode" src="http://eco-station.tk:8000"></iframe>
    <!-- TEST RESPONSE SERVER -->

    <BaseImg v-if="getFormat.baseImg.includes(status)" />

    <SlideImg v-else-if="getFormat.slideImg.includes(status)" />

    <CustomImg v-else-if="getFormat.customImg.includes(status)" />
  </div>
</template>

<script leng="js">
export default {
  name: 'index',
  data: () => ({
    loopTimet: false
  }),
  computed: {
    mode() {
      return process.env.NODE_ENV === 'development'
    },
    status() {
      return this.$store.state.response
    },
    getFormat() {
      return this.$store.state.getFormat
    }
  },
  methods: {
    requestLoop() {
      clearTimeout(this.loopTimet)

      this.loopTimet = setTimeout(() => {
        this.$store.dispatch('request')
        this.loopTimet = setTimeout(this.requestLoop, 1000)
      }, 1000);
    }
  },
  mounted() {
    console.log(process.env);
    this.requestLoop()
  },
  destroyed() {
  }
}
</script>

<style scoped lang="scss">
.wrap {
  width: 100%;
  background: #001147;
  overflow: hidden;
}

/* TEST RESPONSE SERVER */
iframe {
  position: absolute;
  top: -160px;
  left: 0;
  right: 0;
  background: white;
  width: 260px;
  height: 200px;
  margin: 0 auto !important;
  border-left: 2px solid orange !important;
  border-right: 2px solid orange !important;
  border-bottom: 2px solid orange !important;
  border-radius: 0 0 8px 8px;
  z-index: 999999;

  &:hover {
    top: 0px;
    transition: top 1s ease;
  }
}
</style>
