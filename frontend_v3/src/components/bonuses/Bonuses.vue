<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
          <span class="ma-0 headline">Премии и вычеты</span>
          <v-spacer/>
          <create-bonus-dialog @created="created"/>
          <update-delete-bonus-dialog :input="input" @deleted="deleted" @updated="updated"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="allBonusesData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr @click="updateDialog(props.item)">
          <td>{{ status(props.item) }}</td>
          <td class="text-xs-center">{{ props.item.userAdded.shortName }}<div>{{ formatDateTime(props.item.timeAdded) }}</div></td>
          <td class="text-xs-center">{{ props.item.user.shortName }}</td>
          <td class="text-xs-center">{{ pad(props.item.project.number, 5) }}</td>
          <td class="text-xs-center">{{ props.item.amount }}<div v-if="props.item.cash">нал.</div></td>
          <td class="text-xs-center">{{ props.item.installments > 1 ? props.item.installments + ' мес.' : '' }}</td>
          <td>{{ props.item.description }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
    import {allBonuses} from './query'
    import CreateBonusDialog from './CreateBonus.vue'
    import UpdateDeleteBonusDialog from './UpdateDeleteBonus'
    import utilMixin from '../utils'
    export default {
      name: 'Bonuses',
      metaInfo: {
        title: 'Премии и вычеты'
      },
      components: {
        CreateBonusDialog,
        UpdateDeleteBonusDialog
      },
      mixins: [utilMixin],
      apollo: {
        query: {
          fetchPolicy: 'cache-and-network',
          query: allBonuses,
          update (data) {
            this.allBonusesData = data.allBonuses
          },
          loadingKey: 'loadingQueriesCount'
        }
      },
      data () {
        return {
          allBonusesData: [],
          headers: [
            {text: 'Статус', align: 'left', value: 'status', sortable: false},
            {text: 'Кем вынесено', align: 'center', value: 'user_added', sortable: false},
            {text: 'Сотрудник', align: 'center', value: 'user', sortable: false},
            {text: 'Проект', align: 'center', value: 'project', sortable: false},
            {text: 'Сумма', align: 'center', value: 'amount', sortable: false},
            {text: 'Рассрочка', align: 'center', value: 'installments', sortable: false},
            {text: 'Описание', align: 'center', value: 'description', sortable: false, width: '50%'}
          ],
          input: {
            userId: null,
            projectId: null,
            amount: null,
            installments: 1,
            description: null
          },
          rpp: [
            10, 25, {text: 'Все', value: -1}
          ],
          monthArray: {'1': 'Январь', '2': 'Февраль', '3': 'Март', '4': 'Апрель', '5': 'Май', '6': 'Июнь', '7': 'Июль', '8': 'Август', '9': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'},
          loadingQueriesCount: 0
        }
      },
      methods: {
        status (obj) {
          if (obj.counted) {
            const date = new Date(obj.month)
            return 'Начислено за ' + this.monthArray[date.getMonth() + 1].toLowerCase() + ' ' + date.getFullYear()
          }
          return ''
        },
        created () {
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Премия/вычет создан'
          })
          this.$apollo.queries.query.refetch()
        },
        updated () {
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Премия/вычет обновлен'
          })
          this.$apollo.queries.query.refetch()
        },
        deleted () {
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Премия/вычет удален'
          })
          this.$apollo.queries.query.refetch()
        },
        updateDialog (input) {
          this.input = JSON.parse(JSON.stringify(input))
        }
      }
    }
</script>

