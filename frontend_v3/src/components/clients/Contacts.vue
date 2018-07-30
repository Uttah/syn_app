<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Контакты</span>
        <v-spacer/>
        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="mt-3 pb-0">
            <v-flex xs11>
              <client-select label="Контрагент" v-model="filters.clientId" clearable multiple/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field class="pr-3" label="Поиск" style="max-width: 300px" v-model="searchQuery"/>
        <v-btn color="primary" @click="createContact"
               :disabled="!auth.hasPermission('clients.add_contact')">Добавить контакт</v-btn>
      </v-toolbar>
    </v-card-title>
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
        <tr @click="editContact(props.item)">
          <td>{{ props.item.lastName }} {{ props.item.firstName }} {{ props.item.patronum }}</td>
          <td>{{ props.item.position }}</td>
          <td>{{ props.item.phoneNumber }}</td>
          <td>{{ props.item.client.name }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <ContactDialog @success="success" :withClient="withClient" :contact="contact" ref="contactDialog"/>
  </v-card>
</template>

<script>
  import _ from 'lodash'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import {pagedContacts} from './query'
  import ContactDialog from './ContactDialog'
  import ClientSelect from '../ClientSelect'
  import HeaderFilter from '../HeaderFilter'

  export default {
    name: 'Contacts',
    metaInfo: {
      title: 'Контакты'
    },
    mixins: [utilMixin],
    components: {
      ContactDialog,
      ClientSelect,
      HeaderFilter
    },
    data () {
      return {
        auth: auth,
        contact: {},
        withClient: false,
        headers: [
          {text: 'ФИО', value: 'name'},
          {text: 'Должность', sortable: false, value: 'position'},
          {text: 'Телефон', sortable: false, value: 'phone_number'},
          {text: 'Контрагент', value: 'client'}
        ],
        pagedContacts: [],
        searchQuery: '',
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
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      createContact () {
        this.contact = {
          id: null,
          lastName: null,
          firstName: null,
          patronum: null,
          position: null,
          phoneNumber: null,
          clientId: []
        }
        this.withClient = false
        this.$refs.contactDialog.openDialog()
      },
      editContact (val) {
        this.contact = {
          id: val.id,
          lastName: val.lastName,
          firstName: val.firstName,
          patronum: val.patronum,
          position: val.position,
          phoneNumber: val.phoneNumber,
          clientId: val.client.id
        }
        this.withClient = true
        this.$refs.contactDialog.openDialog()
      },
      success () {
        this.$apollo.queries.pagedContacts.refetch()
      },
      clearFilters () {
        this.filters = {
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
        },
        deep: true
      }
    }
  }
</script>
