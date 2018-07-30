<template>
  <div>
    <v-toolbar flat color="background">
      <v-spacer/>
      <months-filter v-model="date" hide-details salary-months/>
    </v-toolbar>
    <div class="px-5 my-4">
      <div class="title">{{ shortName }}</div>
      <div class="pl-4">
        <div v-if="userSalaryInfoData && userSalaryInfoData.costHour">
          <div class="subheading pt-3">Финансовая информация:</div>
          <table v-if="!userSalaryInfoData.salary">
            <thead>
            <tr>
              <th></th>
              <th>Коэффициент</th>
              <th>Вес</th>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td class="name-coefficient">СМР общее</td>
              <td>{{ userSalaryInfoData.myGeneral }}</td>
              <td>{{ userSalaryInfoData.general }}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Навык сварочных работ</td>
              <td>{{ userSalaryInfoData.myWelding }}</td>
              <td>{{ userSalaryInfoData.welding }}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Опыт работы в компании</td>
              <td>{{ userSalaryInfoData.myExperience }}</td>
              <td>{{ userSalaryInfoData.experience }}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Знание основ электротехники</td>
              <td>{{ userSalaryInfoData.myEtech}}</td>
              <td>{{ userSalaryInfoData.etech }}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Чтение схем</td>
              <td>{{ userSalaryInfoData.mySchematic}}</td>
              <td>{{ userSalaryInfoData.schematic}}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Инициативность</td>
              <td>{{ userSalaryInfoData.myInitiative}}</td>
              <td>{{ userSalaryInfoData.initiative}}</td>
            </tr>
            <tr>
              <td class="name-coefficient">Дисциплина, прилежность</td>
              <td>{{ userSalaryInfoData.myDiscipline}}</td>
              <td>{{ userSalaryInfoData.discipline}}</td>
            </tr>
            </tbody>
          </table>
          <div class="pl-3 pt-3" v-if="userSalaryInfoData.salary">Ставка: {{ userSalaryInfoData.salary.toLocaleString() }} руб.</div>
          <div class="pl-3 pt-1">Оклад: {{ userSalaryInfoData.base.toLocaleString() }} руб.</div>
          <div class="pl-3 pt-1" v-if="userSalaryInfoData.advance">Аванс: {{ userSalaryInfoData.advance.toLocaleString() }} руб.</div>
          <div class="pl-3 pt-1" v-if="userSalaryInfoData.avg">Итоговый коэффициент: {{ userSalaryInfoData.avg }}</div>
          <div class="pl-3 pt-1" v-if="userSalaryInfoData.baseCostHour">Базовая стоимость часа: {{ userSalaryInfoData.baseCostHour.toLocaleString()}} руб.</div>
          <div class="pl-3 pt-1">Стоимость часа в этом месяце: {{ userSalaryInfoData.costHour.toFixed(2).toLocaleString() }}
            руб.
          </div>
          <div class="pl-3 pt-1">Количество рабочих часов в текущем месяце: {{ userSalaryInfoData.workHoursInMonth }} ч.
          </div>
        </div>

        <div class="headline my-4" v-if="!salaryInMonthData.user">Нет подтвержденных отчетов</div>
        <div v-if="salaryInMonthData.user">
          <div class="subheading pt-3 pb-3">Рабочие часы:</div>
          <div class="pl-3" v-for="m in salaryInMonthData.months">
            <template v-if="m.totals.workHours">
              <span class="month">{{ generateMonthText(m.month) }}:</span><span class="hours">{{ m.totals.workHours }} ч.
                </span>{{ m.totals.workHoursMoney.toLocaleString() }} руб.
            </template>
          </div>

          <div v-if="salaryInMonthData.totals.overtime">
            <div class="subheading pt-3 pb-3">Переработки:</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.overtime">
                <span class="month">{{ generateMonthText(m.month) }}:</span><span class="hours">{{ m.totals.overtime }} ч.
                  </span>{{ m.totals.overtimeMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.night">
            <div class="subheading pt-3 pb-3">Ночные:</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.night">
                <span class="month">{{ generateMonthText(m.month) }}:</span><span class="hours">{{ m.totals.night }} ч.</span>
                {{ m.totals.nightMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.home">
            <div class="subheading pt-3 pb-3">Нет работы/Сидит дома:</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.home">
                <span class="month">{{ generateMonthText(m.month) }}:</span><span class="hours">{{ m.totals.home }} ч.</span>
                {{ m.totals.homeMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.order">
            <div class="subheading pt-3 pb-3">За ответственность:</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.order">
                <span class="month">{{ generateMonthText(m.month) }}:</span><span class="hours">{{ m.totals.order }} ч.</span>
                {{ m.totals.orderMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.welding">
            <div class="subheading pt-3 pb-3">Сварка:</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.welding">
                <span class="month">{{ generateMonthText(m.month) }}:</span><span
                class="hours">{{ m.totals.welding }} ч.</span>
                {{ m.totals.weldingMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.positiveGradeMoney - salaryInMonthData.totals.negativeGradeMoney">
            <div class="subheading pt-3 pb-3">Оценки
              <v-menu open-on-hover top offset-y>
                <v-btn icon slot="activator"><v-icon>help_outline</v-icon></v-btn>
                <v-data-table
                  :headers="headers"
                  :items="allGradeCoefficients"
                  hide-actions
                  rows-per-page-text="Строк на странице"
                  no-data-text="Нет доступных данных"
                  class="pb-3"
                  style="background-color: white;"
                >
                  <template slot="items" slot-scope="props">
                    <td class="text-xs-center">{{ props.item.quality }}</td>
                    <td class="text-xs-center">{{ props.item.time }}</td>
                    <td class="text-xs-center">{{ props.item.coefficient }}</td>
                  </template>
                </v-data-table>
              </v-menu>
            </div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.positiveGradeMoney - m.totals.negativeGradeMoney">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ (m.totals.positiveGradeMoney - m.totals.negativeGradeMoney).toLocaleString() }} руб.
              </template>
            </div>

            <div class="subheading pt-3 pb-3"><i>Максимально возможная доплата за оценки 5/5 (для справки):</i></div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.idealGradeMoney">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ m.totals.idealGradeMoney.toLocaleString() }} руб.
              </template>
            </div>

          </div>

          <div v-if="salaryInMonthData.totals.privateCar + salaryInMonthData.totals.dutyCar">
            <div class="subheading pt-3 pb-3">Авто</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.privateCar + m.totals.dutyCar">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ (m.totals.privateCar + m.totals.dutyCar).toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.transportMoney || salaryInMonthData.totals.transportOfficeMoney">
            <div class="subheading pt-3 pb-3">Проезд</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.transportMoney + m.totals.transportOfficeMoney">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ (m.totals.transportMoney + m.totals.transportOfficeMoney).toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.bonus || userSalaryBonusInfo.length">
            <div class="subheading pt-3 pb-3">Премии/вычеты</div>
            <div class="pl-3" v-for="b in userSalaryBonusInfo">
              <div v-if="b.installments === 1">
                {{ b.amount }} руб. - {{ b.description }} <span v-if="b.cash">(наличными)</span>
              </div>
              <div v-if="b.installments > 1">
                {{ b.amount / b.installments  }} руб. - {{ b.description }} ({{ b.amount }}, <span v-if="b.cash">наличными,</span> рассрочка на {{ b.installments }} мес.)
              </div>
            </div>
            <div class="pl-3">
              Итого: {{ salaryInMonthData.bonus.toLocaleString() }} руб.
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.healthyDayMoney">
            <div class="subheading pt-3 pb-3">ЗОЖ</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.healthyDayMoney">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ m.totals.healthyDayMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div v-if="salaryInMonthData.totals.vacationMoney">
            <div class="subheading pt-3 pb-3">Разное</div>
            <div class="pl-3" v-for="m in salaryInMonthData.months">
              <template v-if="m.totals.vacationMoney">
                <span class="month-without-hours">{{ generateMonthText(m.month) }}:</span>
                {{ m.totals.vacationMoney.toLocaleString() }} руб.
              </template>
            </div>
          </div>

          <div>
            <div class="subheading pt-3 pb-3">Итого</div>
            <div class="pl-3">
              <span class="month-without-hours">Всего:</span>
              {{ (salaryInMonthData.totals.workHoursMoney + salaryInMonthData.totals.overtimeMoney +
              salaryInMonthData.totals.nightMoney + salaryInMonthData.totals.homeMoney + salaryInMonthData.totals.orderMoney
              +
              salaryInMonthData.totals.weldingMoney + salaryInMonthData.totals.positiveGradeMoney -
              salaryInMonthData.totals.negativeGradeMoney + salaryInMonthData.totals.privateCar +
              salaryInMonthData.totals.dutyCar
              + salaryInMonthData.totals.transportMoney + salaryInMonthData.totals.transportOfficeMoney +
              salaryInMonthData.bonus + salaryInMonthData.totals.healthyDayMoney +
              salaryInMonthData.totals.vacationMoney).toLocaleString() }} руб.
            </div>
            <div class="pl-3">
              <span class="month-without-hours">Аванс:</span>
              {{ salaryInMonthData.advance.toLocaleString() }} руб.
            </div>
            <div class="pl-3">
              <span class="month-without-hours">К выдаче:</span>
              {{ (salaryInMonthData.totals.workHoursMoney + salaryInMonthData.totals.overtimeMoney +
              salaryInMonthData.totals.nightMoney + salaryInMonthData.totals.homeMoney + salaryInMonthData.totals.orderMoney
              +
              salaryInMonthData.totals.weldingMoney + salaryInMonthData.totals.positiveGradeMoney -
              salaryInMonthData.totals.negativeGradeMoney + salaryInMonthData.totals.privateCar +
              salaryInMonthData.totals.dutyCar
              + salaryInMonthData.totals.transportMoney + salaryInMonthData.totals.transportOfficeMoney +
              salaryInMonthData.bonus + salaryInMonthData.totals.healthyDayMoney +
              salaryInMonthData.totals.vacationMoney - salaryInMonthData.advance).toLocaleString() }} руб.
            </div>
          </div>

          <div>
            <div class="subheading pt-3 pb-3">За год</div>
            <div class="pl-3">
              <template>
                <span class="month-without-hours">Cумма за текущий год:</span>
                {{ sumYear.toLocaleString() }} руб.
              </template>
            </div>
            <div class="pl-3">
              <template>
                <span class="month-without-hours">Среднегодовая заработная плата:</span>
                {{ avgYear.toLocaleString() }} руб.
              </template>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
  import auth from '../../auth/auth'
  import gql from 'graphql-tag'
  import utilMixin from '../utils'
  import {allSalaryInMonth, userSalaryInfo, allGradeCoefficients, userSalaryBonusInfo} from './query'
  import MonthsFilter from '../MonthsFilter'

  export default {
    components: {MonthsFilter},
    name: 'user-salary',
    metaInfo: {
      title: 'Зарплатная ведомость сотрудника'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: userSalaryInfo,
        variables () {
          return {
            date: this.date
          }
        },
        update (data) {
          this.shortName = auth.user.shortName
          this.userSalaryInfoData = JSON.parse(JSON.stringify(data.userSalaryInfo))
          this.userSalaryInfoData.salary = this.userSalaryInfoData.salary ? this.userSalaryInfoData.salary : 0
        }
      },
      query2: {
        fetchPolicy: 'cache-and-network',
        query: allSalaryInMonth,
        variables () {
          return {
            userId: auth.user.id,
            date: this.date
          }
        },
        update (data) {
          this.salaryInMonthData = JSON.parse(JSON.stringify(data.allSalaryInMonth.users.length > 0 ? data.allSalaryInMonth.users[0] : data.allSalaryInMonth.users))
        }
      },
      userSalaryBonusInfo: {
        fetchPolicy: 'cache-and-network',
        query: userSalaryBonusInfo,
        variables () {
          return {
            date: this.lastSalaryMonth && this.date !== this.lastSalaryMonth ? this.date : null
          }
        }
      },
      getLastSalaryMonth: {
        fetchPolicy: 'cache-and-network',
        query: gql`{
          lastSalaryMonth
        }`,
        update (data) {
          this.lastSalaryMonth = data.lastSalaryMonth.slice(4) + data.lastSalaryMonth.slice(2, 4)
        }
      },
      allGradeCoefficients: {
        fetchPolicy: 'cache-and-network',
        query: allGradeCoefficients
      },
      getUserSalarySumAvgYear: {
        fetchPolicy: 'cache-and-network',
        query: gql`query ($date: String!){
            userSalarySumAvgYear (date: $date) {
              sumYear
              avgYear
            }
          }`,
        variables () {
          return {
            date: this.date
          }
        },
        update (data) {
          this.sumYear = Math.round(data.userSalarySumAvgYear.sumYear)
          this.avgYear = Math.round(data.userSalarySumAvgYear.avgYear)
        }
      }
    },
    data () {
      return {
        shortName: '',
        userSalaryInfoData: null,
        salaryInMonthData: [],
        allGradeCoefficients: [],
        userSalaryBonusInfo: [],
        sumYear: 0,
        avgYear: 0,
        monthArray: {
          '1': 'Январь',
          '2': 'Февраль',
          '3': 'Март',
          '4': 'Апрель',
          '5': 'Май',
          '6': 'Июнь',
          '7': 'Июль',
          '8': 'Август',
          '9': 'Сентябрь',
          '10': 'Октябрь',
          '11': 'Ноябрь',
          '12': 'Декабрь'
        },
        date: this.getDefaultFilterDate(),
        lastSalaryMonth: null,
        headers: [
          {text: 'Оценка за качество', align: 'center', sortable: false},
          {text: 'Оценка за срок', align: 'center', sortable: false},
          {text: 'Коэффициент', align: 'center', sortable: false}
        ]
      }
    },
    methods: {
      generateMonthText (month) {
        let year = month.slice(0, 4)
        month = this.monthArray[month.slice(4)]
        return month + ' ' + year
      }
    }
  }
</script>

<style scoped>
  .month {
    float: left;
    width: 120px;
  }

  .hours {
    float: left;
    width: 150px;
    text-align: center;
  }

  .month-without-hours {
    float: left;
    width: 270px;
  }

  table th {
    width: 150px;
  }

  table td {
    text-align: center;
  }

  .name-coefficient {
    text-align: right;
    width: 250px;
  }

  table.table tbody td {
    height: 25px;
  }

</style>
