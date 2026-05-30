<template>
  <CustomModal class="box-modal-info start-session-modal" @closeModal="closeModal">

    <body slot="body" class="start-session-modal__body">
      <p class="start-session-modal__body-text" v-if="space.status == 'BU'">
        Внимание данный терминал <b class="start-session-modal__body-warning">
          Занят
        </b>
      </p>

      <div class="start-session-modal__space">
        <div class="start-session-modal__connector" v-html="space.icon"></div>
        <div class="start-session-modal__space-info">
          <p>{{ space.name }}</p>
          <p>{{ space.addres }}</p>
          <p>{{ space.type }}</p>
        </div>
      </div>

      <p class="start-session-modal__body-text">Активировать данный терминал для зарядки вашего электромобиля</p>
    </body>
    <footer slot="footer" class="start-session-modal__footer">
      <div class="start-session-modal__button-block">
        <CustomButton value="нет" type="normal" @get="closeModal" />
        <CustomButton value="да" type="action" @get="startSession" />
      </div>
    </footer>
  </CustomModal>
</template>

<script lang="js">
import CustomButton from "~/components/customButton.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: 'startSessionModal',
  comments: {
    CustomButton,
    CustomModal,
  },
  props: {
    space: {
      type: Object,
      default: {},
    },
  },
  methods: {
    closeModal() {
      this.$router.replace('/profile');
      this.$store.dispatch('closeModal');
    },
    startSession() {
      this.$emit('startSession');
    },
  }
};
</script>

<style lang="scss" scoped>
.start-session-modal__body-text {
  padding-top: 10px;
}

.start-session-modal__body-warning {
  color: var(--orange-status);
}

.start-session-modal__space {
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin: 0 auto;

  @media only screen and (min-width: 400px) {
    flex-direction: row;
    width: 100%;
  }
}

.start-session-modal__connector {
  padding: 0 10px 0 0;
  fill: var(--green-light-fon);
  width: 50%;

  @media only screen and (min-width: 400px) {
    max-width: 100px;
  }
}

.start-session-modal__space-info {
  color: var(--blue-spacer);
  min-width: 190px;
  text-align: start;

  @media only screen and (min-width: 400px) {
    min-width: auto;
  }
}

.start-session-modal__button-block {
  display: flex;
  justify-content: space-around;
  width: 100%;
}
</style>
