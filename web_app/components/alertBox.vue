<template>
  <div class="alert-messanger">
    <div class="icons-msg">{{icon[marker]}}</div>
    <div class="context-msg">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'alertBox',
  props: {
    marker: {
      type: String,
      default: 'default'

    }
  },
  data: () => ({
    text: '',
    icon: {
      exclamation: '!',
      default: ''
    }
  })
}
</script>

<style lang="scss" scoped>
.alert-messanger{
  color: var(--white-text);
  max-width: 100vw;
  min-height: 60px;
  display: flex;
  justify-content: space-between;
  background-color: var(--red-dark-fon);
  padding: 0px 2em;
  user-select: none;
  align-items: center;

  .icons-msg{
    width: fit-content;
    font-size: 3em;
    line-height: 1em;
    font-family: 'myriadBold';
    padding-right: 10px;
  }
  .context-msg{
    width: fit-content;
    font-size: 1.1em;
    font-family: 'myriadRegular';

    p{
      padding: 0 20px 0 0;
    }
  }
}
</style>
