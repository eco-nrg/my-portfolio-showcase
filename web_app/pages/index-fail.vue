<template>
  <client-only>
    <div class="login-box">
      <div class="wrap">
        <div class="box-title">
          <div class="logo">
            <img src="~assets/logo.svg" />
          </div>
          <div class="context">
            <h2 class="title">
              {{ host() }}
            </h2>
            <p class="desck">
              ЗАКРОЙТЕ ДАННУЮ ВКЛАДКУ
            </p>
            <customButton value="В ПРОФИЛЬ" @get="navigateToProfile" type="normal" />
          </div>
        </div>
      </div>
    </div>
  </client-only>
</template>

<script leng="js">
import customInput from "~/components/customInput";
import customButton from "~/components/customButton";


export default {
  name: 'IndexPage',
  head() {
    return {
      title: 'eco-energo: ЗАКРОЙТЕ ДАННУЮ ВКЛАДКУ',
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: 'My custom description'
        }
      ]
    }
  },
  data: () => ({
  }),
  components: {
    customInput, customButton
  },
  computed: {

  },
  methods: {
    host() {
      if (process.client)
        return process.env.API_SERVER_NAME.slice(0, process.env.API_SERVER_NAME.lastIndexOf('.'))
      return ''
    },
    navigateToProfile() {
      this.$router.replace('/profile');
    }
  },
  watch: {

  }
}
</script>

<style>
.header {
  display: none;
}
</style>

<style lang="scss" >
.login-box {
  width: 100%;
  height: 100%;

  .wrap {
    /* max-width: 300px; */
    width: 100%;
    min-height: 100%;
    margin: 0 auto;
    padding: 4em 0 0 0;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;

    .error-event {
      width: 100%;
      color: var(--red-dark-fon);
      text-align: center;
    }

    .box-title {
      margin-bottom: 2em;
      display: flex;
      width: 100%;
      align-items: center;
      justify-content: center;

      .logo {
        margin: 0 0.5em 0 0;
        display: inline-block;
        width: 50px;
      }

      .context {
        color: var(--white-text);
        display: inline-block;
        width: fit-content;

        .title {
          font-size: 2em;
          font-family: 'myriadBold';
        }

        .desck {
          font-size: .7em;
          font-family: 'myriadRegular';
        }
      }
    }

    .form,
    .sms-box {
      color: var(--white-text);
      width: 100%;
      /* min-height: calc(100vh / 2 - 100px); */

      .form-box {
        display: flex;
        align-items: center;
        flex-direction: column;
        justify-content: space-around;
        height: 100%;

        .box-input {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
        }

        .timer-sms {
          font-size: 1.1em;
          font-family: 'myriadRegular';
          color: var(--dark-grey);
        }

        .sms-button {
          font-size: .9em;
        }
      }

      .number {
        font-family: 'myriadRegular';
        font-size: 2em;
        margin: 0 0 1em 0;
      }



      .sms-input {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0 0 1em;

        .code {
          width: calc(100% / 1.4);
        }

        .sms-linck {
          font-size: 1em;
          background: none;
          color: var(--orange-rad);
          text-decoration: underline;
        }
      }

      .sms-twoe {
        color: var(--red-dark-fon);
        width: 100%;
        font-size: 1.1em;
        text-align: center;
      }

    }

  }
}</style>
