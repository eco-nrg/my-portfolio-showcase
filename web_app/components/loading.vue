<template>
  <div v-if="loading" class="loading-page">
    <img class="loading" src="~/assets/lightning-loader.svg" alt=""/>
  </div>
</template>

<script>
export default {
  props: {
    loading: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<style lang="scss" scoped>
.loading-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  text-align: center;
  font-size: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: var(--dark-blue);
  color: var(--blue);

  .loading {
    width: 14rem;
    height: 14rem;
  }
}
</style>
