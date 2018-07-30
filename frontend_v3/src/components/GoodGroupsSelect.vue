<template>
  <v-select
    :label="label"
    :required="required"
    :disabled="disabled"
    :clearable="clearable"
    :readonly="readonly"
    :hide-details="hideDetails"
    :multiple="multiple"
    :rules="nonEmptyField"
    v-model="goodGroups"
    :items="allGoodGroupsData"
    item-text="name"
    item-value="id"
    :autocomplete="autocomplete"
  />
</template>

<script>
  import gql from 'graphql-tag'
  export default {
    name: 'good-groups-select',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Группа товаров'
      },
      autocomplete: Boolean,
      required: Boolean,
      disabled: Boolean,
      clearable: Boolean,
      readonly: Boolean,
      hideDetails: Boolean,
      multiple: Boolean
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            allGoodGroups {
                id
                name
            }
           }`,
        update (data) {
          this.allGoodGroupsData = data.allGoodGroups
        }
      }
    },
    data () {
      return {
        allGoodGroupsData: [],
        goodGroups: null,
        nonEmptyField: [
          value => {
            if (this.required) {
              if (value && Array.isArray(value)) {
                return value.length > 0 || 'Поле не может быть пустым'
              } else {
                return !!value || 'Поле не может быть пустым'
              }
            } else {
              return true
            }
          }
        ]
      }
    },
    mounted () {
      this.assignGoodGroups(this.value)
    },
    methods: {
      assignGoodGroups (val) {
        if (val) {
          this.goodGroups = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.goodGroups = this.goodGroups.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.goodGroups = this.goodGroups.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignGoodGroups(val)
      },
      goodGroups: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>

<style scoped>

</style>
