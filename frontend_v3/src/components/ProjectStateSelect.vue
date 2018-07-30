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
    v-model="states"
    :items="allStatesData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ProjectStateSelect',
    props: {
      value: null,
      label: String,
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      displayText: String
    },
    data () {
      return {
        testQwe: [],
        states: [],
        allStatesData: [],
        searchStates: null,
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
      this.assignStates(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allStates{
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allStates)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchStates
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues.forEach(item => {
          if (this.allStatesData.findIndex(i => i.id === item.id) === -1) {
            this.allStatesData.push(item)
          }
        })
        this.allStatesData.sort((a, b) => a.name.localeCompare(b.name))
      },
      assignStates (val) {
        if (val) {
          this.states = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.states = this.states.map(item => item.id, item => item.name)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.states = this.states.name
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allStatesData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filtered = this.allStatesData.filter(item => this.states.some(id => item.id === id))
          const shortString = filtered.map(item => item.name).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignStates(val)
      },
      states: function (val) {
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
