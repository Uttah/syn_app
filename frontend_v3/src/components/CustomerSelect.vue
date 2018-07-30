<template>
  <div>
    <v-select
      :items="allCustomers"
      :label="label"
      :readonly="readonly"
      :required="required"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      v-model="innerValue"
      :rules="rules"
      item-text="name"
      item-value="id"
      autocomplete
    >
      <template slot="no-data">
          <span class="px-3 subheading">Ни одного заказчика не найдено.
            <v-btn @click="customerMenu = true" small>Создать нового</v-btn>
          </span>
      </template>
    </v-select>
    <client-name-picker @closeDialog="closeDialog" @success="success" :propDialog="customerMenu" hide-row-activator/>
  </div>
</template>

<script>
  import gql from 'graphql-tag'
  import ClientNamePicker from './ClientNamePicker'

  export default {
    name: 'CustomerSelect',
    components: {
      ClientNamePicker
    },
    props: {
      label: {
        type: String,
        default: 'Заказчик'
      },
      readonly: Boolean,
      required: Boolean,
      value: String,
      inStart: Boolean
    },
    apollo: {
      allCustomers: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            allCustomers: allClients {
              id
              name
            }
          }`,
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        allCustomers: [],
        customerMenu: false,
        allCompanies: [],
        loadingQueriesCount: 0,
        innerValue: this.value,
        rules: [
          text => {
            if (this.required) {
              return !!text || 'Поле не может быть пустым'
            } else {
              return true
            }
          }
        ]
      }
    },
    computed: {
      allCustomersText () {
        return this.allCompanies.map(item => item.name)
      }
    },
    methods: {
      closeDialog () {
        this.customerMenu = false
      },
      success (val) {
        this.$apollo.queries.allCustomers.refetch().then(() => {
          this.innerValue = val.id
        })
      }
    },
    watch: {
      value (newValue) {
        this.innerValue = newValue
      },
      innerValue (newValue) {
        this.$emit('input', newValue)
      }
    }
  }
</script>
