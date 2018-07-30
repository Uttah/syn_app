<template>
  <v-select
    v-model="projects"
    :label="label"
    :required="required"
    :readonly="readonly"
    :clearable="clearable"
    ref="select"
    chips
    autocomplete
    :multiple="multiple"
    :disabled="disabled"
    :hide-details="hideDetails"
    :rules="nonEmptyArrayField"
    :search-input.sync="searchProjects"
    :items="allProjectsData"
    :loading="loadingQueriesCount > 0 ? 'loading' : false"
    item-text="fullDescription"
    item-value="id"
    content-class="width-limit"
    @keyup.native.backspace="clearInput"
  >
    <template slot="selection" slot-scope="data">
      <v-chip :key="data.item.id" class="chip--select-multi chip--project">
        <v-avatar class="accent">{{ data.item.state.letter }}</v-avatar>
        {{ pad(data.item.number, 5) }}
      </v-chip>
    </template>
  </v-select>
</template>

<script>
  import {allProjects} from './reports/query'
  import utilsMixin from './utils'

  export default {
    name: 'ProjectsSelect',
    mixins: [utilsMixin],
    props: {
      value: null,
      label: String,
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      hideDetails: Boolean,
      singleGip: Boolean,
      disabled: Boolean,
      clearable: Boolean,
      currentGip: Boolean
    },
    data () {
      return {
        mountDone: false,
        projects: this.multiple ? [] : null,
        allProjectsData: [],
        gip: null,
        searchProjects: null,
        loadingQueriesCount: 0,
        nonEmptyArrayField: [
          array => {
            if (this.required) {
              if (array && array.length > 0) {
                return true
              } else {
                return 'Поле не может быть пустым'
              }
            }
            return true
          }
        ]
      }
    },
    mounted: function () {
      this.assignProjects(this.value)
      this.mountDone = true
    },
    apollo: {
      query: {
        query: allProjects,
        fetchPolicy: 'cache-and-network',
        update (data) {
          if (this.singleGip && this.multiple) {
            if (this.projects.length > 0) {
              this.allProjectsData = this.allProjectsData.filter(item => item.gip === this.gip)
            }
          }
          data.allProjectsData.forEach(item => {
            if (this.allProjectsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              item.fullDescription = this.pad(item.number, 5) + ' - ' + item.description
              this.allProjectsData.push(item)
            }
          })
          if (this.searchProjects && isNaN(parseInt(this.searchProjects))) {
            this.allProjectsData.sort((a, b) => b.number - a.number)
          } else {
            this.allProjectsData.sort((a, b) => a.number - b.number)
          }
          this.updateDisplayText()
          return null
        },
        loadingKey: 'loadingQueriesCount',
        variables () {
          return {
            search: this.searchProjects,
            require: this.requiredProjects,
            gip: this.gip,
            currentGip: this.currentGip
          }
        },
        skip: function () {
          return !this.mountDone
        }
      }
    },
    methods: {
      assignProjects (val) {
        if (typeof val === 'undefined') {
          val = this.multiple ? [] : null
        }
        if (val) {
          this.projects = val
          if (this.multiple) {
            if (!this.gip && val.length > 0 && this.singleGip) {
              let firstProject = val[0]
              firstProject = this.allProjectsData.find(item => item.id === firstProject)
              if (firstProject) {
                this.gip = firstProject.gip.id
              }
            }
            if (this.gip && val.length === 0) {
              this.gip = null
            }
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.allProjectsData = JSON.parse(JSON.stringify(val))
              this.allProjectsData.forEach(item => {
                item.fullDescription = this.pad(item.number, 5) + ' - ' + item.description
              })
              this.projects = this.projects.map(item => item.id)
            }
          } else {
            if (typeof val === 'object' && !Array.isArray(val)) {
              const mutableVal = JSON.parse(JSON.stringify(val))
              mutableVal.fullDescription = this.pad(val.number, 5) + ' - ' + val.description
              // Эта строчка всё ломала, если перестанет работать - раскоментить?
              // this.allProjectsData = [mutableVal]
              this.projects = this.projects.id
            }
          }
        }
        this.updateDisplayText()
      },
      clearInput () {
        if (!this.multiple && (this.searchProjects === null || this.searchProjects === '') && this.projects !== null) {
          this.$nextTick(() => {
            this.$refs.select.clearableCallback()
            this.$refs.select.blur()
            setTimeout(() => {
              this.$refs.select.focus()
            }, 50)
          })
        }
      },
      updateDisplayText () {
        if (this.multiple) {
          // Из массива allProjectsData берем элементы, которые выбраны в селекте и слепляем их в строку через запятую
          const filteredProjects = this.allProjectsData.filter(item => this.projects.some(id => item.id === id))
          const shortString = filteredProjects.map(item => this.pad(item.number, 5)).join(', ')
          this.$emit('update:displayText', shortString)
        }
      }
    },
    watch: {
      value: function (val) {
        this.assignProjects(val)
      },
      projects: function (val) {
        this.searchProjects = null
        this.$emit('input', val)
        this.updateDisplayText()
      }
    },
    computed: {
      requiredProjects: function () {
        if (this.mountDone) {
          let projects = []
          if (this.projects) {
            projects = Array.isArray(this.projects) ? this.projects : [this.projects]
          }
          const notLoaded = projects.filter(project => {
            return this.allProjectsData.findIndex(item => item.id === Number(project)) < 0
          })
          if (notLoaded.length > 0) {
            return notLoaded
          }
        }
        return null
      }
    }
  }
</script>

<style>
  .chip.chip--project {
    border: none;
  }

  .chip.chip--project .chip__content {
    height: 22px;
    border-radius: 22px;
    font-size: 16px;
    padding-right: 8px;
  }

  .chip.chip--project .avatar {
    height: 22px !important;
    min-width: 22px;
    margin-right: 4px;
    font-size: 14px;
    width: 22px !important;
    color: white !important;
  }

  div.width-limit {
    max-width: 500px;
  }
</style>
