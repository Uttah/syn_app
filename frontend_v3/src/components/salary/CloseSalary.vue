<template>
    <v-dialog v-if="disabled" v-model="dialogClose" persistent max-width="500px">
      <v-btn color="primary" slot="activator">Закрыть месяц</v-btn>
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите закрыть заплату за
          <span class="red--text"><b>{{ formatMonth(lastSalaryMonth).toUpperCase() }}</b></span>?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="dialogClose = false" v-show="!loading">Отмена</v-btn>
          <v-btn flat @click.native="closeSalary" :disabled="loading" :loading="loading">Подтвердить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>


<script>
  import {closeSalary, lastSalaryMonth} from './query'
  import utilsMixin from '../utils'

  export default {
    name: 'CloseSalary',
    props: {
      date: String,
      disabled: Boolean
    },
    apollo: {
      lastSalaryMonth: {
        query: lastSalaryMonth,
        fetchPolicy: 'network-only',
        update (data) {
          return this.getDateByMnth(this.getIdFromMnth(data.lastSalaryMonth))
        }
      }
    },
    mixins: [utilsMixin],
    data () {
      return {
        lastSalaryMonth: null,
        dialogClose: false,
        nowDate: new Date(),
        month: new Date(),
        loading: false
      }
    },
    methods: {
      closeSalary () {
        this.loading = true
        this.$apollo.mutate({
          mutation: closeSalary
        }).then(({data}) => {
          this.loading = false
          if (data.closeSalary.result) {
            this.dialogClose = false
            this.$emit('monthClosed')
          }
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      dialogClose (val) {
        if (val) {
          this.$apollo.queries.lastSalaryMonth.refetch()
        }
      }
    }
  }
</script>
