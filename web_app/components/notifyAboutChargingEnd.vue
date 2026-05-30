<script>
export default {
  name: "chargingEnd"
}
</script>

<template>
  <div class="notify-container">
    <h2 class="attention-box">ВНИМАНИЕ</h2>
    <div class="main-text-box">
      <div class="charging-end-txt">
        Зарядка завершена, однако, электромобиль по-прежнему занимает парковочное место
      </div>
      <div class="about-penalty-txt"></div>
      <div class="how-to-finish-txt">
        Для завершения сессии и прекращения начисления двойного простоя необходимо убрать транспортное средство
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.notify-container {
  font-family: myriadRegular, sans-serif;
  color: var(--black-text);
  text-align: center;
  padding: 0.5rem 0 0.5rem 0;
}
.attention-box {
  color: var(--red-dark-fon);
  font-size: 2rem;
}
.main-text-box {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  height: 100%;
}
</style>
