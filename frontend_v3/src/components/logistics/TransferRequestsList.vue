<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Заявки на перемещения</span>
        <v-spacer/>
        <v-checkbox
          class="pt-5"
          label="Ожидающие моих действий"
          v-model="transferFilter.myActions"
          style="max-width: 300px; margin-right: -20px;"
        />
        <v-checkbox
          class="pt-5"
          label="С моим участием"
          v-model="transferFilter.myPartic"
          style="max-width: 180px; margin-right: -20px;"
        />
        <header-filter class="pt-4" @clearFilters="clearFilters">
          <v-layout row wrap justify-center>
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-months-picker v-model="transferFilter.dateRange" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <projects-select label="Проекты" v-model="transferFilter.projects" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <storage-select label="Склад" v-model="transferFilter.storage" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Создатель" v-model="transferFilter.workers" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select label="Статус" :items="statuses" v-model="transferFilter.status"/>
            </v-flex>
          </v-layout>
        </header-filter>

        <v-text-field class="pr-3"
                      label="Поиск (№ заявки)"
                      append-icon="search"
                      hide-details
                      v-model="searchQuery"
                      style="max-width: 350px;"/>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="transferItems.transferRequests"
        :total-items="transferItems.totalCount"
        :pagination.sync="pagination"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        :rows-per-page-items="rpp"
        :rows-per-page-text="'Строк на странице'"
        :no-data-text="'Нет доступных данных'"
        must-sort
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr @click="openRequisit(props.item.id)" :class="{procurementWarning: props.item.needAttention && auth.hasPermission('logistics.is_logist')}">
            <td>{{props.item.id}}</td>
            <td>
              <users-chip :users="Array(props.item.whoRequested)"/>
            </td>
            <td>{{formatDate(props.item.creationDate)}}</td>
            <td class="text-xs-center">
              <div>Проект {{props.item.where.project.number}} - {{props.item.where.project.description}}</div>
              <div>Местонахождение - {{props.item.where.name}}</div>
            </td>
            <td>{{props.item.status}}</td>
          </tr>
        </template>
        <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
          С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
  import utilMixin from '../utils'
  import _ from 'lodash'
  import auth from '../../auth/auth'
  import {pagedTransferRequests} from './query'
  import HeaderFilter from '../HeaderFilter'
  import ProjectsSelect from '../ProjectsSelect'
  import StorageSelect from '../StorageSelect'
  import DatePicker from '../DatePicker'
  import TwoMonthsPicker from '../TwoMonthsPicker'
  import WorkersSelect from '../WorkersSelect'
  import UsersChip from '../UsersChip'

  export default {
    name: 'TransferRequestsList',
    metaInfo: {
      title: 'Заявки на перемещения'
    },
    components: {
      HeaderFilter,
      ProjectsSelect,
      StorageSelect,
      DatePicker,
      TwoMonthsPicker,
      WorkersSelect,
      UsersChip
    },
    mixins: [utilMixin],
    data () {
      return {
        auth: auth,
        statuses: ['Создана', 'Выполняется', 'Выполнена'],
        transferFilter: {
          projects: [],
          storage: null,
          dateRange: {
            monthStart: null,
            monthEnd: null
          },
          workers: [],
          status: null,
          myPartic: false,
          myActions: false
        },
        transferItems: [],
        searchText: '',
        searchQuery: '',
        loadingQueriesCount: 0,
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'number'
        }),
        headers: [
          {text: '№ заявки', align: 'left', value: 'number'},
          {text: 'Запросил', align: 'left', sortable: false, value: 'request'},
          {text: 'Создана', align: 'left', value: 'creationDate'},
          {text: 'Куда', align: 'center', value: 'where'},
          {text: 'Статус и выполнение', align: 'left', sortable: false, value: 'status'}
        ]
      }
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: pagedTransferRequests,
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
              projects: this.transferFilter.projects,
              creators: this.transferFilter.workers,
              warehouses: this.transferFilter.storage,
              dateRange: this.transferFilter.dateRange,
              status: this.transferFilter.status,
              actions: this.transferFilter.myActions,
              partic: this.transferFilter.myPartic
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.transferItems = JSON.parse(JSON.stringify(data.pagedTransferRequests))
        }
      }
    },
    methods: {
      openRequisit (val) {
        this.$router.push({
          name: 'transfer_request',
          params: {id: val}
        })
      },
      clearFilters () {
        this.transferFilter = {
          workers: [],
          projects: []
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'number'
        }
      },
      searchOperation: _.debounce(function () {
        this.searchText = this.searchQuery
      }, 500)
    },
    watch: {
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      transferFilter: {
        handler: function () {
          this.$apollo.queries.query.refetch()
          this.pagination.page = 1
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
  .filter-padding {
    padding-left: 40px;
    padding-right: 40px
  }
</style>
