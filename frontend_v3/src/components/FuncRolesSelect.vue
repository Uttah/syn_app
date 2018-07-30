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
    v-model="funcRoles"
    :items="allFuncRolesData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'FuncRolesSelect',
    props: {
      value: null,
      label: String,
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean
    },
    data () {
      return {
        funcRoles: [],
        allFuncRolesData: [],
        searchFuncRoles: null,
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
      this.assignFuncRoles(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allFuncRoles {
              id
              name
              kind
              positions {
                id
              }
              deleted
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allFuncRoles)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchFuncRoles
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues.forEach(item => {
          if (this.allFuncRolesData.findIndex(i => i.id === item.id) === -1) {
            this.allFuncRolesData.push(item)
          }
        })
        this.allFuncRolesData.sort((a, b) => a.name.localeCompare(b.name))
      },
      assignFuncRoles (val) {
        if (val) {
          this.funcRoles = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.funcRoles = this.funcRoles.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.funcRoles = this.funcRoles.id
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allFuncRolesData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filtered = this.allFuncRolesData.filter(item => this.funcRoles.some(id => item.id === id))
          const shortString = filtered.map(item => item.name).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignFuncRoles(val)
      },
      funcRoles: function (val) {
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
