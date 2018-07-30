<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Расчет заработной платы</span>
        <v-spacer/>
        <v-layout justify-center style="align-items: end; flex: 1" class="px-0">
          <v-flex xs4 class="pr-2">
            <v-select
              label="Компания"
              :items="allCompaniesData"
              item-text="name"
              item-value="id"
              v-model="company"
              clearable
              hide-details
            />
          </v-flex>
          <v-flex xs4 class="pl-2">
            <months-filter v-model="date"
                           hide-details
                           salary-months
                           ref="salaryMonthFilter"
                           :is-loading.sync="monthsLoading"/>
          </v-flex>
          <close-salary class="pl-3" @monthClosed="monthClosed" :date="date" :disabled="showCloseBtn"/>
        </v-layout>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      class="header"
      :headers="headers"
      :items="allSalaryInMonthData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :pagination.sync="pagination"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr :class="{ fired: props.item.user.fired }">
          <!--Сотрудник-->
          <td>{{ props.item.user.shortName }}</td>
          <!--Часы-->
          <td>
            <div v-if="props.item.totals.workHours + props.item.totals.overtime + props.item.totals.night +
                props.item.totals.home + props.item.totals.order + props.item.totals.welding">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.workHours + m.totals.overtime + m.totals.night + m.totals.home +
                m.totals.order + m.totals.welding">
                  <div v-if="m.totals.workHours">
                    Рабочие: {{ m.totals.workHours }}
                  </div>
                  <div v-if="m.totals.overtime">
                    Переработки: {{ m.totals.overtime }}
                  </div>
                  <div v-if="m.totals.night">
                    Ночные: {{ m.totals.night }}
                  </div>
                  <div v-if="m.totals.home">
                    Нет работы/Сидит дома: {{ m.totals.home }}
                  </div>
                  <div v-if="m.totals.order">
                    За ответственность: {{ m.totals.order }}
                  </div>
                  <div v-if="m.totals.welding">
                    Cварка: {{ m.totals.welding }}
                  </div>
                  <v-divider/>
                  {{ normMonth(m.month) }}: {{ (m.totals.workHours + m.totals.overtime + m.totals.night + m.totals.home).toFixed(2) }}
                  <v-divider></v-divider>
                </template>
              </div>
              <div>Итого: {{ (props.item.totals.workHours + props.item.totals.overtime + props.item.totals.night +
                props.item.totals.home).toFixed(2) }}
              </div>
            </div>
          </td>
          <!--За часы, руб.-->
          <td>
            <div v-if="props.item.totals.workHoursMoney + props.item.totals.overtimeMoney +
                props.item.totals.nightMoney + props.item.totals.homeMoney + props.item.totals.orderMoney +
                props.item.totals.weldingMoney">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.workHoursMoney + m.totals.overtimeMoney + m.totals.nightMoney +
                  m.totals.homeMoney + m.totals.orderMoney + m.totals.weldingMoney">
                  <div v-if="m.totals.workHours">
                    Рабочие: {{ m.totals.workHoursMoney.toLocaleString() }}
                  </div>
                  <div v-if="m.totals.overtime">
                    Переработки: {{ m.totals.overtimeMoney.toLocaleString() }}
                  </div>
                  <div v-if="m.totals.night">
                    Ночные: {{ m.totals.nightMoney.toLocaleString() }}
                  </div>
                  <div v-if="m.totals.home">
                    Нет работы/Сидит дома: {{ m.totals.homeMoney.toLocaleString() }}
                  </div>
                  <div v-if="m.totals.order">
                    За ответственность: {{ m.totals.orderMoney.toLocaleString() }}
                  </div>
                  <div v-if="m.totals.welding">
                    Доплата за сварку: {{ m.totals.weldingMoney.toLocaleString() }}
                  </div>
                  <v-divider/>
                  {{ normMonth(m.month) }}: {{ (m.totals.workHoursMoney + m.totals.overtimeMoney + m.totals.nightMoney +
                  m.totals.homeMoney + m.totals.orderMoney + m.totals.weldingMoney).toLocaleString() }}
                  <v-divider></v-divider>
                </template>
              </div>
              <div>Итого: {{ (props.item.totals.workHoursMoney + props.item.totals.overtimeMoney +
                props.item.totals.nightMoney + props.item.totals.homeMoney + props.item.totals.orderMoney +
                props.item.totals.weldingMoney).toLocaleString() }}
              </div>
            </div>
          </td>
          <!--Оценки, руб.-->
          <td>
            <div v-if="props.item.totals.positiveGradeMoney - props.item.totals.negativeGradeMoney">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.positiveGradeMoney - m.totals.negativeGradeMoney">
                  {{ normMonth(m.month) }}: {{ (m.totals.positiveGradeMoney -
                  m.totals.negativeGradeMoney).toLocaleString() }}
                </template>
              </div>
              <v-divider/>
              <div>Итого: {{ (props.item.totals.positiveGradeMoney -
                props.item.totals.negativeGradeMoney).toLocaleString()}}
              </div>
            </div>
          </td>
          <!--Авто, руб.-->
          <td>
            <div v-if="props.item.totals.privateCar + props.item.totals.dutyCar">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.privateCar + m.totals.dutyCar">
                  {{ normMonth(m.month) }}: {{ (m.totals.privateCar + m.totals.dutyCar).toLocaleString() }}
                </template>
              </div>
              <v-divider></v-divider>
              <div>Итого: {{ (props.item.totals.privateCar + props.item.totals.dutyCar).toLocaleString()}}</div>
            </div>
          </td>
          <!--Проезд, руб.-->
          <td>
            <div v-if="props.item.totals.transportMoney || props.item.totals.transportOfficeMoney">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.transportMoney + m.totals.transportOfficeMoney">
                  {{ normMonth(m.month) }}: {{ (m.totals.transportMoney +
                  m.totals.transportOfficeMoney).toLocaleString() }}
                </template>
              </div>
              <v-divider/>
              <div>Итого: {{ (props.item.totals.transportMoney +
                props.item.totals.transportOfficeMoney).toLocaleString()}}
              </div>
            </div>
          </td>
          <!--Премии/вычеты, руб.-->
          <td>
            <div v-if="props.item.bonus">{{ props.item.bonus.toLocaleString() }}</div>
          </td>
          <!--ЗОЖ, руб.-->
          <td>
            <div v-if="props.item.totals.healthyDayMoney">
              <div v-for="m in props.item.months">
                <template v-if="m.totals.healthyDayMoney">
                  {{ normMonth(m.month) }}: {{ m.totals.healthyDayMoney.toLocaleString() }}
                </template>
              </div>
              <v-divider></v-divider>
              <div>Итого: {{ props.item.totals.healthyDayMoney.toLocaleString()}}</div>
            </div>
          </td>
          <!--Аванс, руб.-->
          <td>{{ props.item.advance.toLocaleString() }}</td>
          <!--Разное, руб.-->
          <td>
            <div v-if="props.item.totals.vacationMoney">
              <div v-for="m in props.item.months">
                {{ normMonth(m.month) }}: {{ m.totals.vacationMoney.toLocaleString() }}
              </div>
              <v-divider/>
              <div>Итого: {{ props.item.totals.vacationMoney.toLocaleString()}}</div>
            </div>
          </td>
          <!--Основная часть (-аванс,-авто), руб.-->
          <td>{{(props.item.totals.workHoursMoney + props.item.totals.overtimeMoney + props.item.totals.nightMoney +
            props.item.totals.homeMoney + props.item.totals.orderMoney + props.item.totals.weldingMoney +
            props.item.totals.positiveGradeMoney - props.item.totals.negativeGradeMoney +
            props.item.totals.transportMoney + props.item.totals.transportOfficeMoney + props.item.bonus +
            props.item.totals.healthyDayMoney - props.item.advance).toLocaleString() }}
          </td>
          <!--К выдаче (+аванс,-авто), руб.-->
          <td>{{(props.item.totals.workHoursMoney + props.item.totals.overtimeMoney + props.item.totals.nightMoney +
            props.item.totals.homeMoney + props.item.totals.orderMoney + props.item.totals.weldingMoney +
            props.item.totals.positiveGradeMoney - props.item.totals.negativeGradeMoney +
            props.item.totals.transportMoney + props.item.totals.transportOfficeMoney + props.item.bonus +
            props.item.totals.healthyDayMoney).toLocaleString() }}
          </td>
        </tr>
      </template>
      <template slot="footer" v-if="footerData.workHours">
        <td>Всего</td>
        <!--Часы-->
        <td>
          <div>
            Рабочие: {{ footerData.workHours}}
          </div>
          <div>
            Переработки: {{ footerData.overtime}}
          </div>
          <div>Итого: {{ (footerData.workHours + footerData.overtime + footerData.night +
            footerData.home).toFixed(2)}}
          </div>
        </td>
        <!--За часы, руб.-->
        <td>
          <div>
            Рабочие: {{ footerData.workHoursMoney.toLocaleString()}}
          </div>
          <div>
            Переработки: {{ footerData.overtimeMoney.toLocaleString()}}
          </div>
          <div>Итого: {{ (footerData.workHoursMoney + footerData.overtimeMoney + footerData.nightMoney +
            footerData.homeMoney + footerData.orderMoney + footerData.weldingMoney).toLocaleString() }}
          </div>
        </td>
        <!--Оценки, руб.-->
        <td>
          {{ (footerData.positiveGradeMoney - footerData.negativeGradeMoney).toLocaleString() }}
        </td>
        <!--Авто, руб.-->
        <td>
          {{ (footerData.privateCar + footerData.dutyCar).toLocaleString() }}
        </td>
        <!--Проезд, руб.-->
        <td>
          {{ (footerData.transportMoney + footerData.transportOfficeMoney).toLocaleString() }}
        </td>
        <!--Премии/вычеты, руб.-->
        <td>
          {{ bonus.toLocaleString() }}
        </td>
        <!--ЗОЖ, руб.-->
        <td>
          {{ footerData.healthyDayMoney.toLocaleString() }}
        </td>
        <!--Аванс, руб.-->
        <td>
          {{ advance.toLocaleString() }}
        </td>
        <!--Разное, руб.-->
        <td>
          {{ footerData.vacationMoney.toLocaleString() }}
        </td>
        <!--Основная часть (-аванс,-авто), руб.-->
        <td>
          {{ (footerData.workHoursMoney + footerData.overtimeMoney + footerData.nightMoney +
          footerData.homeMoney + footerData.orderMoney + footerData.weldingMoney +
          footerData.positiveGradeMoney - footerData.negativeGradeMoney + footerData.transportMoney +
          footerData.transportOfficeMoney + bonus + footerData.healthyDayMoney - advance).toLocaleString() }}
        </td>
        <!--К выдаче (+аванс,-авто), руб.-->
        <td>
          {{ (footerData.workHoursMoney + footerData.overtimeMoney + footerData.nightMoney +
          footerData.homeMoney + footerData.orderMoney + footerData.weldingMoney +
          footerData.positiveGradeMoney - footerData.negativeGradeMoney + footerData.transportMoney +
          footerData.transportOfficeMoney + bonus + footerData.healthyDayMoney).toLocaleString() }}
        </td>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {allSalaryInMonth} from './query'
  import {allCompanies} from '../financial_info/query'
  import utilMixin from '../utils'
  import MonthsFilter from '../MonthsFilter'
  import CloseSalary from './CloseSalary'
  import auth from '../../auth/auth'

  export default {
    components: {
      CloseSalary,
      MonthsFilter
    },
    name: 'salary',
    metaInfo: {
      title: 'Расчет заработной платы'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: allSalaryInMonth,
        loadingKey: 'loadingQueriesCount',
        variables () {
          return {
            date: this.date,
            companyFilter: this.company
          }
        },
        update (data) {
          this.allSalaryInMonthData = JSON.parse(JSON.stringify(data.allSalaryInMonth.users))
          this.allSalaryInMonthData.sort((a, b) => a.user.shortName.localeCompare(b.user.shortName))
          this.footerData = JSON.parse(JSON.stringify(data.allSalaryInMonth.totals))
          this.advance = 0
          this.bonus = 0
          this.allSalaryInMonthData.forEach(item => {
            this.advance += item.advance
            this.bonus += item.bonus
          })
        },
        skip () {
          return !this.date
        }
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
    created () {
      this.date = this.getDefaultFilterDate()
    },
    data () {
      return {
        allSalaryInMonthData: [],
        footerData: [],
        allCompaniesData: [],
        bonus: 0,
        advance: 0,
        date: null,
        company: null,
        headers: [
          {text: 'Сотрудник', align: 'left', sortable: false},
          {text: 'Часы', align: 'center', sortable: false},
          {text: 'За часы, руб.', align: 'center', sortable: false},
          {text: 'Оценки, руб.', align: 'center', sortable: false},
          {text: 'Авто, руб.', align: 'center', sortable: false},
          {text: 'Проезд, руб.', align: 'center', sortable: false},
          {text: 'Премии/ вычеты, руб.', align: 'center', sortable: false},
          {text: 'ЗОЖ, руб.', align: 'center', sortable: false},
          {text: 'Аванс, руб.', align: 'center', sortable: false},
          {text: 'Разное, руб.', align: 'center', sortable: false},
          {text: 'Основная часть (-аванс,-авто), руб.', align: 'center', sortable: false},
          {text: 'К выдаче (+аванс,-авто), руб.', align: 'center', sortable: false}
        ],
        rpp: [
          10, 25, {text: 'Все', value: -1}
        ],
        pagination: {
          rowsPerPage: -1
        },
        loadingQueriesCount: 0,
        monthsLoading: true
      }
    },
    methods: {
      normMonth (month) {
        let year = month.slice(2, 4)
        month = month.slice(4).length > 1 ? month.slice(4) : '0' + month.slice(4)
        return month + '.' + year
      },
      monthClosed () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Месяц закрыт'
        })
        this.$apollo.queries.query.refetch()
        setTimeout(() => {
          this.$refs.salaryMonthFilter.$apollo.queries.firstMonth.refetch()
        }, 1000)
      }
    },
    computed: {
      showCloseBtn () {
        if (this.monthsLoading || this.loadingQueriesCount > 0) {
          return false
        }
        if (this.$refs.salaryMonthFilter) {
          return this.date === this.$refs.salaryMonthFilter.months[0].id && auth.user.id === 27
        }
      }
    }
  }
</script>

<style>
  div.header table thead th {
    width: 170px;
    max-width: 170px;
    word-wrap: break-word;
    white-space: normal;
  }

  .td-center {
    text-align: center;
  }
</style>
