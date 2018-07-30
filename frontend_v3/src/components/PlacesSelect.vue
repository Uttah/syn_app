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
    v-model="places"
    :items="allPlacesData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'PlacesSelect',
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
        places: [],
        allPlacesData: [],
        searchPlaces: null,
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
      this.assignPlaces(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allPlaces{
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.mergeArrays(data.allPlaces)
          this.$nextTick(() => this.$emit('loading-done'))
          this.updateDisplayText()
          return null
        },
        variables () {
          return {
            search: this.searchPlaces
          }
        }
      }
    },
    methods: {
      mergeArrays (newValues) {
        newValues.forEach(item => {
          if (this.allPlacesData.findIndex(i => i.id === item.id) === -1) {
            this.allPlacesData.push(item)
          }
        })
        this.allPlacesData.sort((a, b) => a.name.localeCompare(b.name))
      },
      assignPlaces (val) {
        if (val) {
          this.places = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.mergeArrays(val)
              this.places = this.places.map(item => item.id, item => item.name)
            }
          } else {
            if (typeof val === 'object') {
              this.mergeArrays([val])
              this.places = this.places.name
            }
          }
        }
        this.updateDisplayText()
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allPlacesData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filtered = this.allPlacesData.filter(item => this.places.some(id => item.id === id))
          const shortString = filtered.map(item => item.name).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignPlaces(val)
      },
      places: function (val) {
        this.$emit('input', val)
        this.updateDisplayText()
      }
    }
  }
</script>
