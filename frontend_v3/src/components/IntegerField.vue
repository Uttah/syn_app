<template>
  <v-text-field
    ref="textField"
    :label="label"
    :required="required"
    :disabled="disabled"
    v-model="convert"
    :rules="isNumber"
    :prepend-icon="prependIcon"
    :name="name"
    :suffix="suffix"
    :autofocus="autofocus"
    :readonly="readonly"
    @focus="$emit('focus')"
    @blur="$emit('blur')"
  />
</template>

<script>
  export default {
    name: 'IntegerField',
    props: {
      value: Number,
      label: String,
      required: Boolean,
      disabled: Boolean,
      prependIcon: String,
      name: String,
      suffix: String,
      autofocus: Boolean,
      readonly: Boolean,
      rules: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        variable: this.value,
        isNumber: [
          text => {
            let result = /[^-\d]/.test(text)
            if (result) {
              return 'Нужно вводить целые числа'
            }
            if (this.required && text === '') {
              return 'Поле не может быть пустым'
            }
            return true
          },
          ...this.rules
        ]
      }
    },
    computed: {
      convert: {
        get: function () {
          if (this.variable) {
            return String(this.variable)
          } else {
            return ''
          }
        },
        set: function (text) {
          this.variable = text
          const val = parseInt(this.variable)
          if (!isNaN(val)) {
            this.$emit('input', val)
          } else if (text === '') {
            this.$emit('input', null)
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.variable = val
      }
    },
    methods: {
      focus () {
        this.$refs.textField.focus()
      }
    }
  }
</script>
