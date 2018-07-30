<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Контроль заполнения табеля</span>
        <v-spacer/>
        <months-filter class="pr-3" v-model="date" hide-details/>
      </v-toolbar>
    </v-card-title>

    <v-data-table
      style="max-width: 800px; margin-left: auto; margin-right: auto"
      :headers="headers"
      :items="filloutTableItems.fillouts"
      :total-items="filloutTableItems.totalCount"
      :pagination.sync="pagination"
      :rows-per-page-items="rpp"
      rows-per-page-text="Строк на странице"
      no-data-text="Нет доступных данных"
      must-sort
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td>{{ props.item.shortName }}</td>
          <td class="text-xs-center">{{ props.item.hasWorkDays }}</td>
          <td class="text-xs-center">{{ props.item.daysMissing }}</td>
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
  import utilMixin from '../utils'
  import WorkersSelect from '../WorkersSelect.vue'
  import MonthsFilter from '../MonthsFilter.vue'

  export default {
    name: 'fillout',
    metaInfo: {
      title: 'Заполнение табеля'
    },
    mixins: [utilMixin],
    components: {
      WorkersSelect,
      MonthsFilter
    },
    apollo: {
      filloutTableItems: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              sortBy: this.pagination.sortBy
            },
            date: this.date
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        filloutTableItems: [],
        pagination: this.getValue('pagination', {
          rowsPerPage: 10,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'shortName'
        }),
        date: Number(this.getDefaultFilterDate()).toString(),
        headers: [
          {text: 'Исполнитель', align: 'left', sortable: true, value: 'shortName'},
          {text: 'Рабочих дней заполнено', align: 'center', sortable: true, value: 'hasWorkDays'},
          {text: 'Дней не хватает(на сегодня)', align: 'center', sortable: true, value: 'daysMissing'}
        ],
        rpp: [10, 25, {text: 'Все', value: -1}],
        loadingQueriesCount: 0
      }
    },
    watch: {
      date: {
        handler: function (val) {
          this.$apollo.queries.filloutTableItems.refetch()
          this.storeValue('filters', val)
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
    }
  }
</script>
