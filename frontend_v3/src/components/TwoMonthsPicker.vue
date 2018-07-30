<template>
  <v-menu ref="menu" lazy v-model="dialog" transition="scale-transition"
          offset-y full-width :nudge-right="40" :disabled="disabled || readonly">
    <v-text-field slot="activator" :label="label" v-model="getRussianPeriod" :required="required" :disabled="disabled"
                  :hide-details="hideDetails" readonly prepend-icon="event" @focus="$emit('focus')"
                  @blur="$emit('blur')" style="min-width: 320px"/>
    <v-card @click.native.stop width="400px" class="px-2 pt-2 pb-3">
      <v-layout>
        <v-flex xs6 mx-2>
          <months-filter label="Начало" v-model="innerValue.monthStart" clearable hide-details/>
        </v-flex>
        <v-flex xs6 mx-2>
          <months-filter label="Конец" v-model="innerValue.monthEnd" :second-date="innerValue.monthStart" clearable
                         hide-details/>
        </v-flex>
      </v-layout>
    </v-card>
  </v-menu>
</template>

<script>
  import MonthsFilter from './MonthsFilter'
  import utilMixin from './utils'

  export default {
    name: 'TwoMonthsPicker',
    mixins: [utilMixin],
    components: {
      MonthsFilter
    },
    props: {
      value: {
        type: Object,
        default: () => {
          return {
            monthStart: null,
            monthEnd: null
          }
        }
      },
      label: {
        type: String,
        default: 'Период'
      },
      hideDetails: Boolean,
      required: Boolean,
      disabled: Boolean,
      readonly: Boolean,
      displayText: String
    },
    data () {
      return {
        dialog: false,
        innerValue: this.value
      }
    },
    computed: {
      selectAll: function () {
        return this.innerValue.monthStart === null && this.innerValue.monthEnd === null
      },
      getRussianPeriod () {
        if (this.selectAll) {
          return null
        }
        let result = ''
        if (this.innerValue.monthStart) {
          result += 'с ' + this.getNameOfDate(this.innerValue.monthStart, 1)
        }
        if (this.innerValue.monthEnd) {
          result += ' по ' + this.getNameOfDate(this.innerValue.monthEnd, 0)
        }
        return result.trim()
      }
    },
    watch: {
      'innerValue.monthStart': function (val) {
        if (val && this.innerValue.monthEnd) {
          if (this.getDateByMnth(val) > this.getDateByMnth(this.innerValue.monthEnd)) {
            this.innerValue.monthEnd = null
          }
        }
      },
      value: {
        handler: function (val) {
          this.innerValue = val
        },
        deep: true
      },
      innerValue: {
        handler: function (val) {
          this.$emit('input', val)
        },
        deep: true
      },
      getRussianPeriod: function (val) {
        this.$emit('update:displayText', val)
      }
    }
  }
</script>
