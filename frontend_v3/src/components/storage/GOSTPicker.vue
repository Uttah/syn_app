<template>
  <v-select
    :label="label"
    :items="gostItems"
    item-text="name"
    item-value="id"
    :tags="multiple"
    :multiple="multiple"
    v-model="innerValue"
    :required="required"
    :loading="loadingQueriesCount > 0 ? 'loading' : false"
  />
</template>

<script>
  import gql from 'graphql-tag'

  export default {
    name: 'g-o-s-t-picker',
    props: {
      label: {
        type: String,
        default: 'ГОСТ'
      },
      value: Array,
      required: Boolean,
      multiple: Boolean
    },
    apollo: {
      allGosts: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            allGosts {
              id
              name
            }
          }`,
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        allGosts: [],
        innerValue: this.value,
        loadingQueriesCount: 0
      }
    },
    computed: {
      gostItems () {
        return this.allGosts.map(item => item.name)
      }
    },
    watch: {
      value: {
        handler (val) {
          this.innerValue = val
        },
        deep: true
      },
      innerValue: {
        handler (val) {
          this.$emit('input', val)
        },
        deep: true
      }
    },
    methods: {
      refresh () {
        return this.$apollo.queries.allGosts.refetch()
      }
    }
  }
</script>
