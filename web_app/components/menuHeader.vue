<template>
  <header class="header" ref="header">
    <nav>
      <ul class="menu" :class="{ 'link-session': selectSession }">
        <li class="menu-item" v-for="(menu, index) in menuOptions" :key="index">
          <nuxt-link :to="menu.route" class="menu-linck">
            <iconHeaderMenu :image="menu.src"
              :class="{ 'link-active': isRouteActive(menu.route) || ($route.path.indexOf('orders') >= 1 && menu.route === '/history') }">
              <label>
                {{ menu.label }}
              </label>
            </iconHeaderMenu>
          </nuxt-link>
        </li>

        <li class="menu-item" @click="isSessionCharging" v-if="!isSession && !selectSession">
          <iconHeaderMenu :image="toogleCashToSession" :class="{ 'link-active': isRouteActive('/payment') }"
            @click="isRouteActive($route.path)">
            <label :key="cashData.money"
              :style="{ color: setColorCash(cashData.money).int ? colorCashMenu : 'var(--white-text)' }">
              {{ setColorCash(cashData.money).value }}
            </label>
            <label class="menu-text" :class="{ 'cash-bonus': cashData.bonus > 0 }">
              {{ cashData.bonus }}
            </label>
          </iconHeaderMenu>
        </li>

        <li class="menu-item" @click="isSessionCharging" v-else-if="isSession && selectSession">
          <iconHeaderMenu :image="toogleCashToSession"
            @click="isRouteActive($route.path)">
            <label :key="cashData.money"
              :style="{ color: setColorCash(cashData.money).int ? colorCashMenu : 'var(--white-text)' }">
              {{ setColorCash(cashData.money).value }}
            </label>
            <label class="menu-text" :class="{ 'cash-bonus': cashData.bonus > 0 }">
              {{ cashData.bonus }}
            </label>
          </iconHeaderMenu>
        </li>

        <li class="menu-item mr-5" @click="isSessionCharging" v-else-if="isSession"><!-- show session -->
          <iconHeaderMenu class="sassion" :image="toogleCashToSession" @click="isRouteActive($route.path)">
            <label class="menu-text total_kwh">
              {{ parseInt(sessionCharging?.total_kwh || 0) }}
            </label>
            <label class="menu-text am">
              {{ parseInt(sessionCharging?.am || 0) }}
            </label>
            <label class="menu-text current_kwh">
              {{ parseInt(sessionCharging?.current_kwh || 0) }}
            </label>
          </iconHeaderMenu>
        </li>
      </ul>
    </nav>
  </header>
</template>

<script>
import iconHeaderMenu from "~/components/iconHeaderMenu";

export default {
  name: 'menuHeader',
  components: {
    iconHeaderMenu,
  },
  data: () => ({
    currentScroll: 0,
    prevScroll: 0,
    selectSession: false,
  }),
  computed: {
    isSession() {
      return this.$store.state.isSessionCharging
    },
    cashData() {
      return this.$store.state.cashData
    },
    colorCashMenu() {
      return this.$store.state.colorCashMenu
    },
    toogleCashToSession() {
      return this.isSession && !this.selectSession ? 'session' : 'cash'
    },
    sessionCharging() {
      return this.$store.state.sessionCharging
    },
    menuOptions() {
      return [
        {
          label: 'Профиль',
          route: '/profile',
          src: 'profile'
        },
        {
          label: 'Станции',
          route: '/refill',
          src: 'stations'
        },
        {
          label: 'История',
          route: '/history',
          src: 'history'
        }
      ]
    },
  },
  methods: {
    setColorCash(value) {
      this.$store.dispatch('__setColorCash', value)
      return { value, int: value > 0 ? true : false }
    },
    openPaymentModal() {
      this.$store.dispatch(
        'setModal',
        {
          name: 'paymentModal',
        },
      );
    },
    isSessionCharging() {
      if (this.sessionCharging?.id && this.$route.path.includes('/spaces/')) {
        this.$router.push('/payment')
      } else if (!this.sessionCharging?.id) {
        this.$router.push('/payment')
      } else {
        this.$router.push(`/spaces/${this.sessionCharging.id}`)
      }
    },
    isRouteActive(rout) {
      if (this.$route.path.includes('/spaces/') && this.isSession)
        this.selectSession = true
      else
        this.selectSession = false

      return this.$route.path.includes(rout)
    },
    eventShowHide() {
      const header = this.$refs.header,
        headerHidden = () => header.classList.contains('header-hidden')

      this.currentScroll = window.pageYOffset

      if (this.currentScroll > -1) {
        if (this.currentScroll > this.prevScroll && !headerHidden()) {
          header.classList.add('header-hidden');
        }
        if (this.currentScroll < this.prevScroll && headerHidden()) {
          header.classList.remove('header-hidden');
        }
        this.prevScroll = this.currentScroll;
      }
    }
  },
  mounted() {
    this.prevScroll = window.pageYOffset
    window.addEventListener('scroll', this.eventShowHide)
  },
  destroyed() {
    window.removeEventListener('scroll', this.eventShowHide)
  }
}
</script>

<style lang="scss" scoped>
.header {
  position: sticky;
  top: 0;
  transition: 1s;
  z-index: 1;

  .menu {
    background: var(--dark-blue);
    display: flex;
    justify-content: space-around;
    max-width: 100%;

    &>.menu-item {
      /* min-width: calc(100% / 4); */
      width: calc(100% / 4);
      max-height: 100px;
      text-align: center;
      list-style-type: none;
      display: flex;
      justify-content: center;
      cursor: pointer;

      .sassion {
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;
        align-items: center;
        height: 70%;
        margin: auto 10px auto 0;

        .total_kwh {
          color: var(--blue);
        }

        .am {
          color: var(--orange-rad);
        }

        .current_kwh {
          color: var(--green-light-fon);
        }
      }

      &>a {
        width: 100%;
      }

      &>.menu-linck {

        .menu-text {
          width: 100%;
          font-family: "myriadRegular";
          font-size: 1em;
          color: var(--white-text);
          display: block;
          margin: 6px 0 0 0;
          cursor: pointer;
        }
      }

      .cash-bonus {
        color: var(--blue);
      }
    }

    .mr-5 {

      /* margin-right: -20px; */
      label {
        width: fit-content;
      }
    }
  }

  .link-session {
    background: var(--orange-rad);

    .menu-linck {

      .icon-header {
        color: var(--dark-blue);
        fill: var(--dark-blue);

      }

    }
  }
}

.header-hidden {
  transform: translateY(-100%);
}
</style>
