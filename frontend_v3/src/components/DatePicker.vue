<template>
  <v-menu ref="menu" lazy v-model="menu" transition="scale-transition" :close-on-content-click="false"
          offset-y full-width :nudge-right="40" max-width="290px" min-width="290px" :disabled="disabled || readonly">
    <v-text-field v-if="hideIcon" slot="activator" :label="label" v-model="formattedDate" :clearable="clearable" :required="required" :disabled="disabled"
                  readonly :rules="rules" @focus="$emit('focus')" @blur="$emit('blur')" />
    <v-text-field v-else slot="activator" :label="label" v-model="formattedDate" :clearable="clearable" :required="required" :disabled="disabled"
                  readonly prepend-icon="event" :rules="rules" @focus="$emit('focus')" @blur="$emit('blur')" />
    <v-date-picker v-model="internalDate" locale="ru-ru" :first-day-of-week="1"
                   :allowed-dates="allowedDates" no-title scrollable @input="$refs.menu.save(internalDate)">
    </v-date-picker>
  </v-menu>
</template>

<script>
  export default {
    name: 'DatePicker',
    props: ['value', 'allowedDates', 'rules', 'label', 'required', 'disabled', 'readonly', 'clearable', 'hideIcon'],
    data () {
      return {
        menu: false,
        internalDate: this.value
      }
    },
    watch: {
      value: function (val) {
        this.internalDate = val
      },
      internalDate: function (val) {
        this.$emit('input', val)
      }
    },
    computed: {
      formattedDate: {
        get () {
          if (this.internalDate) {
            const date = new Date(this.internalDate)
            return date.toLocaleDateString()
          } else {
            return ''
          }
        },
        set (value) {
          if (!value) {
            this.internalDate = null
          }
        }
      }
    }
  }
</script>
