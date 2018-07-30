<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">История взаимодействий</span>
        <v-spacer/>
        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="mt-3 pb-0">
            <v-flex xs11>
              <client-select v-model="filter.clientId" multiple clearable/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field class="pr-3" style="max-width: 300px" label="Поиск" v-model="searchQuery" append-icon="search"/>
        <v-btn color="primary" @click="addClientHistory"
               :disabled="!auth.hasPermission('clients.add_clienthistory')">Добавить</v-btn>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="tableData.clientHistory"
        :total-items="tableData.totalCount"
        :pagination.sync="pagination"
        :rows-per-page-items="rpp"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        rows-per-page-text="Строк на странице"
        no-data-text="Нет доступных данных"
        must-sort
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr @click="editClientHistory(props.item)" :class="{ fired: props.item.wasDeleted }">
            <td>{{ props.item.client.name }}</td>
            <td>{{ formatDate(props.item.date) }}</td>
            <td style="width: 450px; max-width: 450px; word-wrap: break-word;">{{ props.item.interaction.slice(0, 250) }}</td>
            <td>{{ formatDate(props.item.nextStepDate) }}</td>
            <td style="width: 450px; max-width: 450px; word-wrap: break-word;">{{ props.item.nextStep.slice(0, 250) }}</td>
          </tr>
        </template>
        <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
          С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
        </template>
      </v-data-table>
    </v-card-text>
    <client-history-dialog ref="clientHistoryDialog" @success="success" :clientHistory="clientHistoryItem"/>
  </v-card>
</template>

<script>
  import _ from 'lodash'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import {pagedClientHistories} from './query'
  import ClientSelect from '../ClientSelect'
  import ClientHistoryDialog from './ClientHistoryDialog'
  import HeaderFilter from '../HeaderFilter'

  export default {
    name: 'ClientHistory',
    metaInfo: {
      title: 'История взаимодействий'
    },
    mixins: [utilMixin],
    components: {
      ClientSelect,
      ClientHistoryDialog,
      HeaderFilter
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: pagedClientHistories,
        variables () {
          return {
            paged: {
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              first: this.pagination.rowsPerPage,
              sortBy: this.pagination.sortBy,
              desc: this.pagination.descending,
              search: this.searchText
            },
            filters: this.filter
          }
        },
        update (data) {
          this.tableData = JSON.parse(JSON.stringify(data.pagedClientHistories))
          return null
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        auth: auth,
        tableData: [],
        filter: {
          clientId: []
        },
        searchQuery: '',
        searchText: '',
        clientHistoryItem: {
          id: null,
          client: {
            id: null
          }
        },
        headers: [
          {text: 'Контрагент', value: 'client'},
          {text: 'Когда', value: 'date'},
          {text: 'Что сделано', sortable: false, value: 'interaction'},
          {text: 'Дата след. шага', value: 'nextStepDate'},
          {text: 'След. шаг', sortable: false, value: 'nextStep'}
        ],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'date'
        }),
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0
      }
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      addClientHistory () {
        this.clientHistoryItem = {
          id: null,
          client: {
            id: null
          }
        }
        this.$refs.clientHistoryDialog.openDialog()
      },
      editClientHistory (val) {
        if (!val.wasDeleted) {
          this.clientHistoryItem = val
          this.$refs.clientHistoryDialog.openDialog()
        }
      },
      success () {
        this.$apollo.queries.query.refetch()
      },
      clearFilters () {
        this.filter = {
          clientId: []
        }
      }
    },
    watch: {
      searchQuery: function () {
        this.searchOperation()
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        }
      },
      filter: {
        handler: function (val) {
          this.$apollo.queries.query.refetch()
        },
        deep: true
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
