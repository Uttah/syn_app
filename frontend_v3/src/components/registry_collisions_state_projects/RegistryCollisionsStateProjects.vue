<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Реестр коллизий этапов проектов</span>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="registryCollisionsStateProjectsData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td>{{ pad(props.item.project.number, 5) }} - {{ props.item.project.description }}</td>
          <td class="text-xs-center">
            <span v-for="r in props.item.reports">
              <a :href="'/manage_report/' + r.id" target="_blank">{{ r.id }}</a>&ensp;
            </span>
          </td>
          <td class="text-xs-center">&#8776;{{ props.item.sumHours.toFixed(2) }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {registryCollisionsStateProjects} from './query'
  import utilMixin from '../utils'

  export default {
    name: 'registry-collisions-state-projects',
    metaInfo: {
      title: 'Реестр коллизий этапов проектов'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: registryCollisionsStateProjects,
        update (data) {
          this.registryCollisionsStateProjectsData = data.registryCollisionsStateProjects
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        registryCollisionsStateProjectsData: [],
        headers: [
          {text: 'Проект', align: 'left', value: 'project', sortable: false},
          {text: 'Отчеты', align: 'center', value: 'reports', sortable: false},
          {text: 'Всего часов', align: 'center', value: 'sumHours', sortable: false}
        ],
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0
      }
    }
  }
</script>
