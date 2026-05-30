<template>
  <div class="custom-input-wrapper">
    <div class="custom-input" :class="{ 'custom-input_disabled': disabled }" @click="focusInput" @focus="focusInput"
      ref="box" autofocus="false">
      <div class="custom-input__icon" v-if="renderIcon" :class="`custom-input__icon_${iconType}`" ref="boxVertical"></div>
      <input class="custom-input__input" spellcheck="true" autocapitalize="off" autocorrect="off" ref="input"
        :id="inputId" :key="inputKey" :type="inputType" :autocomplete="autocompleteType" :disabled="disabled"
        @blur="blurInput" :value="inputValue" @input="onValueChange" x-webkit-speech />
      <label class="custom-input__label" :class="{ 'custom-input__label_active': value !== '' }" :for="inputKey" ref="label">
        {{ placeholder }}
      </label>
    </div>
    <p v-if="isError" class="error-message">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script lang="js">
export default {
  name: 'customInput',
  props: {
    value: {
      type: String,
      required: true,
    },
    inputId: {
      type: String,
      required: true,
    },
    inputKey: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: 'label',
    },
    type: {
      type: String,
      default: 'text',
    },
    placeholder: {
      type: String,
      default: 'text',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    isError: {
      type: Boolean,
      default: false,
    },
    errorMessage: {
      type: String,
      default: '',
    }
  },
  computed: {
    inputValue() {
      return this.value;
    },
    autocompleteType() {
      switch (this.type) {
        case 'tel':
          return 'tel';
        case 'pass':
          return 'pass';
        case 'number':
          return '';

        default:
          return 'text';
      }
    },
    inputType() {
      switch (this.type) {
        case 'pass':
          return 'number';

        default:
          return this.type;
      }
    },
    renderIcon() {
      return this.type === 'tel' || this.type === 'pass';
    },
    iconType() {
      switch (this.type) {
        case 'tel':
          return 'tel';
        case 'pass':
          return 'pass';

        default:
          return 'text';
      }
    },
  },
  methods: {
    onValueChange(e) {
      this.$emit("input", e.target.value);
    },
    focusInput() {
      this.$refs.label.classList.add('custom-input__label_active');
    },
    blurInput() {
      if (this.$refs.input.value.length <= 0) {
        this.$refs.label.classList.remove('custom-input__label_active');
      }
      this.$emit('blurInput');
    }
  },
}
</script>

<style scoped lang="scss">
.custom-input-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  //overflow: hidden;
}

.custom-input {
  background-color: var(--white-text);
  border: 2px solid var(--orange-rad);
  border-radius: 10px;

  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  width: auto;
  //overflow: hidden;

  line-height: 1em;
  height: 2.25em;
  align-items: flex-end;

  &_disabled {
    border: 3px solid var(--dark-grey);

    .custom-input__icon {
      border-right: 3px solid var(--dark-grey);
    }

    .custom-input__label,
    .custom-input__label__active {
      color: var(--dark-grey);
    }
  }
}

.custom-input__icon {
  width: 40px;
  height: 100%;
  border-right: 3px solid var(--orange-rad);
  position: relative;

  &_tel::before {
    content: "+7";
    width: 100%;
    height: 100%;
    z-index: 1;
    color: var(--dark-blue);
    font-size: 1.5em;
    font-family: "myriadRegular";
    display: flex;
    justify-content: center;
    align-items: flex-end;
    line-height: 1.7em;
  }

  &_number {
    width: auto;
    left: 0;
  }

  &_pass {
    background-image: url(~assets/lock.svg);
    background-repeat: no-repeat;
  }
}

.custom-input__input {
  box-sizing: border-box;
  border: none;
  outline: none;
  font-size: 1.5em;
  font-family: "myriadRegular";
  padding: 14px 0 4px 4px;
  overflow: scroll;
  width: 100%;
  background: transparent;

  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &[type="number"] {
    --moz-appearance: textfield;
  }
}

.custom-input__label {
  position: absolute;
  color: var(--light-grey);
  font-size: 1em;
  font-family: "myriadRegular", sans-serif;
  cursor: text;
  transition: transform 0.5s ease-out, color 0.5s ease-out;
  right: 13px;
  width: fit-content;
  text-align: right;
  bottom: 50%;
  transform: translateY(50%);

  &_active {
    //transform: translate(-40px, -100%) scale(0.6);
    //color: var(--light-grey);
    opacity: 0;
  }
}

.error-message {
  position: relative;
  color: var(--red-dark-fon);
  font-size: 1em;
  font-family: "myriadRegular", sans-serif;
}
</style>
