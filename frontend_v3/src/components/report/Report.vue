<template>
  <v-card color="grey lighten-4">
    <v-tabs fixed centered color="grey lighten-4" v-model="tab">
      <v-tab href="#tab-report">Отчет</v-tab>
      <v-tab href="#tab-logging">История</v-tab>
      <v-tab-item key="1" id="tab-report">
        <v-card-title>
          <v-progress-linear class="pa-0 ma-0" height="4" :indeterminate="true"
                             :active="loadingQueriesCount > 0"/>
          <v-toolbar flat color="grey lighten-4">
            <h5 class="headline ma-0 px-3"
                :class="{ checked: getReport.checkedBy && !getReport.deleted, deleted: getReport.deleted}">
              <v-btn to="/reports" icon title="Назад к личному табелю">
                <v-icon>arrow_back</v-icon>
              </v-btn>
              <report-title :get-report="getReport"/>
            </h5>
            <v-spacer/>
            <update-delete-report-dialog :report-get="getReport" :disabledEndMonth="disabledEndMonth" :valid="valid" :disabled="disabled"
                                         @updated="updated" v-show="loadingQueriesCount === 0">
            </update-delete-report-dialog>
          </v-toolbar>
        </v-card-title>
        <v-card-text v-show="loadingQueriesCount === 0">
          <report-dialog :report-get="getReport" :disabled="disabled" :disabledEndMonth="disabledEndMonth" :valid.sync="valid"/>
        </v-card-text>
      </v-tab-item>
      <v-tab-item key="2" id="tab-logging">
        <logging modelName="reports.Report" :tab="tab" :instanceId="instanceId" defaultTitle="Отчет о работе"/>
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>


<script>
  import ReportDialog from './ReportDialog.vue'
  import {getReport} from './query'
  import UpdateDeleteReportDialog from './UpdateDeleteReport.vue'
  import auth from '../../auth/auth'
  import ReportTitle from './ReportTitle'
  import Logging from '../logging/Logging'

  export default {
    name: 'Report',
    metaInfo: {
      title: 'Отчет о работе'
    },
    components: {
      Logging,
      ReportTitle,
      UpdateDeleteReportDialog,
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
          this.getReport = JSON.parse(JSON.stringify(data.getReportData))
          this.getReport.worker = data.getReportData.worker.id
          this.getReport.funcRole = data.getReportData.funcRole.id
          if (data.getReportData.process) {
            this.getReport.process = data.getReportData.process.id
            this.getReport.subProcess = data.getReportData.subProcess.id
          }
          this.getReport.place = data.getReportData.place.id
          if (data.getReportData.checkedBy || data.getReportData.deleted ||
            data.getReportData.userAdded.id !== this.auth.user.id) {
            this.disabled = true
          }
          if (data.getReportData.projects[0].gip.id === this.auth.user.id && data.getReportData.recordCounted < 1) {
            this.disabled = false
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
        getReport: {
          worker: null,
          reportDate: null,
          funcRole: null,
          timeEdited: null,
          userAdded: null,
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
          comment: null,
          tasks: null
        },
        disabled: false,
        disabledEndMonth: false,
        loadingQueriesCount: 0,
        auth: auth,
        tab: null,
        instanceId: this.$route.params.id
      }
    }
  }
</script>
