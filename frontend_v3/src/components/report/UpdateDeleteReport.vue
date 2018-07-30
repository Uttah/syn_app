<template>
  <div>
    <v-dialog :disabled="!valid || (disabled && disabledEndMonth)" v-model="dialogUpdate" persistent max-width="500px">
      <v-btn color="primary" :disabled="(!valid || disabled) && disabledEndMonth" slot="activator">Сохранить</v-btn>
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
    <v-dialog :disabled="disabled" v-model="dialogDelete" persistent max-width="500px">
      <v-btn color="red" slot="activator" :disabled="disabled">Удалить</v-btn>
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
    <v-btn color="primary" @click="cloneReport" title="Создать отчет, похожий на этот" :disabled="loading">Дублировать
    </v-btn>
  </div>
</template>


<script>
  import {updateReport, deleteReport} from './query'
  import bus from '../../../src/bus.js'

  export default {
    name: 'UpdateDeleteReportDialog',
    props: [
      'reportGet',
      'valid',
      'disabled',
      'disabledEndMonth'
    ],
    data () {
      return {
        dialogUpdate: false,
        dialogDelete: false,
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
              id: this.reportGet.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.deleteReport.result === true) {
            this.dialogDelete = false
            this.$router.push({name: 'reports'})
            setTimeout(() => bus.$emit('deleted'), 50)
          }
        }).catch(() => {
          this.loading = false
        })
      },
      cloneReport () {
        this.$router.push({name: 'reports', query: {clone: 'true', id: this.reportGet.id}})
      }
    }
  }
</script>
