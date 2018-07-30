<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Список ответственных по проектам</span>
        <v-spacer/>
        <create-order-dialog @created="created"/>
        <update-delete-order-dialog :input="input" @updated="updated" @deleted="deleted"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="allOrdersData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr @click="updateDialog(props.item)">
          <td class="text-xs-center">{{ pad(props.item.project.number, 5) }}</td>
          <td class="text-xs-center">{{ props.item.responsible.shortName }}</td>
          <td class="text-xs-center">{{ formatDate(props.item.date) }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {allOrders} from './query'
  import utilMixin from '../utils'
  import CreateOrderDialog from './CreateOrder'
  import UpdateDeleteOrderDialog from './UpdateDeleteOrder'
  export default {
    name: 'orders',
    components: {
      UpdateDeleteOrderDialog,
      CreateOrderDialog
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: allOrders,
        update (data) {
          this.allOrdersData = data.allOrders
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    metaInfo: {
      title: 'Список ответственных'
    },
    data () {
      return {
        allOrdersData: [],
        headers: [
          {text: 'Проект', align: 'center', value: 'project', sortable: false},
          {text: 'Ответственный', align: 'center', value: 'responsible', sortable: false},
          {text: 'Дата', align: 'center', value: 'date', sortable: false}
        ],
        input: {
          projectId: null,
          responsible: null,
          date: null
        },
        rpp: [
          10, 25, {text: 'Все', value: -1}
        ],
        loadingQueriesCount: 0
      }
    },
    methods: {
      created () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Ответственный назначен'
        })
        this.$apollo.queries.query.refetch()
      },
      deleted () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Ответственный удален'
        })
        this.$apollo.queries.query.refetch()
      },
      updated () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Ответственный обновлен'
        })
        this.$apollo.queries.query.refetch()
      },
      updateDialog (input) {
        this.input = JSON.parse(JSON.stringify(input))
      }
    }
  }
</script>

<style scoped>

</style>
