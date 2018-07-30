<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="headline">Информация о сотрудниках</span>
        <v-spacer/>
        <v-text-field append-icon="search" label="Поиск" single-line hide-details
                      v-model="searchQuery" class="mr-2" style="max-width: 400px"/>
        <user-create-dialog @userAdded="userAdded"
                            v-if="auth.hasPermission('users.hire_user') || auth.hasPermission('users.add_user')"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table :items="userTableItems.users" :headers="headers" :rows-per-page-items="rpp"
                  :pagination.sync="pagination"
                  :total-items="userTableItems.totalCount"
                  :rows-per-page-text="'Строк на странице'"
                  :no-data-text="'Нет доступных данных'"
                  :loading="loadingQueriesCount > 0 ? 'loading' : false" must-sort>
      <template slot="items" slot-scope="props">
        <tr @click="showUser(props.item.id)" :class="{ fired: props.item.fired }">
          <td>{{ props.item.fullName }}</td>
          <td v-html="props.item.positions.join('<br/>')"></td>
          <td class="text-xs-center" v-if="auth.hasPermission('users.view_full_user')">{{ props.item.birthDate ? moment(props.item.birthDate).format('D MMMM'):'' }}</td>
          <td>{{ props.item.email }}</td>
          <td class="text-xs-center">{{ formatPhone(props.item.workPhone) }}</td>
          <td class="text-xs-center">{{ formatPhone(props.item.personalPhone) }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {tableQuery} from './query'
  import auth from '../../auth/auth'
  import Alarms from '../Alarms.vue'
  import _ from 'lodash'
  import StringMask from 'string-mask'
  import UserCreateDialog from './CreateDialog.vue'
  import utilsMixin from '../utils'
  import moment from 'moment'

  export default {
    name: 'Users',
    mixins: [utilsMixin],
    components: {
      UserCreateDialog,
      Alarms
    },
    metaInfo: {
      title: 'Список сотрудников'
    },
    apollo: {
      userTableItems: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
        variables () {
          return {
            input: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              search: this.searchText,
              sortBy: this.pagination.sortBy
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    created () {
      if (!auth.hasPermission('users.view_full_user') && this.headers.length === 6) {
        this.headers.splice(2, 1)
      }
    },
    data () {
      return {
        userTableItems: {
          users: [],
          totalCount: 0
        },
        headers: [
          {text: 'Полное имя', value: 'fullName', align: 'left'},
          {text: 'Занимаемые должности', value: 'occupations', sortable: false, align: 'left'},
          {text: 'День рождения', value: 'birthDate', sortable: false, align: 'center'},
          {text: 'Электронная почта', value: 'email', sortable: false, align: 'center', width: '250px'},
          {text: 'Рабочий телефон', value: 'workPhone', sortable: false, align: 'center', width: '250px'},
          {text: 'Личный телефон', value: 'personalPhone', sortable: false, align: 'center', width: '250px'}
        ],
        rpp: [
          10, 25, {text: 'Все', value: -1}
        ],
        searchText: '',
        searchQuery: '',
        loadingQueriesCount: 0,
        errors: [],
        pagination: this.getValue('pagination', {
          rowsPerPage: 10,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'fullName'
        }),
        auth: auth,
        moment: moment
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
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      showUser (id) {
        if (auth.hasPermission('users.edit_user')) {
          this.$router.push({
            name: 'user',
            params: {id: id}
          })
        }
      },
      formatPhone (text) {
        return StringMask.apply(text, '0 (000) 000-00-00')
      },
      userAdded (id) {
        if (id) {
          this.showUser(id)
        }
      }
    }
  }
</script>
