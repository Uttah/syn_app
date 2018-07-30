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
    v-model="tasks"
    :items="allTasksData"
    item-text="displayedName"
    item-value="id"
  />
</template>

<script>
  import gql from 'graphql-tag'
  import utilsMixin from './utils'

  export default {
    name: 'TasksSelect',
    props: {
      projects: Array,
      value: null,
      label: {
        type: String,
        default: 'Задача'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean
    },
    mixins: [
      utilsMixin
    ],
    data () {
      return {
        tasks: [],
        allTasksData: [],
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
      this.assignTasks(this.value)
    },
    apollo: {
      query: {
        query: gql`
          query ($filters: TasksFilter) {
            tasksInReport (filters: $filters) {
              id
              name
              project {
                id
                number
              }
              tasks {
                id
              }
            }
          }`,
        variables () {
          return {
            filters: {
              projects: this.innerProjects
            }
          }
        },
        fetchPolicy: 'cache-and-network',
        update (data) {
          this.allTasksData = JSON.parse(JSON.stringify(data.tasksInReport))
          this.allTasksData.map(item => {
            item.displayedName = `${this.pad(item.project.number, 5)} - ${item.name}`
          })
          if (this.allTasksData.length === 0) {
            this.$emit('show', false)
          } else {
            this.$emit('show', true)
          }
        }
      }
    },
    methods: {
      assignTasks (val) {
        if (val) {
          this.tasks = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.tasks = this.tasks.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.tasks = this.tasks.id
            }
          }
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignTasks(val)
      },
      tasks: function (val) {
        this.$emit('input', val)
      }
    },
    computed: {
      innerProjects () {
        if (this.projects.length > 0 && typeof this.projects[0] === 'object') {
          return this.projects.map(item => item.id)
        } else {
          return this.projects
        }
      }
    }
  }
</script>
