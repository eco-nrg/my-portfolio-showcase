<template>
  <div class="custom-button-wrapper">
    <button :class="className" :disabled="disabled" @click.self="submitEvent($event)">{{ value }}</button>
  </div>
</template>

<script>
export default {
  name: 'customButton',
  props: {
    value: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'normal'
    },
    size: {
      type: String,
      default: '',
    },
    classList: {
      type: String,
      default: ''
    },
  },
  data: () => ({
    key: ''
  }),
  computed: {
    className() {
      const defaultClassName = `custom-button custom-button_${this.type} ${this.classList}`;
      if (this.size != '') {
        return `${defaultClassName} custom-button_${this.size}`;
      }
      return defaultClassName;
    }
  },
  methods: {
    randomString() {
      return Math.random().toString(36).substring(2);
    },
    submitEvent(e) {
      e.preventDefault();
      this.$emit('get', e);
    }
  },
  mounted() {
    if (this.$vnode.key)
      this.key = this.$vnode.key;
    else
      this.key = this.randomString();
  }
}
</script>

<style lang="scss" scoped>
.custom-button-wrapper {
  position: relative;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  margin: 0 0 10px;
  user-select: none;
}

.custom-button {
  width: fit-content;
  border: none;
  padding: 8px 1em 6px;
  border-radius: 10px;
  background-color: var(--red-dark-fon);
  border: 2px solid var(--white-text);
  color: var(--white-text);
  font-family: 'myriadRegular';
  font-size: 1.2em;
  white-space: nowrap;
  cursor: pointer;

  &[disabled] {
    background-color: var(--light-grey);
  }
}

.custom-button_min {
  padding: 3px 18px 3px 10px;
  font-size: 1em;
  border-radius: 6px;

  &::after {
    content: "";
    position: absolute;
    top: 15px;
    width: 8px;
    min-height: 8px;
    transform: rotate(45deg);
    border-top: 2px solid var(--white-text);
    border-right: 2px solid var(--white-text);
  }
}

.custom-button_normal {
  background-color: var(--blue);

  &:active {
    border: 2px solid var(--black-text);
  }
}

.custom-button_action {
  background-color: var(--green-light-fon);

  &:active {
    border: 2px solid var(--black-text);
  }
}

.custom-button_attention {
  background-color: var(--red-dark-fon);

  &:active {
    border: 2px solid var(--black-text);
  }

  &.custom-button_min {
    background-color: var(--red-dark-fon);

    &:active {
      background-color: var(--orange-rad);
    }
  }
}

.indicator-profile {
  background: linear-gradient(to right, var(--green-light-fon) 70%, var(--light-grey) 30%);
}

.visited {
  &.custom-button_normal {
    background-color: var(--blue-fon-button);
  }

  &.custom-button_action {
    background-color: var(--green-fon-button);
  }

  &.custom-button_attention {
    background-color: var(--orange-rad);
  }
}

.report-problem-button.custom-button_attention {
  background-color: var(--white-background);
  border-color: var(--red-dark-fon);
  color: var(--red-dark-fon);
}
</style>
