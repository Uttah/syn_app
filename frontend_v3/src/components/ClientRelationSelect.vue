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
    v-model="clientRelation"
    :items="allClientRelationsData"
    item-text="name"
    item-value="id"
    :search-input.sync="searchClientRelation"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ClientRelationSelect',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Взаимоотношения'
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
        searchClientRelation: null,
        clientRelation: [],
        allClientRelationsData: [],
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
      this.assignClientRelation(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allClientRelations{
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          data.allClientRelations.forEach(item => {
            if (this.allClientRelationsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allClientRelationsData.push(item)
            }
          })
          this.allClientRelationsData.sort((a, b) => a.id - b.id)
        },
        variables () {
          return {
            search: this.searchClientRelation
          }
        }
      }
    },
    methods: {
      assignClientRelation (val) {
        if (val) {
          this.clientRelation = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.clientRelation = this.clientRelation.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.clientRelation = this.clientRelation.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignClientRelation(val)
      },
      clientRelation: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
