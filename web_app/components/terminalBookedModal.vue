<template>
  <CustomModal @closeModal="closeModal" class="box-modal-info">
    <body slot="body">
      <p v-if="myBooking">
        Вы забронировали этот терминал. Вам необходимо успеть активировать терминал, до:
        <span class="time">{{ millisecondsToDate(bookedUntil) }}</span>
      </p>
      <p v-else>
        Терминал забронирован другим пользователем, если он не успеет активировать терминал, бронь
        снимется в
        <span class="time">{{ millisecondsToDate(bookedUntil) }}</span>
      </p>
    </body>
    <footer slot="footer">
      <customButton value="Понятно)" type="normal" @get="closeModal" />
    </footer>
  </CustomModal>
</template>

<script lan="js">
import CustomButton from "~/components/customButton.vue";
import CustomModal from "~/components/customModal.vue";

export default {
  name: "terminalBookedModal",
  components: {
    CustomButton,
    CustomModal,
  },
  computed: {
    myBooking() {
      return this.$store.state.dataModal[0].myBooking;
    },
    bookedUntil() {
      return this.$store.state.dataModal[0].bookedUntil;
    },
  },
  methods: {
    millisecondsToDate(milliseconds) {
      const date = new Date(milliseconds)
      
      return date.toTimeString();
    },
    closeModal() {
      this.$store.dispatch("closeModal");
    },
  },
};
</script>

<style lang="scss" scoped>
.time {
  font-size: 1.2em;
  color: var(--orange-rad);
  font-weight: 900;
}
</style>
