<template>
  <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition" persistent scrollable :overlay=false>
    <v-btn full-width color="primary" dark slot="activator" @click="openDialog">Создать отчет</v-btn>
    <v-card color="grey lighten-4">
      <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
        <v-btn icon @click.native="closeDialog" dark>
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Создание отчета</v-toolbar-title>
        <v-spacer/>
        <v-toolbar-items>
          <v-btn color="blue darken-1" flat @click.native="createReport" :disabled="!valid || loading"
                 :loading="loading">Создать
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <report-dialog :report-get.sync="report" :valid.sync="valid"/>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
  import ReportDialog from './ReportDialog.vue'
  import {createReport, getReport} from './query'
  import auth from '../../auth/auth'

  export default {
    name: 'CreateReportDialog',
    components: {
      ReportDialog
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        report: {
          worker: null,
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
          distance: null,
          car: 'D',
          gas: 'D',
          whereFrom: null,
          whereTo: null,
          moneySpent: null,
          model: null,
          vcProject: null,
          vcDigits: null,
          vcDigitsMinor: null,
          qualityGrade: null,
          timeGrade: null,
          comment: null,
          tasks: null
        }
      }
    },
    mounted: function () {
      if (this.$route.query.clone === 'true' && this.$route.query.id) {
        this.dialog = true
        this.$apollo.query({
          query: getReport,
          variables: {
            reportId: this.$route.query.id
          }
        }).then(({data, loading}) => {
          if (!loading) {
            this.report = JSON.parse(JSON.stringify(data.getReportData))
            delete this.report.id
            delete this.report.__typename
            delete this.report.checkedBy
            delete this.report.deleted
            delete this.report.timeEdited
            delete this.report.userAdded
            delete this.report.timeChecked
            delete this.report.recordCounted
            this.report.funcRole = data.getReportData.funcRole.id
            this.report.process = data.getReportData.process.id
            this.report.subProcess = data.getReportData.subProcess.id
            this.report.place = data.getReportData.place.id
          }
        })
      }
    },
    methods: {
      openDialog () {
        if (this.$route.query.clone !== 'true') {
          this.report.worker = auth.user.id
        }
      },
      closeDialog () {
        this.dialog = false
        this.$router.push({name: 'reports'})
      },
      createReport () {
        this.loading = true
        this.$apollo.mutate({
          mutation: createReport,
          variables: {
            report: this.report
          }
        }).then(({data}) => {
          this.loading = false
          if (data.createReport.report) {
            this.dialog = false
            this.$emit('created')
            this.$router.push({name: 'reports'})
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
