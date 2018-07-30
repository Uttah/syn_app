<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <v-spacer/>
        <projects-select class="mr-3" currentGip v-model="projects" multiple label="Фильтр по проектам"/>
        <create-task @tasksChanged="tasksChanged"/>
        <task-dialog @tasksChanged="tasksChanged" :input="selected" ref="taskDialog"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      style="margin-left: auto; margin-right: auto; max-width: 1500px"
      :headers="headers"
      :items="tasksOnProjects.tasks"
      :total-items="tasksOnProjects.totalCount"
      :pagination.sync="pagination"
      :rows-per-page-items="rpp"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      rows-per-page-text="Строк на странице"
      no-data-text="Нет доступных данных"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr @click="selectMethod (props.item)">
          <td class="tableLine">{{ pad(props.item.project.number, 5) }} - {{ props.item.project.description }}</td><!--Проект-->
          <td class="tableLine">{{ props.item.name }}</td><!--Задача-->
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import ProjectsSelect from '../ProjectsSelect'
  import TaskDialog from './TaskDialog'
  import CreateTask from './CreateTask'
  import {tasksOnProjects} from './query'
  import UtilsMixin from '../utils'

  export default {
    name: 'Tasks',
    metaInfo: {
      title: 'Задачи'
    },
    mixins: [
      UtilsMixin
    ],
    components: {
      ProjectsSelect,
      TaskDialog,
      CreateTask
    },
    data () {
      return {
        created: false,
        projects: [],
        tasksOnProjects: [],
        selected: {
          id: null,
          projectId: null,
          name: ''
        },
        pagination:
          {
            rowsPerPage: 10,
            descending: true,
            page: 1,
            totalItems: 0,
            sortBy: 'project'
          },
        headers: [
          {text: 'Проект', align: 'center', sortable: true, value: 'project'},
          {text: 'Задача', align: 'center', sortable: true, value: 'task'}
        ],
        rpp: [
          5, 10, 25, {text: 'Все', value: -1}
        ],
        loadingQueriesCount: 0
      }
    },
    apollo: {
      tasksOnProjects: {
        fetchPolicy: 'cache-and-network',
        query: tasksOnProjects,
        variables () {
          return {
            paged: {
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              first: this.pagination.rowsPerPage,
              sortBy: this.pagination.sortBy,
              desc: this.pagination.descending
            },
            filters: {
              projects: this.projects
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          return JSON.parse(JSON.stringify(data.tasksOnProjects))
        }
      }
    },
    methods: {
      tasksChanged () {
        this.$apollo.queries.tasksOnProjects.refetch()
      },
      selectMethod (val) {
        this.selected.id = val.id
        this.selected.name = val.name
        this.selected.projectId = val.project.id
        this.$refs.taskDialog.openDialog()
      }
    },
    watch: {
      projects: {
        handler: function (val) {
          this.pagination.page = 1
          this.$apollo.queries.tasksOnProjects.refetch()
        }
      }
    }
  }
</script>

<style scoped>
  .tableLine {
    width: 250px;
    max-width: 250px;
    word-wrap: break-word;
  }
</style>
