<template>
  <div class="map-box">
    <client-only>
      <yandex-map
        ref="map"
        class="map"
        map-type="map"
        style="width: 100%; height: 100vh;"
        :coords="coords"
        :zoom="zoom"
        :controls="['geolocationControl', 'fullscreenControl', 'routeButtonControl']"
        :use-object-manager="true"
        :use-html-in-layout="true"
      >
        <ymap-marker v-for="marker, index in markersAll" :key="index"
          :marker-id="marker.index"
          marker-type="placemark"
          :coords="marker.coord"
          :icon="markerIcon"
          :balloon-template="balloonTemplate(marker)"
          >
        </ymap-marker>
      </yandex-map>

      <template #placeholder>
        <Loading :loading="markersAll.length > 0"/>
      </template>
    </client-only>
  </div>
</template>

<script>
// DOCUMENTATION
// https://yandex.ru/dev/maps/jsapi/doc/2.1/quick-start/index.html
// MAP COORDINATIONS
// https://yandex.ru/map-constructor/location-tool/
import { loadYmap } from 'vue-yandex-maps';
import Loading from "~/components/loading"

export default {
  name: "RefillMapTab",
  components: {
    Loading
  },
  async asyncData() {
    const markerIcon = {
      layout: 'default#image', // default#imageWithContent',
      imageHref: require('~/assets/marcker-map.svg'),// Normal,
      imageSize: [30, 50]
      // imageOffset: [-22, -55]
    }
    return { markerIcon }
  },
  data: () => ({

  }),
  computed: {
    isSelect(){
      const spacesId = this.$route.query?.spaces
      return spacesId ? this.markersAll.find(m => m.index === parseInt(spacesId) ) : false
    },
    markersAll(){
      return this.$store.state.map?.markers || []
    },
    zoom() {
      return this.isSelect ? this.isSelect?.zoom : this.$store.state.map.config?.zoom || process.env.API_MAP_ZOOM
    },
    iconImageSize(){
      return this.$store.state.map.config?.iconImageSize
    },
    coords(){
      return this.isSelect ? this.isSelect?.coord : this.$store.state.map.config?.coords || process.env.API_MAP_COORDS.split(',')
    },
  },
  async updated() {
    if(typeof ymaps === 'undefined' || this.isSelect || this.zoom || this.coords){
      this.markerIcon.imageSize = await this.iconImageSize
      await loadYmap()
      await ymaps.ready(this.setHeightMap())
    }
  },
  methods: {
    balloonTemplate(marker) {
      return `
        <p>${marker.address}</p>
      `
    },
    async setHeightMap(){
      if (this.$refs.map?.$el){
        const offset = document.querySelector('.header').clientHeight + document.querySelector('.nav-refill').clientHeight;
        this.$refs.map.$el.style.height = `${window.innerHeight - offset}px`
      }
    }
  },
  mounted(){
    // setInterval(()=>{
    //   console.log( this.zoom , this.coords );
    // }, 1000)
  }
};
</script>

<style lang="scss" scoped>

</style>
