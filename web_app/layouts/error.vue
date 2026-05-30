<template>
  <!-- <section>
    <a-result :status="'' + error.statusCode" :title="'' + error.statusCode" :subTitle="subTitle"> -->

    <!-- <template v-slot:extra> -->
      <button type="primary" @click="backHome">
        Вернуться на главную
      </button>
    <!-- </template> -->
  <!-- </a-result>
  </section> -->
</template>

<script>
export default {
  props: ['error'],
  data () {
    return {
      subTitle: ''
    }
  },
  created () {
    // this.$store.commit('setTitle', 'Ошибка')
    if (this.error.statusCode === 404) {
      this.subTitle = 'Извините, страница, которую вы посетили, не существует.'
    } else if (this.error.statusCode === 403) {
      this.subTitle = 'Извините, у вас нет прав для доступа к этой странице.'
    } else if (this.error.statusCode === 500) {
      this.subTitle = 'Извините, сервер сломался.'
    } else if (this.error.statusCode === 100500) {
      this.error.statusCode = 500
      this.subTitle = this.error.message
    } else {
      this.subTitle = 'Неизвестная ошибка'
    }
  },
  methods: {
    backHome () {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
  h1 {
    color: red;
  }

  @media screen and (min-width: 480px) {
    section {
      padding-top: 5rem;
    }
  }
</style>
