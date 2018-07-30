<template>
  <v-select
    v-model="innerValue"
    :label="label"
    :required="required"
    :readonly="readonly"
    :clearable="clearable"
    autocomplete
    :disabled="disabled"
    :hide-details="hideDetails"
    :items="occupations"
    :loading="loadingQueriesCount > 0 ? 'loading' : false"
    item-text="name"
    item-value="id"/>
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'occupation-filter',
    props: {
      label: {
        type: String,
        default: 'Сотрудники'
      },
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      disabled: Boolean,
      hideDetails: Boolean,
      value: String
    },
    apollo: {
      occupations: {
        fetchPolicy: 'cache-and-network',
        query: gql`{
          allOccupations {
            id
            user {
              id
              shortName
            }
          }
        }`,
        update (data) {
          return data.allOccupations.map(item => {
            return {id: item.id, name: item.user.shortName}
          })
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        loadingQueriesCount: 0,
        innerValue: this.value,
        occupations: []
      }
    },
    watch: {
      value (val) {
        this.innerValue = val
      },
      innerValue (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
