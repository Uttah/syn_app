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
    v-model="contact"
    :items="allContactsData"
    item-text="lastName"
    item-value="id"
    :search-input.sync="searchContact"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ContactSelect',
    props: {
      value: null,
      idClient: String,
      label: {
        type: String,
        default: 'Контакты'
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
        searchContact: null,
        contact: [],
        allContactsData: [],
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
      this.assignContact(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query ($filters: IntID) {
            allContacts (filters: $filters) {
              id
              lastName
              firstName
              patronum
              phoneNumber
              client {
                id
              }
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.allContactsData = JSON.parse(JSON.stringify(data.allContacts))
        },
        variables () {
          return {
            search: this.searchContact,
            filters: this.idClient
          }
        }
      }
    },
    methods: {
      assignContact (val) {
        if (val) {
          this.contact = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.contact = this.contact.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.contact = this.contact.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignContact(val)
      },
      contact: function (val) {
        this.$emit('input', val)
      },
      allContactsData: function (val) {
        if (Array.isArray(val) && val.length > 0) {
          this.$emit('allContactsData', val)
        }
      }
    }
  }
</script>
