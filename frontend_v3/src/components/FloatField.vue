<template>
  <v-text-field
    :label="label"
    :required="required"
    :disabled="disabled"
    v-model="convert"
    :rules="isNumber"
    :suffix="suffix"
    :hide-details="hideDetails"
  />
</template>

<script>
  export default {
    name: 'FloatField',
    props: {
      value: Number,
      label: String,
      required: Boolean,
      disabled: Boolean,
      hideDetails: Boolean,
      suffix: String,
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
            let result = /[^\d,.]/.test(text)
            if (result) {
              return 'Только цифры'
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
            return String(this.variable).replace('.', ',')
          } else {
            return ''
          }
        },
        set: function (text) {
          this.variable = text
          const val = parseFloat(this.variable.replace(',', '.'))
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
    }
  }
</script>
