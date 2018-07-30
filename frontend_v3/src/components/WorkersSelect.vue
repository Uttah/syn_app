<template>
  <v-select
    :label="label"
    :required="required"
    :multiple="multiple"
    :disabled="disabled"
    :clearable="clearable && !readonly"
    :readonly="readonly"
    :subordinate="subordinate"
    :hide-details="hideDetails"
    autocomplete
    :combobox="combobox"
    :rules="nonEmptyArrayField"
    v-model="workers"
    :items="allUsersData"
    item-text="shortName"
    item-value="id"
    :filter="fullNameFilter"
  >
    <template slot="item" slot-scope="data">
      <v-list-tile-content>
        <v-list-tile-title>{{ data.item.fullName }}</v-list-tile-title>
      </v-list-tile-content>
    </template>
  </v-select>
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'WorkersSelect',
    props: {
      value: null,
      label: String,
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      subordinate: Boolean,
      combobox: Boolean
    },
    data () {
      return {
        workers: [],
        allUsersData: [],
        searchUsers: null,
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
      this.assignWorkers(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query($search: String, $subordinate: Boolean) {
            allUsers(search: $search, subordinate: $subordinate){
              id
              shortName
              fullName
              funcRoles
              hasSignature
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allUsers)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchUsers,
            subordinate: this.subordinate
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues.forEach(item => {
          if (this.allUsersData.findIndex(i => i.id === item.id) === -1) {
            this.allUsersData.push(item)
          }
        })
        this.allUsersData.sort((a, b) => a.shortName.localeCompare(b.shortName))
      },
      assignWorkers (val) {
        this.workers = val
        if (val) {
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.workers = this.workers.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.workers = this.workers.id
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allUsersData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filteredUsers = this.allUsersData.filter(item => this.workers.some(id => item.id === id))
          const shortString = filteredUsers.map(item => item.shortName).join(', ')
          this.$emit('update:displayText', shortString)
        }
      },
      fullNameFilter (item, queryText) {
        if (!queryText || !item || !item.fullName) {
          return true
        } else {
          return item.fullName.toUpperCase().indexOf(queryText.toUpperCase()) > -1
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignWorkers(val)
      },
      workers: function (val) {
        if (val && this.combobox) {
          this.$emit('getSignature', val)
          if (typeof val === 'object') {
            val = val.shortName
          }
        }
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
