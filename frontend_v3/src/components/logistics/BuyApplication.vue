<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Заявки на закупку</span>
        <v-spacer/>
        <v-checkbox
          v-show="auth.hasPermission('logistics.is_logist')"
          class="pt-5"
          label="Показывать выполненые"
          v-model="applicationFilter.showCompleted"
          style="max-width: 300px; margin-right: -20px;"
        />
        <v-checkbox
          v-show="auth.hasPermission('logistics.is_logist')"
          class="pt-5"
          label="Ожидающие моих действий"
          v-model="applicationFilter.myActions"
          style="max-width: 300px; margin-right: -20px;"
        />
        <v-checkbox
          class="pt-5"
          label="С моим участием"
          v-model="applicationFilter.myPartic"
          style="max-width: 180px; margin-right: -20px;"
        />
        <header-filter class="pt-4" @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="pb-4">
            <v-flex xs11 class="filter-padding">
              <projects-select label="Проекты" v-model="applicationFilter.projects" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Запросившие" v-model="applicationFilter.workers" multiple clearable hide-details/>
            </v-flex>
          </v-layout>
        </header-filter>

        <v-text-field class="pr-3"
                      label="Поиск (номер)"
                      append-icon="search"
                      hide-details
                      v-model="searchQuery"
                      style="max-width: 350px;"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="applicationItems.logisticsRequests"
      :total-items="applicationItems.totalCount"
      :pagination.sync="pagination"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr @click="openRequisition(props.item.id)" :class="{procurementWarning: props.item.needAttention && auth.hasPermission('logistics.is_logist'),
        checked: props.item.requestCompleted}"
        @hover="">
          <td>{{props.item.id}}</td>
          <td>{{formatDate(props.item.whenRequested)}}</td>
          <td>{{props.item.whoRequested.shortName}}</td>
          <td>{{pad(props.item.goal.project.number, 5)}} - {{props.item.goal.project.description}}</td>
          <td>Спецификация {{props.item.goal.name}}</td>
          <td>{{formatDate(props.item.deadline)}}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import utilMixin from '../utils'
  import _ from 'lodash'
  import auth from '../../auth/auth'
  import {pagedLogisticsRequest} from './query'
  import HeaderFilter from '../HeaderFilter'
  import WorkersSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'

  export default {
    name: 'BuyRequisition',
    metaInfo: {
      title: 'Заявки на закупку'
    },
    mixins: [utilMixin],
    components: {
      HeaderFilter,
      WorkersSelect,
      ProjectsSelect
    },
    data () {
      return {
        auth: auth,
        applicationFilter: this.getValue('filter', {
          projects: [],
          workers: [],
          myPartic: false,
          myActions: false,
          showCompleted: false
        }),
        applicationItems: [],
        searchText: '',
        searchQuery: '',
        loadingQueriesCount: 0,
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'applicationDate'
        }),
        headers: [
          {text: '№ заявки', align: 'left', value: 'number'},
          {text: 'Дата заявки', align: 'left', value: 'applicationDate'},
          {text: 'Запросил', align: 'left', sortable: false, value: 'request'},
          {text: 'Проект', align: 'left', value: 'project'},
          {text: 'Цель закупки', align: 'left', sortable: false, value: 'specification'},
          {text: 'Крайний срок', align: 'left', value: 'deadline'}
        ]
      }
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: pagedLogisticsRequest,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              search: this.searchText,
              sortBy: this.pagination.sortBy
            },
            filters: {
              projects: this.applicationFilter.projects,
              requested: this.applicationFilter.workers,
              actions: this.applicationFilter.myActions,
              partic: this.applicationFilter.myPartic,
              showCompleted: this.applicationFilter.showCompleted
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.applicationItems = JSON.parse(JSON.stringify(data.pagedLogisticsRequest))
        }
      }
    },
    methods: {
      openRequisition (val) {
        this.$router.push({
          name: 'logistic_request',
          params: {id: val}
        })
      },
      clearFilters () {
        this.applicationFilter = {
          workers: [],
          projects: []
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'applicationDate'
        }
      },
      searchOperation: _.debounce(function () {
        this.searchText = this.searchQuery
      }, 500)
    },
    watch: {
      applicationFilter: {
        handler: function (val) {
          this.storeValue('filter', val)
        },
        deep: true
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      searchQuery: function () {
        this.searchOperation()
      }
    }
  }
</script>

<style>
  tr.procurementWarning:hover {
    background-color: rgba(0, 0, 0, .06) !important;
  }
</style>
