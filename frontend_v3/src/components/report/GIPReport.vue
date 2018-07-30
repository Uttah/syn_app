<template>
  <v-card color="grey lighten-4">
    <v-card-title>
      <v-progress-linear class="pa-0 ma-0" height="4" :indeterminate="true"
                         :active="loadingQueriesCount > 0"/>
      <v-toolbar flat color="grey lighten-4">
        <h5 class="headline ma-0 px-3"
            :class="{ checked: getReport.checkedBy && !getReport.deleted, deleted: getReport.deleted}">
          <v-btn to="/manage_reports" icon title="Назад к проверке отчетов">
            <v-icon>arrow_back</v-icon>
          </v-btn>
          <report-title :get-report="getReport"/>
        </h5>
        <v-spacer/>
        <update-confirm-delete-report-dialog v-if="!disableEdit" v-show="loadingQueriesCount === 0"
                                             :report-get="getReport" :showRestoreBtn="showRestoreBtn"
                                             :disabledConfirm="disabledConfirm" @updated="updated" :valid="valid">
        </update-confirm-delete-report-dialog>
      </v-toolbar>
    </v-card-title>
    <v-card-text v-show="loadingQueriesCount === 0">
      <report-dialog :report-get="getReport" :gip-id="gipId" :valid.sync="valid" :disabled="disabled" :disabledEndMonth="disabledEndMonth"
                     :disabled-quality="disabledQuality"/>
    </v-card-text>
  </v-card>
</template>


<script>
  import ReportDialog from './ReportDialog.vue'
  import {getReport} from './query'
  import UpdateConfirmDeleteReportDialog from './UpdateConfirmDeleteReport.vue'
  import ReportTitle from './ReportTitle'
  import auth from '../../auth/auth'

  export default {
    name: 'Report',
    metaInfo: {
      title: 'Отчет о работе'
    },
    components: {
      ReportTitle,
      UpdateConfirmDeleteReportDialog,
      ReportDialog
    },
    apollo: {
      getReportData: {
        fetchPolicy: 'cache-and-network',
        query: getReport,
        variables () {
          return {
            reportId: this.$route.params.id
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.gipId = data.getReportData.projects[0].gip.id
          this.getReport = JSON.parse(JSON.stringify(data.getReportData))
          this.getReport.worker = data.getReportData.worker.id
          this.getReport.funcRole = data.getReportData.funcRole.id
          if (data.getReportData.process) {
            this.getReport.process = data.getReportData.process.id
            this.getReport.subProcess = data.getReportData.subProcess.id
          }
          this.getReport.place = data.getReportData.place.id
          if (data.getReportData.deleted) {
            this.showRestoreBtn = true
          }
          if (data.getReportData.checkedBy) {
            this.disabledConfirm = true
          }
          this.disableEdit = this.gipId !== this.auth.user.id && !this.auth.hasPermission('reports.global_manage')
          switch (data.getReportData.recordCounted) {
            case 0: {
              this.disabled = this.disableEdit
              this.disabledQuality = this.disableEdit
              break
            }
            case 1: {
              this.disabled = true
              this.disabledQuality = this.disableEdit
              break
            }
            case 2: {
              this.disabled = true
              this.disabledQuality = true
              break
            }
          }
          // Нет прав
          this.disabledEndMonth = !this.auth.hasPermission('reports.change_fields_after_month')
        }
      }
    },
    methods: {
      updated () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Отчет обновлен'
        })
      }
    },
    data () {
      return {
        dialog: false,
        valid: false,
        gipId: null,
        getReport: {
          worker: null,
          timeEdited: null,
          userAdded: null,
          reportDate: null,
          funcRole: null,
          projects: [],
          process: null,
          subProcess: null,
          task: null,
          timeSpent: null,
          timeTo: null,
          timeFrom: null,
          place: null,
          distance: 0,
          car: 'D',
          gas: 'D',
          whereFrom: null,
          whereTo: null,
          moneySpent: 0,
          model: null,
          nightShift: false,
          vcProject: null,
          vcDigits: null,
          vcDigitsMinor: null,
          qualityGrade: null,
          timeGrade: null,
          comment: null
        },
        showRestoreBtn: false,
        disabledConfirm: false,
        loadingQueriesCount: 0,
        disabled: false,
        disabledQuality: false,
        disableEdit: false,
        auth: auth,
        disabledEndMonth: false
      }
    }
  }
</script>
