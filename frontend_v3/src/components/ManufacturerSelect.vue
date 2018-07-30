<template>
  <v-select
    :combobox="editable"
    :label="label"
    :required="required"
    :multiple="multiple"
    :disabled="disabled"
    :clearable="clearable"
    :readonly="readonly"
    :hide-details="hideDetails"
    autocomplete
    :rules="nonEmptyArrayField"
    v-model="manufacturer"
    :items="allManufacturerData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import {manufacturers} from './storage/query'

  export default {
    name: 'ManufacturerSelect',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Производитель'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      editable: Boolean,
      alwaysReturnName: Boolean
    },
    data () {
      return {
        manufacturer: null,
        allManufacturerData: [],
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
        ],
        search: null
      }
    },
    mounted: function () {
      this.assignManufacturer(this.value)
    },
    apollo: {
      allManufacturerData: {
        query: manufacturers,
        fetchPolicy: 'cache-and-network'
      }
    },
    methods: {
      assignManufacturer (val) {
        if (val) {
          this.manufacturer = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.manufacturer = this.manufacturer.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.manufacturer = this.manufacturer.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignManufacturer(val)
      },
      manufacturer: function (val) {
        if (this.alwaysReturnName) {
          if (val && val.name) {
            this.$emit('input', val.name)
          } else if (val && Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
            this.$emit('input', val.map(item => item.name))
          } else if (val) {
            this.$emit('input', val)
          }
        } else {
          if (typeof val === 'string') {
            this.$apollo.queries.allManufacturerData.refetch().then(() => {
              this.allManufacturerData.find(item => {
                if (item.name === val) {
                  val = item.id
                }
              })
              this.$emit('input', val)
            })
          } else {
            this.$emit('input', val)
          }
        }
      }
    }
  }
</script>
