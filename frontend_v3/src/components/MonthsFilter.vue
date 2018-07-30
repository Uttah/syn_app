<template>
  <v-select
    :label="label"
    v-model="month"
    :disabled="disabled"
    :clearable="clearable"
    :hide-details="hideDetails"
    :items="months"
    item-text="month"
    item-value="id"
    :loading="loadingQueriesCount > 0 ? 'loading' : false"
  />
</template>

<script>
  import utilMixin from './utils'
  import gql from 'graphql-tag'

  export default {
    name: 'MonthsFilter',
    mixins: [utilMixin],
    props: {
      value: String,
      salaryMonths: Boolean,
      secondDate: String, // Для формы с двумя датами (диапазон дат)
      label: {
        type: String,
        default: 'Период'
      },
      hideDetails: Boolean,
      disabled: Boolean,
      clearable: Boolean,
      isLoading: Boolean
    },
    apollo: {
      firstMonth: {
        fetchPolicy: 'cache-and-network',
        query: gql`{
          firstMonth: lastSalaryMonth
        }`,
        loadingKey: 'loadingQueriesCount',
        skip () {
          return !this.salaryMonths
        }
      }
    },
    data () {
      return {
        firstMonth: null,
        loadingQueriesCount: 0,
        month: this.value
      }
    },
    watch: {
      value: function (val) {
        this.month = val
      },
      month: function (val) {
        this.$emit('input', val)
      },
      firstMonth: function (val) {
        this.month = this.getIdFromMnth(val)
      },
      loadingQueriesCount (val) {
        this.$emit('update:isLoading', val > 0)
      }
    },
    computed: {
      months: function () {
        return this.secondDate ? this.generateFilterDatesRange(this.firstMonth, this.secondDate) : this.generateFilterDates(this.firstMonth)
      }
    }
  }
</script>
