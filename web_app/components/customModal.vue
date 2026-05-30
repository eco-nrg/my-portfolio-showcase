<template>
  <div class="custom-modal" ref="modal" @click.self="closeModal">
    <div class="box-modal">
      <span class="box-close" @click="closeModal"></span>
      <div class="box-header">
        <slot name="header"></slot>
      </div>
      <div class="box-context">
        <slot name="body"></slot>
      </div>
      <div class="box-footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script lang="js">
export default {
  name: 'customModal',
  methods: {
    closeModal() {
      this.$emit('closeModal');
    }
  },
  mounted() {
    if (process.client) {
      document.body.setAttribute('style', 'overflow: clip;');
    }
  },
  beforeDestroy() {
    if (process.client) {
      document.body.removeAttribute('style');
    }
  },
}
</script>

<style lang="scss" scoped>
.custom-modal {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--dark-fon);
  padding: 0;
  z-index: 9;

  .box-modal {
    min-width: 80%;
    height: max-content;
    width: min-content;
    background-color: var(--white-text);
    color: var(--black-text);
    border: 2px solid var(--blue);
    border-radius: 10px;
    position: relative;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    /* margin: 5em 0 0 0; */

    .box-close {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 20px;
      height: 20px;
      opacity: 1;
      cursor: pointer;
    }

    .box-close:hover {
      opacity: 0.5;
    }

    .box-close:before,
    .box-close:after {
      position: absolute;
      top: 0;
      left: 8px;
      content: " ";
      height: 20px;
      width: 4px;
      background-color: var(--blue);
      border-radius: 10px;
    }

    .box-close:before {
      transform: rotate(45deg);
    }

    .box-close:after {
      transform: rotate(-45deg);
    }

    .box-header {
      width: 100%;
      height: fit-content;
      color: var(--dark-blue);
      font-size: 1.3em;
      text-align: center;
      padding: 1.3em 0 0 0;
      font-family: 'myriadBold';
    }

    .box-context {
      width: 100%;
      color: var(--green-light-fon);
      font-size: 1.3em;
      text-align: center;
      font-family: "myriadBold";
      height: fit-content;
      padding: 0 20px 24px;
    }

    .box-footer {
      width: 100%;

      &>div {
        display: flex;
        justify-content: space-around;
        width: 100%;
      }
    }
  }
}

.box-modal-alert {
  .box-modal {
    border: 2px solid var(--red-dark-fon);

    .box-close:before,
    .box-close:after {
      background-color: var(--orange-rad);
    }
  }

  .box-context {
    color: var(--orange-rad) !important;
  }
}

.box-modal-chart {

  .box-modal {
    position: absolute;
    width: calc(100vw - 20px);
    height: calc(100vh - 20px);

    @media (orientation: portrait) {
      width: calc(100vh - 20px);
      height: calc(100vw - 20px);
      transform: rotate(-90deg);
    }

    background-color: #000000;
    border: 2px solid var(--black-text);

    .box-close {
      top: 6px;
      right: 6px;

    }

    .box-close::after,
    .box-close::before {
      background-color: var(--white-text);
    }
  }
}


.box-modal-bonus {
  .box-header {
    font-size: 1.6em !important;
    color: var(--blue) !important;
  }

  .box-modal {
    border: 2px solid var(--green-light-fon);

    .box-close:before,
    .box-close:after {
      background-color: var(--green-light-fon);
    }
  }

  .box-context {
    font-size: 1.5em !important;
    color: var(--green-light-fon) !important;
  }
}

.box-modal-info {
  .box-header {
    font-size: 1.2em !important;
    color: var(--dark-blue) !important;
  }

  .box-modal {
    border: 2px solid var(--blue);

    .box-close:before,
    .box-close:after {
      background-color: var(--blue);
    }
  }

  .box-context {
    font-family: "myriadRegular" !important;
    font-size: .8em !important;
    font-weight: normal;
    color: var(--dark-blue) !important;
    padding: 0 20px 4px !important;

    &>div {
      text-align: left;
    }
  }

  .box-footer {
    width: 100%;
    padding: 20px 10px 10px 10px;

    &>div {
      flex-wrap: wrap;
      display: flex;
      justify-content: space-evenly;
      width: 100%;
      align-content: space-between;
    }

    .connector-footer {
      justify-content: space-around;
      align-items: flex-end;

      &>span {
        background-color: var(--dark-grey);
        width: 3em;
        height: 4em;
        padding: 4px 12px;
        border-radius: 6px;
      }

      &>div:not(:last-child) {
        margin-right: 1em;
      }
    }
  }

}

.check {
  .box-modal {
    background-color: #FCF9E4;
  }
}

.requisites {
  .box-modal {
    .box-header {
      padding: 0.4em 0 0 0;

      .title {
        text-align: left;
        padding-left: 20px;
        color: var(--red-light-fon);
      }

      .header {
        text-align: left;
        padding-left: 20px;
        max-width: 80%;
      }
    }

    .box-context {
      .inform {
        width: 80%;
        height: fit-content;
        font-size: 1.1em;
        white-space: pre-line;
      }
    }

    .box-context div {
      height: 100px;
      display: flex;
      flex-direction: row;
      align-items: center;
      padding: 20px 0 0 0;

      .info {
        width: 100%;
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        height: 100%;
        align-items: flex-start;
        justify-content: space-between;
        height: 100%;
      }

      .command {
        width: 50%;
        flex: 2 0 auto;
        display: flex;
        flex-direction: column;
        height: 100%;

        .custom-button {
          margin: 0;
        }
      }
    }

    .box-footer>div {
      display: flex;
      justify-content: flex-start;
    }

  }
}
</style>
