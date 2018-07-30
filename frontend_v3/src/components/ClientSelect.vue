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
    v-model="clients"
    :items="allClientsData"
    item-text="name"
    item-value="id"
    :search-input.sync="searchClient"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ClientSelect',
    props: {
      value: null,
      idClient: String,
      label: {
        type: String,
        default: 'Контрагенты'
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
        searchClient: null,
        clients: [],
        allClientsData: [],
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
      this.assignClient(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allOwnClients {
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          data.allOwnClients.forEach(item => {
            if (this.allClientsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allClientsData.push(item)
            }
          })
          this.allClientsData.sort((a, b) => a.id - b.id)
          this.allClientsData = JSON.parse(JSON.stringify(this.allClientsData))
          this.$emit('allClientsData', this.allClientsData)
        }
      }
    },
    methods: {
      assignClient (val) {
        if (val) {
          this.clients = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.clients = this.clients.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.clients = this.clients.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignClient(val)
      },
      clients: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
