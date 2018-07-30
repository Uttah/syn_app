<template>
  <v-select
    :label="label"
    :required="required"
    :multiple="multiple"
    :disabled="disabled"
    :clearable="clearable"
    :readonly="readonly"
    :hide-details="hideDetails"
    autocomplete
    :rules="nonEmptyArrayField"
    v-model="clientKind"
    :items="allClientKindsData"
    item-text="name"
    item-value="id"
    :search-input.sync="searchClientKind"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ClientKindSelect',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Тип контрагента'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean
    },
    data () {
      return {
        searchClientKind: null,
        clientKind: [],
        allClientKindsData: [],
        nonEmptyArrayField: [
          array => {
            if (this.required) {
              if (array && Array.isArray(array)) {
                return array.length > 0 || 'Поле не может быть пустым'
              } else {
                return !!array || 'Поле не может быть пустым'
              }
            } else {
              return true
            }
          }
        ]
      }
    },
    mounted: function () {
      this.assignClientKind(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allClientKinds{
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          data.allClientKinds.forEach(item => {
            if (this.allClientKindsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allClientKindsData.push(item)
            }
          })
          this.allClientKindsData.sort((a, b) => a.id - b.id)
        },
        variables () {
          return {
            search: this.searchClientKind
          }
        }
      }
    },
    methods: {
      assignClientKind (val) {
        if (val) {
          this.clientKind = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.clientKind = this.clientKind.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.clientKind = this.clientKind.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignClientKind(val)
      },
      clientKind: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
