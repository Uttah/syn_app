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
    v-model="product"
    :items="allProductData"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'ProductSelect',
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
        product: [],
        allProductData: [],
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
      this.assignProduct(this.value)
    },
    apollo: {
      allProductData: {
        query: gql`
          query {
            allProductData: allProducts {
              id
              name
            }
          }`,
        fetchPolicy: 'cache-and-network'
      }
    },
    methods: {
      assignProduct (val) {
        if (val) {
          this.product = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.product = this.product.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.product = this.product.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignProduct(val)
      },
      product: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
