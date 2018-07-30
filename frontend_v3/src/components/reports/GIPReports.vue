<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Проверка отчетов</span>
        <v-spacer/>
        <v-checkbox v-model="reportFilter.onlyOwnProjects" label="Только свои проекты" hide-details class="pt-4" style="max-width: 220px"/>
        <header-filter class="pr-4 pt-3" @clearFilters="clearFilters" style="align-self: end;">
          <v-layout row wrap justify-center class="pb-4 pt-3">
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-months-picker v-model="reportFilter.dateRange" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Исполнитель" v-model="reportFilter.worker" clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <projects-select v-model="reportFilter.projects" label="Номер проекта" multiple hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select :items="allStatesData" item-text="name" item-value="id" label="Этап" clearable
                        v-model="reportFilter.state" autocomplete hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select :items="allFuncRolesData" item-text="name" item-value="id" label="Функциональная роль"
                        clearable v-model="reportFilter.funcRole" autocomplete hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select :items="allProcessesData" item-text="name" item-value="id" label="Процесс" clearable
                        v-model="reportFilter.process" @input="loadSubProcesses(reportFilter.process, false)" autocomplete hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select :items="allSubProcessesData" item-text="name" item-value="id" label="Подпроцесс"
                        clearable v-model="reportFilter.subProcess" autocomplete hide-details/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field
          label="Поиск по тексту задач"
          append-icon="search"
          hide-details
          v-model="searchQuery"
          style="max-width: 350px;"
        />
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
        <tr :class="{
              checked: props.item.checkedBy && !props.item.deleted && props.item.recordCounted < 2,
              deleted: props.item.deleted,
              locked: props.item.recordCounted === 2 && !props.item.deleted
            }"
            @mouseover="selId = props.item.id" @mouseout="selId = 0"
            @click.stop="showReport(props.item.id, $event)">
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
          </td>
          <td>{{props.item.projects[0].gip.shortName }}
            <v-btn v-if="props.item.comment" icon @click.native.stop="openDialogComment(props.item.comment)"
                   class="ma-0">
              <v-icon>comment</v-icon>
            </v-btn>
            <v-btn icon class="check-button-hidden ma-0"
                   v-if="props.item.recordCounted < 2 && !props.item.deleted && canManageReport(props.item)"
                   @click.stop="openQualityDialog($event, props.item)"
                   :title="props.item.checkedBy ? 'Оценить отчет' : 'Проверить отчет'">
              <v-icon>done</v-icon>
            </v-btn>
            <div>{{ props.item.qualityGrade ? props.item.qualityGrade + '/' + props.item.timeGrade : ''}}</div>
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
    <v-menu top offset-y absolute :close-on-click="false" :close-on-content-click="false" :position-x="qualityDialogX"
            :position-y="qualityDialogY" v-model="qualityDialog">
      <v-card style="min-width: 800px">
        <v-card-title>
          <span class="title">{{ qualityMenu.checkedBy ? 'Оценка' : 'Оценка и подтверждение' }}</span>
        </v-card-title>
        <v-card-text class="py-0">
          <v-form ref="qualityForm" v-model="validQualityForm">
            <v-container class="pa-0">
              <v-layout wrap justify-center>
                <v-flex xs6 class="pr-3" v-if="qualityMenu.worker !== auth.user.id">
                  <v-select label="Оценка качества" v-model="report.qualityGrade" :rules="qualityValid"
                            @input="$refs.qualityForm.validate()" :items="qualityGrades" clearable/>
                </v-flex>
                <v-flex xs6 class="pl-3" v-if="qualityMenu.worker !== auth.user.id">
                  <v-select label="Оценка срока" v-model="report.timeGrade" :rules="qualityValid"
                            @input="$refs.qualityForm.validate()" :items="timeGrades" clearable/>
                </v-flex>
                <v-flex xs12>
                  <v-text-field label="Комментарий" multiLine v-model="report.comment"
                                :rules="commentValid"/>
                </v-flex>
              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="qualityDialog = false">Отмена</v-btn>
          <v-btn flat :disabled="!validQualityForm" @click.native="updateConfirm">
            {{ qualityMenu.checkedBy ? 'Сохранить' : 'Подтвердить и сохранить' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
  </v-card>
</template>

<script>
  import {tableQuery, updateConfirmReport, allForFill} from './query'
  import _ from 'lodash'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import bus from '../../../src/bus.js'
  import MonthsFilter from '../MonthsFilter.vue'
  import WorkersSelect from '../WorkersSelect.vue'
  import ProjectsSelect from '../ProjectsSelect.vue'
  import IntegerField from '../IntegerField'
  import TwoMonthsPicker from '../TwoMonthsPicker'
  import HeaderFilter from '../HeaderFilter'

  export default {
    components: {
      IntegerField,
      MonthsFilter,
      WorkersSelect,
      ProjectsSelect,
      TwoMonthsPicker,
      HeaderFilter
    },
    name: 'GIPReports',
    metaInfo: {
      title: 'Проверка отчетов'
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
            filters: this.reportFilter,
            gip: true
          }
        },
        loadingKey: 'loadingQueriesCount'
      },
      query: {
        query: allForFill,
        update (data) {
          this.allStatesData = data.allStates
          this.allFuncRolesData = data.allFuncRoles
          this.allProcessesData = data.allProcesses
          if (this.reportFilter.process) {
            this.loadSubProcesses(this.reportFilter.process, true)
          }
        }
      }
    },
    data () {
      return {
        reportTableItems: [],
        headers: [
          {text: 'Исполнитель', align: 'left', value: 'worker'},
          {text: 'Дата', align: 'left', value: 'reportDate'},
          {text: '№ проекта', align: 'left', value: 'projectNum'},
          {text: 'Задача', align: 'left', value: 'task', sortable: false, width: '50%'},
          {text: 'Время/Место', align: 'left', value: 'time', sortable: false},
          {text: 'ГИП/Оценка', align: 'left', value: 'gip', sortable: false, width: '250px'}
        ],
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'reportDate'
        }),
        searchText: this.getValue('searchGIPReports', ''),
        searchQuery: this.getValue('searchGIPReports', ''),
        loadingQueriesCount: 0,
        allStatesData: [],
        allFuncRolesData: [],
        allProcessesData: [],
        allSubProcessesData: [],
        reportFilter: this.getValue('filters', {
          onlyOwnProjects: true,
          dateRange: {
            monthStart: this.getDefaultFilterDate(),
            monthEnd: this.getDefaultFilterDate()
          },
          worker: null,
          projects: null,
          state: null,
          funcRole: null,
          process: null,
          subProcess: null
        }),
        selId: 0,
        qualityDialog: false,
        qualityDialogX: 0,
        qualityDialogY: 0,
        validQualityForm: false,
        report: {},
        qualityValid: [
          text => {
            if ((this.checkGrade(this.report.qualityGrade) && !this.checkGrade(this.report.timeGrade)) ||
              (!this.checkGrade(this.report.qualityGrade) && this.checkGrade(this.report.timeGrade))) {
              return 'Для начисления коэффициента нужны обе оценки'
            }
            return true
          }
        ],
        commentValid: [
          text => {
            if (this.checkGrade(this.report.qualityGrade) &&
              this.checkGrade(this.report.timeGrade) && !this.report.comment) {
              return 'Поле не может быть пустым'
            }
            return true
          }
        ],
        comment: '',
        dialogComment: false,
        qualityGrades: [
          {text: '2 - неудовлетворительно (требуется переделка)', value: 2},
          {text: '3 - удовлетворительно (нет времени или возможности переделать)', value: 3},
          {text: '4 - хорошо (работа сделана приемлемо)', value: 4},
          {text: '5 - отлично (выше ожиданий)', value: 5}
        ],
        timeGrades: [
          {text: '0 - срока не было', value: 0},
          {text: '2 - не выполнено, либо срок провален', value: 2},
          {text: '3 - не успел по объективным причинам (либо были переделки)', value: 3},
          {text: '4 - успел в срок, без переделок', value: 4},
          {text: '5 - успел с опережением, без переделок', value: 5}
        ],
        auth: auth,
        qualityMenu: {
          worker: auth.user.id,
          checkedBy: null
        }
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
      let handler2 = () => {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Отчет подтвержден'
        })
      }
      let handler3 = () => {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Отчет восстановлен'
        })
      }
      bus.$once('deleted', handler)
      bus.$once('confirm', handler2)
      bus.$once('restore', handler3)
    },
    watch: {
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchGIPReports', val)
        }
      },
      reportFilter: {
        handler: function (val) {
          this.storeValue('filters', val)
          this.pagination.page = 1
          this.$apollo.queries.reportTableItems.refetch()
        },
        deep: true
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      qualityDialog (val) {
        if (val) {
          const result = this.reportTableItems.reports.find(report => report.id === this.selId)
          if (result) {
            this.qualityMenu = {
              worker: result.worker ? result.worker.id : null,
              checkedBy: result.checkedBy ? result.checkedBy.id : null
            }
          }
        }
      }
    },
    methods: {
      checkGrade (grade) {
        if (grade === null) {
          return false
        } else {
          const int = parseInt(grade)
          return !isNaN(int) && int >= 0 && int <= 5
        }
      },
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
            name: 'manage_report',
            params: {id: id}
          })
        }
      },
      openQualityDialog (e, item) {
        e.preventDefault()
        // Вместо копирования отдельных полей надо пересылать весь отчет для обновления
        this.report = JSON.parse(JSON.stringify(item))
        delete this.report.__typename
        delete this.report.deleted
        delete this.report.recordCounted
        this.report.worker = item.worker.id
        this.report.funcRole = item.funcRole.id
        this.report.projects = item.projects.map(item => item.id)
        this.report.place = item.place.id
        this.report.process = item.process ? item.process.id : null
        this.report.subProcess = item.subProcess ? item.subProcess.id : null
        // Если Нет работы, то проверяем без окна
        if (item.place.kind === 'N') {
          this.updateConfirm(null, true)
          return
        }

        // Если жмем на проверку своего собственного отчета, то проверяем без окна
        if (item.worker.id === this.auth.user.id && !item.checkedBy) {
          this.updateConfirm(null, true)
          return
        }

        this.qualityDialogX = e.clientX - 300
        this.qualityDialogY = e.clientY
        this.$refs.qualityForm.validate()
        this.qualityDialog = true
      },
      updateConfirm (event, skipUpdate) {
        skipUpdate = !!skipUpdate
        const doConfirm = this.report.checkedBy === null
        delete this.report.checkedBy
        this.$apollo.mutate({
          mutation: updateConfirmReport,
          variables: {
            doConfirm: doConfirm,
            skipUpdate: skipUpdate,
            report: this.report,
            report2: {
              id: this.report.id
            }
          },
          update: (store, {data}) => {
            const updatedReport = skipUpdate ? data.confirmReport : data.updateReport
            if (updatedReport) {
              // Обновляем кеш возвращенными данными
              const query = {
                query: tableQuery,
                variables: {
                  paged: {
                    first: this.pagination.rowsPerPage,
                    offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
                    desc: this.pagination.descending,
                    search: this.searchText,
                    sortBy: this.pagination.sortBy
                  },
                  filters: this.reportFilter,
                  gip: true
                }
              }
              try {
                const data = store.readQuery(query)
                const index = data.reportTableItems.reports.findIndex(report => report.id === updatedReport.id)
                for (let key of updatedReport) {
                  if (updatedReport.hasOwnProperty(key)) {
                    data.reportTableItems.reports[index][key] = updatedReport[key]
                  }
                }
                query.data = data
                store.writeQuery(query)
              } catch (e) {
              }
            }
          }
        }).then(({data}) => {
          if (data.updateReport || data.confirmReport) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: doConfirm ? 'Отчет оценен и подтвержден' : 'Оценки обновлены'
            })
            this.qualityDialog = false
          }
        })
      },
      loadSubProcesses (val, processSwitch) {
        const res = this.allProcessesData.find(item => item.id === val)
        this.allSubProcessesData = res ? res.subprocessSet : []
        if (!processSwitch) {
          this.reportFilter.subProcess = null
        }
      },
      canManageReport (report) {
        if (report.projects[0].gip.id === this.auth.user.id || this.auth.hasPermission('reports.global_manage')) {
          if (report.worker.id !== this.auth.user.id) {
            return true
          } else {
            return !report.checkedBy
          }
        } else {
          return false
        }
      },
      clearFilters () {
        this.reportFilter = {
          onlyOwnProjects: true,
          dateRange: {
            monthStart: null,
            monthEnd: null
          },
          worker: null,
          projects: [],
          state: null,
          funcRole: null,
          process: null,
          subProcess: null
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

  tr:hover .check-button-hidden {
    visibility: visible;
  }

  tr .check-button-hidden {
    visibility: hidden;
  }
</style>
