<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <v-btn v-if="backBtnRoute" :to="backBtnRoute" icon :title="backBtnTitle">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <span class="headline">{{ title }}</span>
        <v-spacer/>
        <slot name="filter"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="loggingData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td class="text-xs-center">{{ formatDateTime(props.item.date) }}</td>
          <td class="text-xs-center" v-if="!instanceId">{{ props.item.instance }}</td>
          <td class="text-xs-center">{{ props.item.user.shortName }}</td>
          <td>
            <div v-for="c in props.item.change.split('|=-=|')">
              <span v-if="c">{{ c }}</span>
              <span v-if="!c">Запись создана</span>
            </div>
          </td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {allJournal} from './query'
  import utilMixin from '../utils'

  export default {
    name: 'logging',
    metaInfo () {
      return {
        title: (this.tab === 'tab-logging' || !this.tab) ? this.title : this.defaultTitle
      }
    },
    props: {
      modelName: String,
      instanceId: String,
      tab: String,
      title: {
        type: String,
        default: 'История'
      },
      defaultTitle: String,
      backBtnTitle: String,
      backBtnRoute: {
        type: Object,
        default: null
      }
    },
    mixins: [utilMixin],
    apollo: {
      loggingData: {
        fetchPolicy: 'cache-and-network',
        query: allJournal,
        variables () {
          return {
            modelName: this.modelName,
            instanceId: this.instanceId
          }
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    watch: {
      tab: function (val) {
        if (val === 'tab-logging') {
          this.$apollo.queries.loggingData.refetch()
        }
      }
    },
    data () {
      return {
        loggingData: [],
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0
      }
    },
    computed: {
      headers () {
        const headers = [
          {text: 'Дата', align: 'center', value: 'date', sortable: false, width: '160px'},
          {text: 'Объект изменения', align: 'center', value: 'instance', sortable: false, width: '350px'},
          {text: 'Кто изменил', align: 'center', value: 'userId', sortable: false, width: '250px'},
          {text: 'Изменения', align: 'center', value: 'change', sortable: false}
        ]
        if (this.instanceId) {
          headers.splice(1, 1)
        }
        return headers
      }
    }
  }
</script>
