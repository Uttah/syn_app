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
    v-model="specification"
    :items="allSpecificationData"
    item-text="displayText"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'
  import utilsMixin from './utils.js'

  export default {
    name: 'SpecificationSelect',
    props: {
      value: null,
      label: {
        type: String,
        default: 'Спецификация'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean
    },
    mixins: [utilsMixin],
    data () {
      return {
        searchSpecification: null,
        specification: [],
        allSpecificationData: [],
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
      this.assignSpecification(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query {
            allSpecification {
              id
              pressmark
              project {
                id
                number
              }
              objectName
              sectionName
              organization
              documentName
              state
              workersData
              dates
              approved
            }
          }`,
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.allSpecificationData = JSON.parse(JSON.stringify(data.allSpecification))
          this.allSpecificationData.forEach(item => {
            item.displayText = `${this.formatProject(item.project.number)} - ${item.pressmark}`
          })
          this.$emit('allSpecification', this.allSpecificationData)
        }
      }
    },
    methods: {
      assignSpecification (val) {
        if (val) {
          this.specification = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.specification = this.specification.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.specification = this.specification.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignSpecification(val)
      },
      specification: function (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
