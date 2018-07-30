<template>
  <v-select
    :label="label"
    v-model="reason"
    :hide-details="hideDetails"
    :items="reasons"
    :rules="rules"
    :readonly="readonly"
    :multiple="multiple"
    :required="required"
    :disabled="disabled"
    item-text="name"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'absence-reason-picker',
    props: {
      label: {
        type: String,
        default: 'Причина'
      },
      hideDetails: Boolean,
      multiple: Boolean,
      required: Boolean,
      disabled: Boolean,
      readonly: Boolean,
      value: [String, Array]
    },
    apollo: {
      reasons: {
        query: gql`{
          reasons: absenceReasons {
            id
            name
          }
        }`
      }
    },
    data () {
      return {
        reason: this.value,
        reasons: [],
        rules: [
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
    watch: {
      value (newValue) {
        this.reason = newValue
      },
      reason (newValue) {
        this.$emit('input', newValue)
      }
    }
  }
</script>
