<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Производители</span>
        <v-spacer/>
        <v-text-field class="pr-3"
                      label="Поиск по производителю"
                      append-icon="search"
                      hide-details
                      v-model="searchQuery"
        />
        <v-btn color="submit" @click="changeManufacturer">Смена производителя</v-btn>
        <change-manufacturer ref="changeDialog"/>
        <create-manufacturer @success="success"/>
      </v-toolbar>
    </v-card-title>
    <delete-manufacturer @success="success" :input="input" ref="manufacturerDialog"/>
    <v-data-table
      :headers="headers"
      :items="pagedManufacturers.manufacturers"
      :total-items="pagedManufacturers.totalCount"
      :pagination.sync="pagination"
      :rows-per-page-items="rpp"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      rows-per-page-text="Строк на странице"
      no-data-text="Нет доступных данных"
      must-sort
      style="max-width: 500px"
      class="elevation-1 mx-auto"
    >
      <template slot="items" slot-scope="props">
        <tr class="tableLine" @click="removeDialog(props.item)">
          <td>{{ props.item.name }}</td>
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
  import CreateManufacturer from './CreateManufacturer'
  import ChangeManufacturer from './ChangeManufacturer'
  import DeleteManufacturer from './DeleteManufacturer'
  import _ from 'lodash'
  import utilMixin from '../utils'

  export default {
    name: 'Manufacturers',
    metaInfo: {
      title: 'Производители'
    },
    mixins: [utilMixin],
    components: {
      CreateManufacturer,
      ChangeManufacturer,
      DeleteManufacturer
    },
    data () {
      return {
        input: {
          id: null,
          name: null
        },
        createDialog: false,
        changeDialog: false,
        pagedManufacturers: [],
        searchQuery: this.getValue('searchManufacturers', ''),
        searchText: this.getValue('searchManufacturers', ''),
        pagination: {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'name'
        },
        headers: [
          {text: 'Производитель', align: 'center', value: 'name'}
        ],
        rpp: [25, 50, 100],
        loadingQueriesCount: 0
      }
    },
    apollo: {
      pagedManufacturers: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
        variables () {
          return {
            paged: {
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              first: this.pagination.rowsPerPage,
              sortBy: this.pagination.sortBy,
              desc: this.pagination.descending,
              search: this.searchText
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    methods: {
      // Задержка перед отправкой
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      // Открытие диалога "Смена производителя"
      changeManufacturer () {
        this.$refs.changeDialog.openDialog()
      },
      // Обновление таблицы
      success () {
        this.$apollo.queries.pagedManufacturers.refetch()
      },
      removeDialog (item) {
        this.input = JSON.parse(JSON.stringify(item))
        this.$refs.manufacturerDialog.openDialog()
      }
    },
    watch: {
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchManufacturers', val)
        }
      }
    },
    created: function () {
      // Убираем фильтр "Все" для записей
      if (this.pagination.rowsPerPage < 0) {
        this.pagination.rowsPerPage = this.rpp[this.rpp.length - 1]
      }
    }
  }
</script>
