<template>
  <v-card>
    <v-card-title>
      <v-progress-linear class="pa-0 ma-0" height="4" :indeterminate="true"
                         :active="loadingQueriesCount > 0"/>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Начисления</span>
        <v-spacer/>
      </v-toolbar>
    </v-card-title>
    <div class="pb-5" v-for="company in accrualsData">
      <span class="title ml-5">{{ company.name }}</span>
      <v-data-table
        :headers="company.id !== 'cash' ? headersCompany: headersCash"
        :items="company.accruals"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        :rows-per-page-text="'Строк на странице'"
        :no-data-text="'Нет доступных данных'"
        hide-actions
        style="max-width: 1000px"
        class="mx-auto"
      >
        <template slot="items" slot-scope="props">
          <tr>
            <td>
              <v-tooltip top>
                <v-icon v-if="props.item.mainPart < 0" color="error" slot="activator">warning</v-icon>
                <span>Основная часть меньше нуля</span>
              </v-tooltip>
              {{ props.item.user }}
            </td>
            <td class="text-xs-center" v-if="company.id === 'cash'">{{ props.item.auto.toLocaleString() }}</td>
            <td class="text-xs-center" v-if="company.id === 'cash'">{{ props.item.other.toLocaleString() }}</td>
            <td class="text-xs-center" v-if="company.id !== 'cash'">{{ props.item.bonus.toLocaleString() }}</td>
            <td class="text-xs-center" v-if="company.id !== 'cash'">{{ props.item.advance.toLocaleString() }}</td>
            <td class="text-xs-center">{{ props.item.mainPart.toLocaleString() }}</td>
            <td class="text-xs-center" v-if="company.id === 'cash'">{{ (props.item.auto + props.item.other + props.item.mainPart).toLocaleString() }}</td>
          </tr>
        </template>
      </v-data-table>
    </div>
  </v-card>
</template>

<script>
  import {accruals} from './query'

  export default {
    name: 'accruals',
    metaInfo: {
      title: 'Начисления'
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: accruals,
        update (data) {
          this.accrualsData = data.accruals
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        accrualsData: [],
        headersCompany: [
          {text: 'Сотрудник', align: 'left', value: 'user', sortable: false},
          {text: 'Премии/вычеты', align: 'center', value: 'bonus', sortable: false},
          {text: 'Аванс', align: 'center', value: 'advance', sortable: false},
          {text: 'Основная часть', align: 'center', value: 'mainPart', sortable: false}
        ],
        headersCash: [
          {text: 'Сотрудник', align: 'left', value: 'user', sortable: false},
          {text: 'Авто', align: 'center', value: 'auto', sortable: false},
          {text: 'Разное', align: 'center', value: 'other', sortable: false},
          {text: 'Основная часть', align: 'center', value: 'mainPart', sortable: false},
          {text: 'Итого', align: 'center', value: 'mainPart', sortable: false}
        ],
        loadingQueriesCount: 0
      }
    }
  }
</script>

<style scoped>

</style>
