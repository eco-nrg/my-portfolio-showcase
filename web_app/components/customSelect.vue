<template>
  <div class="custom-select">
    <div class="wrap">
      <label :for="keyInputComponent" ref="label" :class="{ 'active': valueSelected && valueSelected.length > 0 }">
        {{ placeholderData }}
      </label>
      <input :type="type" :aria-labelledby="placeholder" :id="keyInputComponent" autocomplete="off" autocapitalize="off"
        autocorrect="off" :disabled="disabled" :name="nameInput" :value="valueSelected" @input="filterValue($event)"
        @blur="focusBlur" @focus="focusSelect" @keyup="keypress" x-webkit-speech :placeholder="valueSelected"
        ref="input" />
      <div class="icon-arrow" @click="focusSelect">
        <span ref="iconArrow" class="arrow">
          <span></span>
          <span></span>
        </span>
      </div>
    </div>

    <div class="container" v-show="showOption">
      <ul ref="options">
        <li v-for="option in optionsArr" :key="option.id" :class="{ 'selected': option.selected }" @click="setValue">
          {{ option.value }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="js">
export default {
  name: 'customSelect',
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    options: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: 'Все'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'text'
    },
  },
  data: () => ({
    // delaiBlur: false,
    delaiBlurActive: false,
    delaiSelected: false,
    showOption: false,
    valueSelected: '',
    optionsArr: []
  }),
  computed: {
    keyInputComponent() {
      return this.$vnode.key ? this.$vnode.key : this.hashGenerator(6)
    },
    nameInput() {
      return this.$vnode.key ? this.$vnode.key : this.hashGenerator(10)
    },
    placeholderData() {
      return this.placeholder
    },
  },
  methods: {
    setValue(e) {
      const input = this.$refs.input
      this.valueSelected = (e?.target ? e.target?.innerText : e.value)

      if (typeof this.$vnode.key !== 'undefined' && this.placeholder && this.placeholder.length > 0 && input.name !== "map") {
        localStorage.setItem(input.name, this.valueSelected)//сохраняем введенные данные
      }

      this.optionsArr.map(item => { item.selected = String(item.value).toLowerCase() === String(this.valueSelected).toLowerCase() })

      if (this.valueSelected === "все") {
        localStorage.removeItem(input.name)
        this.valueSelected = ''
      }

      this.submitValue()
    },
    keypress(e) {
      if (["ArrowDown", "ArrowUp", "Enter"].indexOf(e.key) != -1) {
        const length = this.optionsArr.length - 1;

        for (let key = 0; key < this.optionsArr.length; key++) {
          const item = this.optionsArr[key];

          if (item.selected && key < length && e.key === 'ArrowDown') {
            item.selected = false
            this.optionsArr[key + 1].selected = true
            break
          } else if (item.selected && key == length && e.key === 'ArrowDown') {
            item.selected = false
            this.optionsArr[0].selected = true
            break
          } else if (item.selected && key > 0 && e.key === 'ArrowUp') {
            item.selected = false
            this.optionsArr[key - 1].selected = true
            break
          } else if (item.selected && key == 0 && e.key === 'ArrowUp') {
            item.selected = false
            this.optionsArr[length].selected = true
            break
          }

          if (item.selected) {
            this.setValue(item)
            this.$refs.input.blur()
          }
        }

        this.delaiSelected = setTimeout(() => {
          document.querySelector('li.selected').scrollIntoView({ behavior: "smooth" })
          this.delaiSelected = false
        }, 200);
      }
    },
    filterValue(e) {
      let value = e.target.value
      this.valueSelected = value

      if (value && value.length > 0) {
        const newVal = this.options.filter(item => String(item.value).toLowerCase().match(value.toLowerCase()))
        this.optionsArr = newVal.map((item, key) => this.convertOptions(item, key))
      } else {
        this.optionsArr = this.options.map((item, key) => this.convertOptions(item, key))
      }
    },
    convertOptions(item, key) {
      return { id: key, value: item.value, selected: key == 0 ? true : false }
    },
    focusSelect() {
      this.$refs.input.focus()
      this.showOption = true
      this.$refs.label.classList.add('active')
      this.$refs.iconArrow.classList.add('active')
    },
    focusBlur(e) {
      if (e.type === 'blur') {
        setTimeout(() => {
          if (this.valueSelected && this.valueSelected.length <= 0)
            this.$refs.label.classList.remove('active')
          this.$refs.iconArrow.classList.remove('active')
          this.showOption = false
        }, 250)
      }
    },
    submitValue() {
      console.log(1111, this.valueSelected);
      const e = this.$refs.input
      if (this._events?.get) {
        this.$emit('get', this.valueSelected);
      }
    },
    createdSelect(value) {
      const saveData = localStorage.getItem(this.$refs.input.name)
      const arr = JSON.parse(JSON.stringify(value ? value : this.options))
      const selected = typeof arr === 'object' ? arr.filter(item => item?.selected) : this.options

      this.valueSelected = saveData ? saveData : (selected?.value ? selected?.value : this.value)

      if (this.value !== null && this.value != 0 || saveData?.length) {
        this.$refs.input.value = saveData
        this.$refs.label.classList.add('active')
        this.$refs.iconArrow.classList.add('active')
      }

      this.optionsArr = arr
    },
    hashGenerator(sumString) {
      const symbolArr = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM";
      var randomString = "";
      for (let i = 0; i < sumString; i++) {
        var index = Math.floor(Math.random() * symbolArr.length);
        randomString += symbolArr[index];
      }
      return randomString;
    },
  },
  watch: {
    options: function (newVal, oldVal) {
      this.createdSelect(newVal)
    },
    deep: true,
    immediate: true,
  },
  mounted() {
    // console.log( this.value );
    this.createdSelect()
  }
}
</script>

