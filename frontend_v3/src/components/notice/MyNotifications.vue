<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Мои уведомления</span>
        <v-spacer/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="allNoticeData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td class="text-xs-center">{{ formatDateTime(props.item.date) }}</td>
          <td class="text-xs-center">{{ props.item.created.shortName }}</td>
          <td>{{ props.item.text }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {getAllNotice} from './query'
  import utilMixin from '../utils'

  export default {
    name: 'my-notifications',
    metaInfo: {
      title: 'Мои уведомления'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: getAllNotice,
        update (data) {
          this.allNoticeData = data.getAllNotice
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        allNoticeData: [],
        headers: [
          {text: 'Дата', align: 'center', value: 'status', sortable: false},
          {text: 'От кого', align: 'center', value: 'user_added', sortable: false},
          {text: 'Содержание', align: 'center', value: 'user', sortable: false}
        ],
        rpp: [
          50, 100, {text: 'Все', value: -1}
        ],
        loadingQueriesCount: 0
      }
    }
  }
</script>

<style scoped>

</style>
