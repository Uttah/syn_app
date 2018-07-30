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
    v-model="subProcesses"
    :items="allSubProcessesData"
    item-text="diaplayName"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'SubProcessesSelect',
    props: {
      value: null,
      label: String,
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      showProcessName: Boolean
    },
    data () {
      return {
        subProcesses: [],
        allSubProcessesData: [],
        searchSubProcesses: null,
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
      this.assignSubProcesses(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allSubProcesses {
              id
              name
              process {
                id
                name
              }
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allSubProcesses)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchSubProcesses
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues = JSON.parse(JSON.stringify(newValues))
        newValues.forEach(item => {
          if (this.allSubProcessesData.findIndex(i => i.id === item.id) === -1) {
            this.allSubProcessesData.push(item)
          }
        })
        if (this.showProcessName) {
          this.allSubProcessesData.forEach(item => {
            item.diaplayName = `${item.process.name.substr(0, 3)} - ПП: ${item.name}`
          })
        }
        this.allSubProcessesData.sort((a, b) => a.name.localeCompare(b.name))
      },
      assignSubProcesses (val) {
        if (val) {
          this.subProcesses = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.subProcesses = this.subProcesses.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.subProcesses = this.subProcesses.id
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allSubProcessesData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filtered = this.allSubProcessesData.filter(item => this.subProcesses.some(id => item.id === id))
          const shortString = filtered.map(item => item.name).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignSubProcesses(val)
      },
      subProcesses: function (val) {
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
