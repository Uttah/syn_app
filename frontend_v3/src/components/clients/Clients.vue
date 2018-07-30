<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Контрагенты</span>
        <v-spacer/>
        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="mt-3 pb-0">
            <v-flex xs11>
              <client-kind-select label="Тип контрагента" v-model="filters.clientKind" clearable multiple/>
            </v-flex>
            <v-flex xs11>
              <client-relation-select label="Взаимоотношения" v-model="filters.clientRelation" clearable multiple/>
            </v-flex>
          </v-layout>
        </header-filter>

        <v-text-field class="pr-3" style="max-width: 300px" label="Поиск по названию" v-model="searchQuery"/>
        <v-btn color="primary" @click="openCreateClient"
               :disabled="!auth.hasPermission('clients.add_client')">Добавить контрагента</v-btn>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="clientsTableItems.clients"
      :total-items="clientsTableItems.totalCount"
      :pagination.sync="pagination"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr @click="openDialog(props.item)">
          <td>{{ props.item.name }}</td>
          <td>{{ props.item.kind ? props.item.kind.name : null }}</td>
          <td>{{ props.item.relation ? props.item.relation.name : null}}</td>
          <td>{{ props.item.phoneNumber }}</td>
          <td>{{ props.item.manager ? props.item.manager.shortName : null}}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <client-dialog ref="clientDialog" @success="success"/>
    <create-client ref="createClient" @success="success"/>
  </v-card>
</template>

<script>
  import _ from 'lodash'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import {tableQuery} from './query'
  import ClientKindSelect from '../ClientKindSelect'
  import ClientRelationSelect from '../ClientRelationSelect'
  import ClientDialog from './ClientDialog'
  import CreateClient from './CreateClient'
  import HeaderFilter from '../HeaderFilter'

  export default {
    name: 'clients',
    metaInfo: {
      title: 'Контрагенты'
    },
    components: {
      ClientKindSelect,
      ClientRelationSelect,
      ClientDialog,
      CreateClient,
      HeaderFilter
    },
    mixins: [utilMixin],
    apollo: {
      clientsTableItems: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
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
              clientKind: this.filters.clientKind,
              clientRelation: this.filters.clientRelation
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        auth: auth,
        dialog: false,
        clientsTableItems: [],
        searchQuery: '',
        searchText: '',
        filters: {
          clientKind: [],
          clientRelation: []
        },
        headers: [
          {text: 'Название', value: 'name'},
          {text: 'Вид', value: 'kind'},
          {text: 'Взаимоотношения', value: 'relation'},
          {text: 'Телефон', sortable: false, value: 'phone_number'},
          {text: 'Менеджер', value: 'manager'}
        ],
        loadingQueriesCount: 0,
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'name'
        })
      }
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      openDialog (val) {
        let manager = val.manager ? val.manager.id : ''
        if (auth.hasPermission('clients.change_client') || auth.user.id === manager) {
          val = JSON.parse(JSON.stringify(val))
          val.kind = val.kind ? val.kind.id : null
          val.relation = val.relation ? val.relation.id : null
          val.manager = val.manager ? val.manager.id : null
          this.$refs.clientDialog.openDialog(val)
        }
      },
      openCreateClient () {
        this.$refs.createClient.openDialog()
      },
      success () {
        this.$apollo.queries.clientsTableItems.refetch()
      },
      clearFilters () {
        this.filters = {
          clientKind: [],
          clientRelation: []
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
        },
        deep: true
      }
    }
  }
</script>
