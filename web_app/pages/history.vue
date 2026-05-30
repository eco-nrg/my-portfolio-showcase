<template>
  <div class="history">
    <nav class="nav-history">
      <ul class="list-history">
        <li class="item-list" :class="{ 'active-rout': isRouteActive() }">
          <nuxt-link to="/history">
            Сессии
          </nuxt-link>
        </li>
        <li class="item-list" :class="{ 'active-rout': !isRouteActive() }">
          <nuxt-link to="/history/transaction">
            Транзакции
          </nuxt-link>
        </li>
      </ul>
    </nav>
    <nuxt-child/>
  </div>
</template>

<script>
import Loading from "~/components/loading"

export default {
  name: 'HistoryLayoutPage',
  components: {
    Loading
  },
  computed: {
  },
  methods: {
    isRouteActive() {
      return !this.$route.path.includes('/transaction')
    },
  }
}
</script>


<style lang="scss" scoped>
.history {
  width: 100%;
  height: 100%;

  .nav-history {
    width: 100%;
    height: 2.7em;
    display: flex;
    align-items: center;
    justify-content: center;

    .list-history {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .item-list {
        width: calc(50% - 2px);
        background-color: var(--white-text);
        height: 100%;
        /* color: var(--dark-blue); */
        /* text-transform: uppercase; */
        color: #001147;
        opacity: .5;
        transition: opacity .3s linear;

        &>a {
          font-size: 1.6em;
          font-family: "myriadBold";
          height: 100%;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-around;
          padding: 3px 0 0 0;
        }
         .nuxt-link-exact-active {
          color: var(--red-light-fon);
          opacity: 1;

          .icon path {
            fill: var(--red-light-fon);
          }
        }
      }
      .active-rout {
        color: var(--red-light-fon);
        opacity: 1;

        .icon path {
          fill: var(--red-light-fon);
        }
      }
    }
  }
}
</style>