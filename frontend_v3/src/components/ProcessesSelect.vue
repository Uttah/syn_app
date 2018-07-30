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
    v-model="processes"
    :items="allProcessesData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ProcessesSelect',
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
        processes: [],
        allProcessesData: [],
        searchProcesses: null,
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
      this.assignProcesses(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allProcesses {
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allProcesses)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchProcesses
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues.forEach(item => {
          if (this.allProcessesData.findIndex(i => i.id === item.id) === -1) {
            this.allProcessesData.push(item)
          }
        })
        this.allProcessesData.sort((a, b) => a.name.localeCompare(b.name))
      },
      assignProcesses (val) {
        if (val) {
          this.processes = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.processes = this.processes.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.processes = this.processes.id
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allProcessesData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filtered = this.allProcessesData.filter(item => this.processes.some(id => item.id === id))
          const shortString = filtered.map(item => item.name).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignProcesses(val)
      },
      processes: function (val) {
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
