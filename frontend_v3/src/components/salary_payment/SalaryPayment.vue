<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Выплата по компаниям</span>
        <v-spacer/>

        <v-dialog v-model="confirmUpdateDialog" persistent scrollable lazy max-width="700px">
          <v-card>
            <v-card-title>
              <span class="subheading">
                Вы действительно хотите обновить запись?
              </span>
            </v-card-title>
            <v-card-actions>
              <v-spacer/>
              <v-btn flat @click.native="confirmUpdateDialog = false">Отмена</v-btn>
              <v-btn flat :loading="loading"  @click.native="updateSalaryPaymentFunc">Обновить</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="confirmDeleteDialog" persistent scrollable lazy max-width="700px">
          <v-card>
            <v-card-title>
              <span class="subheading">
                Вы действительно хотите удалить запись?
              </span>
            </v-card-title>
            <v-card-actions>
              <v-spacer/>
              <v-btn flat @click.native="confirmDeleteDialog = false">Отмена</v-btn>
              <v-btn flat :loading="loading"  @click.native="deleteSalaryPaymentFunc">Удалить</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="salaryPaymentDialog" persistent max-width="500">
          <v-btn v-if="auth.hasPermission('salary.add_salarypayment')" color="primary" dark slot="activator"
                 @click="create">Создать запись
          </v-btn>
          <v-card>
            <v-card-title v-if="!updateDelete" class="headline">Создание записи</v-card-title>
            <v-card-title v-if="updateDelete" class="headline">Обновление/Удаление записи</v-card-title>
            <v-form v-model="valid">
              <v-container>
                <v-layout wrap justify-center>
                  <v-flex xs12>
                    <workers-select label="Сотрудник" required v-model="salaryPayment.userId"/>
                  </v-flex>
                  <v-flex xs12>
                    <integer-field label="Сумма выплаты" required suffix="руб."
                                   v-model="salaryPayment.amount" :rules="amountFieldRules"/>
                  </v-flex>
                  <v-flex xs12>
                    <integer-field label="Аванс" required suffix="руб."
                                   v-model="salaryPayment.advance" :rules="advanceFieldRules"/>
                  </v-flex>
                  <v-flex xs12>
                    <v-select
                      label="Компания"
                      required
                      :items="allCompaniesData"
                      item-text="name"
                      item-value="id"
                      v-model="salaryPayment.companyId"
                      :rules="nonEmptyField"
                    >
                    </v-select>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-form>
            <v-card-actions>
              <v-spacer/>
              <v-btn flat @click.native="salaryPaymentDialog = false">Отмена</v-btn>
              <v-btn v-if="updateDelete" flat :disabled="!auth.hasPermission('salary.delete_salarypayment')"
                     @click.native="confirmDeleteDialog = true">Удалить
              </v-btn>
              <v-btn v-if="updateDelete" flat :disabled="!valid || !auth.hasPermission('salary.change_salarypayment')"
                     @click.native="confirmUpdateDialog = true">Обновить
              </v-btn>
              <v-btn v-if="!updateDelete" flat :disabled="!valid" @click.native="createSalaryPaymentFunc">Создать
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="salaryPaymentData.salaryPayments"
      :total-items="salaryPaymentData.totalCount"
      :pagination.sync="pagination"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
      must-sort
      style="max-width: 1000px"
      class="mx-auto"
    >
      <template slot="items" slot-scope="props">
        <tr @click="update(props.item)">
          <td class="text-xs-center">{{ props.item.user.shortName }}</td>
          <td class="text-xs-center">{{ props.item.amount.toLocaleString() }} &#8381;</td>
          <td class="text-xs-center">{{ props.item.advance.toLocaleString() }} &#8381;</td>
          <td class="text-xs-center">{{ props.item.company.client.name }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {pagedSalaryPayments, createSalaryPayment, updateSalaryPayment, deleteSalaryPayment} from './query'
  import {allCompanies} from '../financial_info/query'
  import utilMixin from '../utils'
  import WorkersSelect from '../WorkersSelect'
  import IntegerField from '../IntegerField'
  import auth from '../../auth/auth'

  export default {
    components: {
      IntegerField,
      WorkersSelect
    },
    name: 'salary-payment',
    metaInfo: {
      title: 'Выплата по компаниям'
    },
    mixins: [utilMixin],
    apollo: {
      pagedSalaryPaymentsQuery: {
        fetchPolicy: 'cache-and-network',
        query: pagedSalaryPayments,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              search: this.searchText,
              sortBy: this.pagination.sortBy
            }
          }
        },
        update (data) {
          this.salaryPaymentData = data.pagedSalaryPayments
        },
        loadingKey: 'loadingQueriesCount'
      },
      allCompaniesQuery: {
        fetchPolicy: 'cache-and-network',
        query: allCompanies,
        update (data) {
          data.companies.forEach(company => {
            this.allCompaniesData.push({
              id: company.client.id,
              name: company.client.name
            })
          })
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        auth: auth,
        valid: false,
        confirmUpdateDialog: false,
        confirmDeleteDialog: false,
        salaryPaymentDialog: false,
        salaryPaymentData: [],
        allCompaniesData: [],
        updateDelete: false, // Скрывает кнопки в диалоге
        headers: [
          {text: 'Сотрудник', align: 'center', value: 'user'},
          {text: 'Сумма выплаты', align: 'center', value: 'amount'},
          {text: 'Аванс', align: 'center', value: 'advance'},
          {text: 'Компания', align: 'center', value: 'company'}
        ],
        rpp: [
          25, 50, {text: 'Все', value: -1}
        ],
        loadingQueriesCount: 0,
        loading: false,
        salaryPayment: {
          userId: null,
          amount: null,
          advance: null,
          companyId: null
        },
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'user'
        }),
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        amountFieldRules: [
          text => Number(text) > 0 || 'Сумма должна быть больше нуля'
        ],
        advanceFieldRules: [
          text => Number(text) > 0 || 'Аванс должен быть больше нуля'
        ]
      }
    },
    watch: {
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      }
    },
    methods: {
      create () {
        this.updateDelete = false
        this.salaryPayment = {
          userId: null,
          amount: null,
          advance: null,
          companyId: null
        }
      },
      update (item) {
        this.updateDelete = true
        this.salaryPayment = {
          id: item.id,
          userId: item.user.id,
          amount: item.amount,
          advance: item.advance,
          companyId: item.company.id
        }
        this.salaryPaymentDialog = true
      },
      createSalaryPaymentFunc () {
        this.loading = true
        this.$apollo.mutate({
          mutation: createSalaryPayment,
          variables: {
            input: this.salaryPayment
          }
        }).then(({data}) => {
          this.loading = false
          if (data.createSalaryPayment.result) {
            this.salaryPaymentDialog = false
            this.$apollo.queries.pagedSalaryPaymentsQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Запись создана'
            })
          }
        }).catch(() => {
          this.loading = false
        })
      },
      updateSalaryPaymentFunc () {
        this.loading = true
        this.$apollo.mutate({
          mutation: updateSalaryPayment,
          variables: {
            input: this.salaryPayment
          }
        }).then(({data}) => {
          this.loading = false
          if (data.updateSalaryPayment.result) {
            this.confirmUpdateDialog = false
            this.salaryPaymentDialog = false
            this.$apollo.queries.pagedSalaryPaymentsQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Запись обновлена'
            })
          }
        }).catch(() => {
          this.loading = false
        })
      },
      deleteSalaryPaymentFunc () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deleteSalaryPayment,
          variables: {
            input: {
              id: this.salaryPayment.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.deleteSalaryPayment.result) {
            this.confirmDeleteDialog = false
            this.salaryPaymentDialog = false
            this.$apollo.queries.pagedSalaryPaymentsQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Запись удалена'
            })
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