<style lang="scss" scoped>
.custom-select {
  position: relative;
  width: 100%;
  margin: 0 15px;
  display: flex;
  cursor: pointer;
  align-items: stretch;
  flex-flow: row wrap;
  /* max-height: 2em; */
  overflow-x: clip;
  margin: 0 auto;
  height: 2.8em;
  line-height: 1em;
  /* overflow: hidden; */

  .wrap {
    display: flex;
    position: relative;
    width: 100%;
    height: 100%;

    border-top: 2px solid var(--orange-rad);
    border-bottom: 2px solid var(--orange-rad);
    border-left: 2px solid var(--orange-rad);
    border-right: 2px solid var(--orange-rad);
    border-radius: 8px;
    background-color: var(--white-text);


    &>label {
      position: absolute;
      color: var(--light-grey);
      top: 1em;
      font-size: .8em;
      font-family: "myriadBold";
      cursor: text;
      transition: transform .2s ease-out, color .2s ease-out;
      left: 50px;
      /* width: 200px; */
      width: fit-content;
      text-align: left;
    }

    &>label.active {
      transform: translate(-40px, -80%) scale(0.6);
      color: var(--light-grey);
      // var(--blue);
    }

    .icon-arrow {
      width: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-left: 2px solid var(--orange-rad);
      border-radius: 0 8px 8px 0;
      background-color: var(--white-text);

      .arrow {
        width: 5px;
        height: 70%;
        display: inline-block;
        position: relative;

        span {
          top: .5rem;
          position: absolute;
          width: .75rem;
          height: .1rem;
          background-color: var(--dark-grey);
          display: inline-block;
          transition: all .2s ease;

          &:first-of-type {
            left: 0;
            transform: rotate(45deg);
          }

          &:last-of-type {
            right: 0;
            transform: rotate(-45deg);
          }
        }

        &.active {
          span {
            &:first-of-type {
              transform: rotate(-45deg);
            }

            &:last-of-type {
              transform: rotate(45deg);
            }
          }
        }
      }
    }

    &>input[type="search"]::-webkit-search-decoration,
    &>input[type="search"]::-webkit-search-cancel-button,
    &>input[type="search"]::-webkit-search-results-button,
    &>input[type="search"]::-webkit-search-results-decoration {
      display: none;
    }

    &>input::-webkit-outer-spin-button,
    &>input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    &>input[type=number] {
      -moz-appearance: textfield;
      /* Firefox */
    }

    input[type="number"]::placeholder {
      color: var(--black-text);
    }

    &>input {
      width: calc(100% - 43px);
      height: 100%;
      color: var(--black-text);
      padding: 12px 4px 0 10px;
      font-size: 1.5em;
      font-family: "myriadRegular";
      box-sizing: border-box;
      border-radius: 8px 0 0 8px;
      border-width: 0;
    }
  }


  .container {
    -ms-overflow-style: none;
    scrollbar-width: none;
    max-height: 10em;
    overflow: scroll;
    width: calc(100% - 47px);
    z-index: 1;
    position: absolute;
    top: 1.6em;
    border: 2px solid var(--orange-rad);
    border-radius: 0 0 5px 5px;
    border-top: none;
    padding: 10px 0 0 0;

    &>ul {
      list-style-type: none;
      background-color: var(--white-text);
      font-size: 0.7em;
      width: 100%;

      li {
        padding: 6px 10px;
        border-bottom: 1px solid var(--light-grey);
        cursor: pointer;
        color: var(--dark-grey);
        font-size: 1em;
        font-family: 'myriadRegular';
      }

      li.selected {
        background-color: var(--light-grey);
        color: var(--dark-grey);
      }
    }
  }

  .container::-webkit-scrollbar {
    display: none;
    /* Safari and Chrome */
  }

}
</style>
