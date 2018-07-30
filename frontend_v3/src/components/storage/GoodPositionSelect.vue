<template>
  <v-select :items="allGoodPositionText"
            :label="label"
            combobox
            :readonly="readonly"
            :hide-details="hideDetails"
            :required="required"
            :clearable="clearable"
            :loading="loadingQueriesCount > 0 ? 'loading' : false"
            v-model="selectedGoodPosition"
            :rules="rules">
  </v-select>
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'GoodPositionSelect',
    props: {
      label: {
        type: String,
        default: 'Товарная позиция'
      },
      readonly: Boolean,
      required: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      value: Object,
      goodKindId: String
    },
    apollo: {
      allGoodPositions: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query ($filters: IntID) {
            allGoodPositions (filters: $filters) {
              id
              descriptionInfo
              unit {
                id
                shortName
              }
            }
          }`,
        loadingKey: 'loadingQueriesCount',
        variables () {
          return {
            filters: this.goodKindId
          }
        },
        update ({allGoodPositions}) {
          this.allGoodPositions = allGoodPositions
          this.updateSelectedGoodPosition()
          return allGoodPositions
        }
      }
    },
    data () {
      return {
        allGoodPositions: [],
        selectedGoodPosition: null,
        loadingQueriesCount: 0,
        innerValue: this.value,
        rules: [
          text => {
            if (this.required) {
              return !!text || 'Поле не может быть пустым'
            } else {
              return true
            }
          }
        ]
      }
    },
    computed: {
      allGoodPositionText () {
        if (this.allGoodPositions) {
          return this.allGoodPositions.map(item => item.descriptionInfo)
        }
      }
    },
    methods: {
      updateSelectedGoodPosition () {
        if (this.innerValue) {
          if (this.innerValue.id) {
            // this.goodKindId = this.innerValue.goodKind.id
            // Ждем обновления данных по сети
            if (this.loadingQueriesCount > 0) {
              return
            }
            if (this.allGoodPositions) {
              const item = this.allGoodPositions.find(item => item.id === this.innerValue.id)
              this.selectedGoodPosition = item ? item.descriptionInfo : null
            } else {
              this.selectedGoodPosition = null
            }
          } else {
            this.selectedGoodPosition = this.innerValue.descriptionInfo
          }
        }
      }
    },
    watch: {
      value: {
        handler: function (newValue) {
          this.innerValue = newValue
          this.updateSelectedGoodPosition()
        },
        deep: true
      },
      selectedGoodPosition: function (newValue) {
        const item = this.allGoodPositions.find(item => item.descriptionInfo === newValue)
        if (item) {
          this.$emit('input', { id: item.id, descriptionInfo: item.descriptionInfo, unit: item.unit })
        } else {
          this.$emit('input', { id: null, descriptionInfo: newValue, unit: {id: null} })
        }
      }
    }
  }
</script>
