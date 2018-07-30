<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Личный табель</span>
        <v-spacer/>
        <header-filter class="pt-4" @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="pb-4">
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-months-picker v-model="reportFilter.dateRange" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Исполнитель" v-model="reportFilter.worker" clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <projects-select v-model="reportFilter.projects" label="Номер проекта" multiple hide-details/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field class="pr-3"
                      label="Поиск по тексту задач"
                      append-icon="search"
                      hide-details
                      v-model="searchQuery"
                      style="max-width: 350px;"/>
        <create-report-dialog @created="created"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="reportTableItems.reports"
      :total-items="reportTableItems.totalCount"
      :pagination.sync="pagination"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr :class="{locked: props.item.checkedBy, deleted: props.item.deleted} "
            @click="showReport(props.item.id, $event)">
          <td>{{ props.item.worker.shortName }}
            <div>{{ props.item.funcRole.name }}</div>
          </td>
          <td>{{ formatDate(props.item.reportDate) }}</td>
          <td>
            <span v-for="(project, index) in props.item.projects" :title="project.description">
              {{ String(formatProject(project.number)) + ((index < props.item.projects.length - 1) ? ', ' : '') }}</span>
          </td>
          <td style="width: 450px; max-width: 450px; word-wrap: break-word;">
            <div v-if="props.item.process">{{ props.item.process.name }} / {{ props.item.subProcess.name }}</div>
            <div v-html="formatTask(props.item)"></div>
          </td>
          <td>{{ props.item.timeSpent.slice(0, 5) }}
            <v-icon class="pl-2" v-if="props.item.nightShift" title="Ночная смена">mdi-weather-night</v-icon>
            <div>{{ props.item.place.name}}</div>
            <div v-if="props.item.moneySpent > 0">(Проезд: {{ props.item.moneySpent }} &#8381;)</div>
          </td>
          <td>{{props.item.projects[0].gip.shortName }}
            <div>{{ props.item.qualityGrade ? props.item.qualityGrade + '/' + props.item.timeGrade : ''}}
              <v-btn v-if="props.item.comment" icon @click.native.stop="openDialogComment(props.item.comment)">
                <v-icon>comment</v-icon>
              </v-btn>
            </div>
          </td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <v-dialog v-model="dialogComment" persistent max-width="290">
      <v-card>
        <v-card-title class="headline">Комментарий</v-card-title>
        <v-card-text>{{ comment }}</v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="green darken-1" flat @click.native="dialogComment = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
  import {tableQuery} from './query'
  import CreateReportDialog from '../report/CreateReport.vue'
  import _ from 'lodash'
  import utilMixin from '../utils'
  import bus from '../../../src/bus.js'
  import WorkersSelect from '../WorkersSelect.vue'
  import ProjectsSelect from '../ProjectsSelect.vue'
  import TwoMonthsPicker from '../TwoMonthsPicker.vue'
  import HeaderFilter from '../HeaderFilter'

  export default {
    components: {
      CreateReportDialog,
      WorkersSelect,
      ProjectsSelect,
      TwoMonthsPicker,
      HeaderFilter
    },
    name: 'Reports',
    metaInfo: {
      title: 'Личный табель'
    },
    mixins: [utilMixin],
    apollo: {
      reportTableItems: {
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
            filters: this.reportFilter
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        dialogComment: false,
        comment: '',
        reportTableItems: [],
        headers: [
          {text: 'Исполнитель', align: 'left', value: 'worker'},
          {text: 'Дата', align: 'left', value: 'reportDate'},
          {text: '№ проекта', align: 'left', value: 'projectNum'},
          {text: 'Задача', align: 'left', value: 'task', sortable: false, width: '50%'},
          {text: 'Время/Место', align: 'left', value: 'time', sortable: false},
          {text: 'ГИП/Оценка', align: 'left', value: 'gip', sortable: false, width: '150px'}
        ],
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'reportDate'
        }),
        searchText: this.getValue('searchReports', ''),
        searchQuery: this.getValue('searchReports', ''),
        loadingQueriesCount: 0,
        reportFilter: this.getValue('filters', {
          worker: null,
          projects: null,
          dateRange: {
            monthStart: this.getDefaultFilterDate(),
            monthEnd: this.getDefaultFilterDate()
          }
        })
      }
    },
    created: function () {
      // Удаляем из фильтра параметр date, так как он больше не используется
      if (this.reportFilter.date) {
        delete this.reportFilter.date
        this.reportFilter.dateRange = {
          monthStart: this.getDefaultFilterDate(),
          monthEnd: this.getDefaultFilterDate()
        }
        this.storeValue('filters', this.reportFilter)
      }
      // Убираем фильтр "Все" для записей
      if (this.pagination.rowsPerPage < 0) {
        this.pagination.rowsPerPage = this.rpp[this.rpp.length - 1]
      }
      let handler = () => {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Отчет удален'
        })
      }
      bus.$once('deleted', handler)
    },
    watch: {
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchReports', val)
        }
      },
      reportFilter: {
        handler: function (val) {
          this.$apollo.queries.reportTableItems.refetch()
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
    },
    methods: {
      openDialogComment (comment) {
        this.comment = comment
        this.dialogComment = true
      },
      created () {
        this.$apollo.queries.reportTableItems.refetch()
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Отчет создан'
        })
      },
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      showReport (id, event) {
        if (event.target.tagName !== 'A') {
          this.$router.push({
            name: 'report',
            params: {id: id}
          })
        }
      },
      clearFilters () {
        this.reportFilter = {
          worker: null,
          projects: [],
          dateRange: {
            monthStart: null,
            monthEnd: null
          }
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'reportDate'
        }
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
