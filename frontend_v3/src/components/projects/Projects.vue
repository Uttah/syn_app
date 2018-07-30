<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Проекты</span>
        <v-spacer/>
        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="pb-4">
            <v-flex xs11 class="filter-padding">
              <workers-select class="pr-3" label="ГИП" v-model="projectsFilter.gip" clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select class="pr-3" :items="allStatesData" v-model="projectsFilter.state" item-text="name" item-value="id"
                        label="Этап" clearable autocomplete hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select
                class="pr-3"
                label="Заказчик"
                :items="allClientsData"
                item-text="name"
                item-value="id"
                v-model="projectsFilter.customer"
                autocomplete
                hide-details
                clearable
              />
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select class="pr-3" label="Менеджер" v-model="projectsFilter.manager" clearable hide-details/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field class="pr-3"
                      label="Поиск"
                      append-icon="search"
                      v-model="searchQuery"
                      style="max-width: 350px;"
        />
        <create-project-dialog @created="created"/>
        <UpdateDeleteProjectDialog :input="input" @deleted="deleted" @updated="updated"/>

      </v-toolbar>
    </v-card-title>
    <v-data-table must-sort :pagination.sync="pagination" :total-items="allProjectsData.totalCount"
                  :loading="loadingQueriesCount > 0 ? 'loading' : false"
                  :headers="headers"
                  :items="allProjectsData.projects"
                  :rows-per-page-items="rpp"
                  :rows-per-page-text="'Строк на странице'"
                  :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr @click="updateDialog(props.item)">
          <td class="text-xs-center">{{ pad(props.item.number, 5) }}</td>
          <td class="text-xs-center">{{ props.item.dateCreated ? formatDate(props.item.dateCreated) : '' }}
            <div>{{ props.item.userCreated ? props.item.userCreated.shortName : '' }}</div>
          </td>
          <td class="text-xs-center">{{ props.item.customer ? props.item.customer.name : '' }}</td>
          <td>{{ props.item.description }}</td>
          <td class="text-xs-center">{{ props.item.manager ? props.item.manager.shortName : 'Нет менеджера' }}
            <div>{{ props.item.gip.shortName}}</div>
          </td>
          <td class="text-xs-center">{{ props.item.state.name }}</td>
          <td>{{ props.item.comment}}</td>
          <td class="text-xs-center" v-html="props.item.budget ? props.item.budget + ' \u20BD' : ''"></td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {pagedProjects, allForFillSelect} from './query'
  import CreateProjectDialog from './CreateProject'
  import UpdateDeleteProjectDialog from './UpdateDeleteProjects'
  import utilMixin from '../utils'
  import _ from 'lodash'
  import WorkersSelect from '../WorkersSelect'
  import FloatField from '../FloatField'
  import HeaderFilter from '../HeaderFilter'

  export default {
    name: 'Projects',
    metaInfo: {
      title: 'Проекты'
    },
    mixins: [utilMixin],
    components: {
      CreateProjectDialog,
      UpdateDeleteProjectDialog,
      WorkersSelect,
      FloatField,
      HeaderFilter
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: pagedProjects,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              sortBy: this.pagination.sortBy,
              search: this.searchText
            },
            filters: this.projectsFilter
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.allProjectsData = data.pagedProjects
        }
      },
      query2: {
        fetchPolicy: 'cache-and-network',
        query: allForFillSelect,
        update (data) {
          this.allStatesData = data.allStates
          this.allClientsData = data.allClients
        }
      }
    },
    data () {
      return {
        allProjectsData: [],
        allStatesData: [],
        allClientsData: [],
        input: {},
        headers: [
          {text: '№ проекта', align: 'center', value: 'number'},
          {text: 'Дата/Кем внесен', align: 'center', value: 'date', sortable: false},
          {text: 'Заказчик', align: 'center', value: 'customer'},
          {text: 'Описание', align: 'center', value: 'description', sortable: false, width: '30%'},
          {text: 'Менеджер/ГИП', align: 'center', value: 'gip', sortable: false},
          {text: 'Этап проекта', align: 'center', value: 'state'},
          {text: 'Комментарий', align: 'center', value: 'comment', sortable: false, width: '30%'},
          {text: 'Примерный бюджет', align: 'center', value: 'budget'}
        ],
        rpp: [25, 50, 100],
        searchText: this.getValue('searchProjects', ''),
        searchQuery: this.getValue('searchProjects', ''),
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'number'
        }),
        loadingQueriesCount: 0,
        projectsFilter: this.getValue('filters', {
          gip: null,
          state: null,
          manager: null,
          customer: null
        })
      }
    },
    created: function () {
      // Убираем фильтр "Все" для записей
      if (this.pagination.rowsPerPage < 0) {
        this.pagination.rowsPerPage = this.rpp[this.rpp.length - 1]
      }
    },
    watch: {
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchProjects', val)
        }
      },
      projectsFilter: {
        handler: function (val) {
          this.storeValue('filters', val)
          this.$apollo.queries.query.refetch()
          this.pagination.page = 1
        },
        deep: true
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      }
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      created () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Проект создан'
        })
        this.$apollo.queries.query.refetch()
      },
      deleted () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Проект удален'
        })
        this.$apollo.queries.query.refetch()
      },
      updated () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Проект обновлен'
        })
        this.$apollo.queries.query.refetch()
      },
      updateDialog (input) {
        this.input = JSON.parse(JSON.stringify(input))
      },
      clearFilters () {
        this.projectsFilter = {
          gip: null,
          state: null,
          manager: null,
          customer: null
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'number'
        }
      }
    }
  }
</script>
