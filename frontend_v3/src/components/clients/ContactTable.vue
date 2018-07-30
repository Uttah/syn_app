<template>
  <v-data-table
    :headers="headers"
    :items="pagedContacts.contacts"
    :total-items="pagedContacts.totalCount"
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
        <td>{{ props.item.lastName }}</td>
        <td>{{ props.item.firstName }}</td>
        <td>{{ props.item.patronum }}</td>
        <td>{{ props.item.position }}</td>
        <td>{{ props.item.phoneNumber }}</td>
        <td>{{ props.item.client ? props.item.client.name : null}}</td>
      </tr>
    </template>
    <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
      С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
    </template>
  </v-data-table>
</template>

<script>
  import {pagedContacts} from './query'
  import utilMixin from '../utils'

  export default {
    name: 'ContactTable',
    mixins: [utilMixin],
    props: {
      contactId: String
    },
    data () {
      return {
        headers: [
          {text: 'Фамилия', value: 'last_name'},
          {text: 'Имя', value: 'first_name'},
          {text: 'Отчество', value: 'patronum'},
          {text: 'Должность', value: 'position'},
          {text: 'Телефон', sortable: false, value: 'phone_number'},
          {text: 'Контрагент', value: 'client'}
        ],
        pagedContacts: [],
        searchText: '',
        filters: {
          clientId: null
        },
        loadingQueriesCount: 0,
        rpp: [10, 25, 50],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'last_name'
        })
      }
    },
    apollo: {
      pagedContacts: {
        fetchPolicy: 'cache-and-network',
        query: pagedContacts,
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
              clientId: this.filters.clientId
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    methods: {
      getFilters (val) {
        this.filters.clientId = val
      }
    },
    watch: {
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      }
    }
  }
</script>
