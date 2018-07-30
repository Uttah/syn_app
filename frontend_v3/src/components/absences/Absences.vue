<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="headline">Отсутствия сотрудников</span>
        <v-spacer/>
        <two-months-picker class="pr-3" v-model="filters.dateFilter" hide-details/>
        <absence-reason-picker v-model="filters.reasons" hide-details multiple
                               style="max-width: 300px"/>
        <absence-edit-dialog ref="editDialog" @save="saveAbsence" @add="addAbsence"
                             :disable-buttons.sync="queryIsActive" @remove="removeAbsence">
        </absence-edit-dialog>
      </v-toolbar>
    </v-card-title>
    <v-data-table :items="absencesTable.absences" :headers="headers" :rows-per-page-items="rpp"
                  :pagination.sync="pagination"
                  :total-items="absencesTable.totalCount"
                  :rows-per-page-text="'Строк на странице'"
                  :no-data-text="'Нет доступных данных'"
                  :loading="loadingQueriesCount > 0 ? 'loading' : false" must-sort>
      <template slot="items" slot-scope="props">
        <tr @click="showAbsence(props.item)" :class="{ locked: props.item.locked }">
          <td>
            <div>{{ props.item.userAdded.shortName }}</div>
            <div>{{ formatDateTime(props.item.timeAdded) }}</div>
          </td>
          <td>{{ props.item.worker.shortName }}</td>
          <td>{{ constructDate(props.item) }}</td>
          <td class="text-xs-center">{{ props.item.reason.name }}</td>
          <td>{{ props.item.comment }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {tableQuery, addAbsence, updateAbsence, deleteAbsence} from './query.js'
  import MonthsFilter from '../MonthsFilter'
  import utilsMixin from '../utils'
  import moment from 'moment'
  import auth from '../../auth/auth'
  import AbsenceEditDialog from './AbsenceEditDialog'
  import AbsenceReasonPicker from './AbsenceReasonPicker'
  import TwoMonthsPicker from '../TwoMonthsPicker'

  export default {
    components: {
      AbsenceEditDialog,
      MonthsFilter,
      AbsenceReasonPicker,
      TwoMonthsPicker
    },
    mixins: [utilsMixin],
    name: 'absences',
    metaInfo: {
      title: 'Отсутствия сотрудников'
    },
    apollo: {
      absencesTable: {
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
            },
            filters: {
              dateRange: {
                monthStart: this.filters.dateFilter.monthStart,
                monthEnd: this.filters.dateFilter.monthEnd
              },
              reason: this.filters.reasons
            }
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        absencesTable: {
          absences: [],
          totalCount: 0
        },
        headers: [
          {text: 'Добавлено', value: 'added', sortable: false, align: 'left'},
          {text: 'Отсутствующий', value: 'worker', sortable: true, align: 'left'},
          {text: 'Дата, время', value: 'date', sortable: true, align: 'left'},
          {text: 'Причина', value: 'reason', sortable: true, align: 'center'},
          {text: 'Комментарий', value: 'comment', sortable: false, align: 'center', width: '40%'}
        ],
        rpp: [25, 50, 100],
        loadingQueriesCount: 0,
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'date'
        }),
        filters: this.getValue('filters', {
          dateFilter: {
            monthStart: this.getDefaultFilterDate(),
            monthEnd: this.getDefaultFilterDate()
          },
          reasons: []
        }),
        queryIsActive: false,
        auth: auth
      }
    },
    created: function () {
      // Удаляем из фильтра параметр date, так как он больше не используется
      if ((this.filters.begin) || (this.filters.end)) {
        delete this.filters.begin
        delete this.filters.end
        this.filters.dateFilter = {
          monthStart: this.getDefaultFilterDate(),
          monthEnd: this.getDefaultFilterDate()
        }
        this.storeValue('filters', this.filters)
      }
      // Убираем фильтр "Все" для записей
      if (this.pagination.rowsPerPage < 0) {
        this.pagination.rowsPerPage = this.rpp[this.rpp.length - 1]
      }
    },
    watch: {
      pagination: {
        handler (newVal) {
          this.storeValue('pagination', newVal)
        },
        deep: true
      },
      filters: {
        handler (newVal) {
          this.storeValue('filters', newVal)
          this.pagination.page = 1
        },
        deep: true
      }
    },
    methods: {
      constructDate (item) {
        if (item.begin === item.end) {
          return moment(item.begin).format('L') + ' (на ' + moment(item.time, 'HH:mm:ss').format('LT') + ' часов)'
        } else {
          const b = moment(item.begin)
          const e = moment(item.end)
          return b.format('L') + ' - ' + e.format('L') + ' (' + (e.diff(b, 'days') + 1) + ' календарных дней)'
        }
      },
      showAbsence (item) {
        if (!item.locked) {
          this.$refs.editDialog.show(item)
        }
      },
      addAbsence (item) {
        this.$apollo.mutate({
          mutation: addAbsence,
          variables: {
            input: item
          }
        }).then(({data}) => {
          this.queryIsActive = false
          if (data.addAbsence.absence) {
            this.$apollo.queries.absencesTable.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Отсутствие успешно добавлено'
            })
          }
        }).catch(e => {
          console.log(e)
          this.queryIsActive = false
        })
      },
      saveAbsence (item) {
        delete item.__typename
        delete item.timeAdded
        delete item.userAdded
        delete item.locked
        this.$apollo.mutate({
          mutation: updateAbsence,
          variables: {
            input: item
          },
          update: (store, {data: {updateAbsence}}) => {
            // Обновляем кеш возвращенными данными
            const query = {
              query: tableQuery,
              variables: {
                input: {
                  first: this.pagination.rowsPerPage,
                  offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
                  desc: this.pagination.descending,
                  search: this.searchText,
                  sortBy: this.pagination.sortBy
                },
                filters: {
                  dateRange: this.filters.dateFilter,
                  reason: this.filters.reasons
                }
              }
            }
            try {
              const data = store.readQuery(query)
              const index = data.absencesTable.absences.findIndex(absence => absence.id === updateAbsence.id)
              data.absencesTable.absences[index] = updateAbsence
              query.data = data
              store.writeQuery(query)
            } catch (e) {
            }
          }
        }).then(({data}) => {
          this.queryIsActive = false
          if (data.updateAbsence.absence) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Отсутствие успешно обновлено'
            })
          }
        })
      },
      removeAbsence (item) {
        this.$apollo.mutate({
          mutation: deleteAbsence,
          variables: {
            input: {
              absenceId: item.id
            }
          }
        }).then(({data}) => {
          this.queryIsActive = false
          if (data.deleteAbsence.success) {
            this.$apollo.queries.absencesTable.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Отсутствие успешно удалено'
            })
          }
        }).catch(e => {
          console.log(e)
          this.queryIsActive = false
        })
      }
    }
  }
</script>
