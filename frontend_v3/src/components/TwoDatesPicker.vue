<template>
  <v-menu ref="menu" lazy v-model="dialog" transition="scale-transition"
          offset-y full-width :nudge-right="40" :disabled="disabled || readonly" min-width="280px">
    <v-text-field slot="activator" :label="label" v-model="getRussianPeriod" :required="required" :disabled="disabled"
                  :hide-details="hideDetails" readonly prepend-icon="event" @focus="$emit('focus')"
                  @blur="$emit('blur')" style="min-width: 280px"/>
    <v-card @click.native.stop width="280" class="px-2 pt-2 pb-1">
      <v-layout>
        <v-flex xs5 ml-2>
          <date-picker label="Начало" v-model="innerValue.dateStart" clearable :hideIcon="true" hide-details/>
        </v-flex>
        <v-spacer/>
        <v-flex xs5 mr-2>
          <date-picker label="Конец" v-model="innerValue.dateEnd" :hideIcon="true" :second-date="innerValue.dateStart" clearable
                       hide-details/>
        </v-flex>
      </v-layout>
    </v-card>
  </v-menu>
</template>

<script>
  import DatePicker from './DatePicker'
  import utilMixin from './utils'

  export default {
    name: 'TwoDatesPicker',
    mixins: [utilMixin],
    components: {
      DatePicker
    },
    props: {
      value: {
        type: Object,
        default: () => {
          return {
            dateStart: null,
            dateEnd: null
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
        return this.innerValue.dateStart === null && this.innerValue.dateEnd === null
      },
      getRussianPeriod () {
        if (this.selectAll) {
          return null
        }
        let result = ''
        if (this.innerValue.dateStart) {
          result += 'с ' + this.formatDate(this.innerValue.dateStart)
        }
        if (this.innerValue.dateEnd) {
          result += ' по ' + this.formatDate(this.innerValue.dateEnd)
        }
        return result.trim()
      }
    },
    watch: {
      'innerValue.dateStart': function (val) {
        if (val && this.innerValue.dateEnd) {
          if (this.getDateByMnth(val) > this.getDateByMnth(this.innerValue.dateEnd)) {
            this.innerValue.dateEnd = null
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
