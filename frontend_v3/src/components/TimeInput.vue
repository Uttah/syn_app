<template>
  <v-text-field
    :label="label"
    :prepend-icon="prependIcon"
    :disabled="disabled"
    :clearable="clearable"
    :rules="timeValid"
    :required="required"
    :readonly="readonly"
    v-model="timeText"
    @blur="bluredOut"
  />
</template>

<script>
  import utilsMixin from './utils'

  export default {
    name: 'time-input',
    mixins: [utilsMixin],
    props: {
      value: String,
      label: String,
      readonly: Boolean,
      clearable: Boolean,
      disabled: Boolean,
      required: Boolean,
      prependIcon: String
    },
    data () {
      return {
        time: null,
        timeText: this.value ? this.value.slice(0, 5) : null,
        timeValid: [
          text => {
            if (this.required) {
              return !!text || 'Поле не может быть пустым'
            } else {
              return true
            }
          },
          text => {
            if (text) {
              // Сначала проверяем наличие правильных символов
              if (/[^:\d]/.test(text)) {
                return 'Некорректное время'
              }
              // Делим на части
              const parts = text.split(':')
              if (parts.length > 2) {
                return 'Некорректное время'
              }
              if (parts.length === 2) {
                // Должно быть ровно 2 - значит формат 00:00
                if (text.length === 5 || (text.length === 4 && parts[0].length === 1)) {
                  const hours = Number(parts[0])
                  const minutes = Number(parts[1])
                  if (hours > 23 || minutes > 59) {
                    return 'Некорректное время'
                  }
                } else {
                  return 'Некорректное время'
                }
              } else {
                // Одна часть - значит без двоеточия, просто количество часов
                if (text.indexOf(':') > -1) {
                  return 'Некорректное время'
                }
                if (Number(parts[0]) > 23) {
                  return 'Некорректное время'
                }
              }
            }
            return true
          }
        ]
      }
    },
    methods: {
      bluredOut () {
        let newTime = null
        if (this.timeText && this.timeText.length < 3) {
          newTime = this.pad(this.timeText, 2) + ':00'
        } else {
          if (this.timeText && this.timeText.length === 4) {
            newTime = '0' + this.timeText
          } else {
            newTime = !this.timeText ? null : this.timeText
          }
        }
        if (newTime === this.time) {
          this.time = null
          this.$nextTick(() => {
            this.time = newTime
          })
        } else {
          this.time = newTime
        }
      }
    },
    watch: {
      value: function (val) {
        this.timeText = val ? val.slice(0, 5) : ''
      },
      time: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
