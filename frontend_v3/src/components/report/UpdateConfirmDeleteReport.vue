<template>
  <div>
    <v-dialog :disabled="showRestoreBtn || !valid" v-model="dialogUpdate" persistent max-width="500px">
      <v-btn :disabled="showRestoreBtn || !valid" color="primary" slot="activator">Сохранить</v-btn>
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите сохранить отчет?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogUpdate = false" :disabled="loading">Отмена</v-btn>
          <v-btn flat @click.native="updateReport" :disabled="loading" :loading="loading">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogDelete" persistent max-width="500px">
      <v-btn v-show="!showRestoreBtn" color="red" slot="activator">Удалить</v-btn>
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите удалить отчет?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogDelete = false" :disabled="loading">Отмена</v-btn>
          <v-btn flat @click.native="deleteReport" :disabled="loading" :loading="loading">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogRestore" persistent max-width="500px">
      <v-btn v-show="showRestoreBtn" color="primary" slot="activator">Восстановить</v-btn>
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите восстановить отчет?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogRestore = false" :disabled="loading">Отмена</v-btn>
          <v-btn flat @click.native="restoreReport" :disabled="loading" :loading="loading">Восстановить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog :disabled="showRestoreBtn || disabledConfirm || !valid" v-model="dialogConfirm" persistent
              max-width="500px">
      <v-btn :disabled="showRestoreBtn || disabledConfirm || !valid" color="primary" slot="activator">Подтвердить
      </v-btn>
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите подтвердить отчет?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogConfirm = false" :disabled="loading">Отмена</v-btn>
          <v-btn flat @click.native="confirmReport" :disabled="loading" :loading="loading">Подтвердить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>


<script>
  import {updateReport, deleteReport, confirmReport, restoreReport} from './query'
  import bus from '../../../src/bus.js'

  export default {
    name: 'UpdateConfirmDeleteReportDialog',
    props: [
      'reportGet',
      'showRestoreBtn',
      'disabledConfirm',
      'valid'
    ],
    data () {
      return {
        dialogUpdate: false,
        dialogDelete: false,
        dialogConfirm: false,
        dialogRestore: false,
        loading: false
      }
    },
    methods: {
      updateReport () {
        this.loading = true
        const report = Object.assign({}, this.reportGet)
        delete report.__typename
        delete report.checkedBy
        delete report.timeChecked
        delete report.userAdded
        delete report.timeEdited
        delete report.deleted
        delete report.recordCounted
        this.$apollo.mutate({
          mutation: updateReport,
          variables: {
            report: report
          }
        }).then(({data}) => {
          this.loading = false
          if (data.updateReport.report) {
            this.dialogUpdate = false
            this.$emit('updated')
          }
        }).catch(() => {
          this.loading = false
        })
      },
      deleteReport () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deleteReport,
          variables: {
            report: {
              id: this.reportGet.id,
              deleted: true
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.deleteReport.result === true) {
            this.dialogDelete = false
            this.$router.push({name: 'manage_reports'})
            setTimeout(() => bus.$emit('deleted'), 50)
          }
        }).catch(() => {
          this.loading = false
        })
      },
      confirmReport () {
        this.loading = true
        this.$apollo.mutate({
          mutation: confirmReport,
          variables: {
            report: {
              id: this.reportGet.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.confirmReport.report) {
            this.dialogConfirm = false
            this.$router.push({name: 'manage_reports'})
            setTimeout(() => bus.$emit('confirm'), 50)
          }
        }).catch(() => {
          this.loading = false
        })
      },
      restoreReport () {
        this.loading = true
        this.$apollo.mutate({
          mutation: restoreReport,
          variables: {
            report: {
              id: this.reportGet.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.restoreReport.result === true) {
            this.dialogRestore = false
            this.$router.push({name: 'manage_reports'})
            setTimeout(() => bus.$emit('restore'), 50)
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
