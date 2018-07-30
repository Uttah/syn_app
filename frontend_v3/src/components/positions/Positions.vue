<template>
  <v-card :raised="!getAll">
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="headline">Занимаемые должности</span>
        <v-spacer/>
        <template v-if="getAll">
          <header-filter @clearFilters="clearFilters">
            <v-layout row wrap justify-center class="pb-4">
              <v-flex xs11 class="filter-padding">
                <v-select
                  class="pr-3"
                  label="Компании"
                  :items="companies"
                  item-text="name"
                  item-value="id"
                  v-model="appliedFilters.company"
                  hide-details
                  clearable
                />
              </v-flex>
              <v-flex xs11 class="filter-padding">
                <v-select
                  class="pr-3"
                  label="Должности"
                  :items="filterPositions"
                  item-text="name"
                  item-value="id"
                  v-model="appliedFilters.position"
                  hide-details
                  clearable
                />
              </v-flex>
            </v-layout>
          </header-filter>

          <v-text-field append-icon="search" label="Поиск по сотруднику" single-line hide-details
                        v-model="searchQuery" style="max-width: 25%"/>
        </template>
        <template v-else>
          <positions-hire-dialog :user="user" @hire="hire"/>
          <positions-fire-dialog :selected-rows="selectedRows" :all-users="getAll" @fire="fire"/>
        </template>
      </v-toolbar>
      <v-toolbar v-if="getAll" flat color="white">
        <v-spacer/>
        <v-checkbox label="Показывать уволенных" v-model="showFired" hide-details style="flex-grow: 0; min-width: 240px"/>
        <positions-hire-dialog :user="user" @hire="hire"/>
        <positions-fire-dialog :selected-rows="selectedRows" :all-users="getAll" @fire="fire"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table :headers="headers" hide-actions :no-data-text="'Нет доступных данных'"
                  :items="positions" :loading="loadingQueriesCount > 0 ? 'loading' : false"
                  v-model="selectedRows" select-all v-if="!getAll">
      <!-- Таблица для отображения на странице пользователя -->
      <template slot="items" slot-scope="props">
        <tr :class="{ fired: props.item.fireDate }">
          <td>
            <v-checkbox primary hide-details v-model="props.selected" v-if="!props.item.fireDate"/>
          </td>
          <td>{{ props.item.position.company.name }}</td>
          <td>{{ props.item.position.name }}</td>
          <td class="text-xs-center">{{ formatDate(props.item.hireDate) }}</td>
          <td class="text-xs-center">{{ formatDate(props.item.fireDate) }}</td>
          <td class="text-xs-center">
            {{ formatMoney(props.item.salary) }} &#8381; ({{ props.item.fraction }}%)
          </td>
          <td class="text-xs-center">{{ formatMoney(props.item.base) }} &#8381;</td>
          <td class="text-xs-center">{{ formatMoney(props.item.advance) }} &#8381;</td>
          <td class="text-xs-center">
            <v-icon>{{ (props.item.byHours ? 'check_box' : 'check_box_outline_blank') }}</v-icon>
          </td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <v-data-table :headers="headers" no-data-text="Нет доступных данных"
                  no-results-text="Нет данных, удовлетворяющих запросу"
                  :rows-per-page-text="'Строк на странице'"
                  :items="positionsPaged.positions" :loading="loadingQueriesCount > 0 ? 'loading' : false"
                  v-model="selectedRows" select-all :rows-per-page-items="rpp"
                  :pagination.sync="pagination" must-sort
                  :total-items="positionsPaged.totalCount" v-else>
      <!-- Таблица для отображения всех должностей -->
      <template slot="items" slot-scope="props">
        <tr :class="{ fired: props.item.fireDate }">
          <td>
            <v-checkbox primary hide-details v-model="props.selected" v-if="!props.item.fireDate"/>
          </td>
          <td>{{ props.item.user.shortName }}</td>
          <td>{{ props.item.position.company.name }}</td>
          <td>{{ props.item.position.name }}</td>
          <td class="text-xs-center">{{ formatDate(props.item.hireDate) }}</td>
          <td class="text-xs-center">{{ formatDate(props.item.fireDate) }}</td>
          <td class="text-xs-center">
            <v-menu bottom offset-y>
              <span slot="activator" @click="tmp = props.item.salary; tmp2 = props.item.fraction">{{ formatMoney(props.item.salary) }} &#8381; ({{ props.item.fraction }}%)</span>
              <v-list v-if="!props.item.fireDate && auth.hasPermission('users.change_occupation')">
                <v-layout row justify-space-between>
                  <v-flex xs6>
                    <integer-field @click.native.stop class="mt-3 mr-2" label="Ставка, руб" v-model="tmp" autofocus/>
                  </v-flex>
                  <v-flex xs6>
                    <integer-field @click.native.stop class="mt-3 ml-2" label="Ставка, %" v-model="tmp2"/>
                  </v-flex>
                </v-layout>
                <v-btn>Отменить</v-btn>
                <v-btn @click="savePosition(props.item, 'salary')">Сохранить</v-btn>
              </v-list>
            </v-menu>
          </td>
          <td class="text-xs-center">
            <v-menu bottom offset-y>
              <span slot="activator" @click="tmp = props.item.base">{{ formatMoney(props.item.base) }} &#8381;</span>
              <v-list v-if="!props.item.fireDate && auth.hasPermission('users.change_occupation')">
                <integer-field @click.native.stop class="mt-3" label="База, руб" v-model="tmp" autofocus/>
                <v-btn>Отменить</v-btn>
                <v-btn @click="savePosition(props.item, 'base')">Сохранить</v-btn>
              </v-list>
            </v-menu>
          </td>
          <td class="text-xs-center">
            <v-menu bottom offset-y>
              <span slot="activator" @click="tmp = props.item.advance">{{ formatMoney(props.item.advance) }} &#8381;</span>
              <v-list v-if="!props.item.fireDate && auth.hasPermission('users.change_occupation')">
                <integer-field @click.native.stop class="mt-3" label="Аванс, руб" v-model="tmp" autofocus/>
                <v-btn>Отменить</v-btn>
                <v-btn @click="savePosition(props.item, 'advance')">Сохранить</v-btn>
              </v-list>
            </v-menu>
          </td>
          <td class="text-xs-center">
            <v-checkbox v-if="!props.item.fireDate && auth.hasPermission('users.change_occupation')"
                        hide-details v-model="props.item.byHours"
                        @change="savePosition(props.item, 'byHours')"/>
            <v-icon v-else>{{ (props.item.byHours ? 'check_box' : 'check_box_outline_blank') }}</v-icon>
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
  import {positionsQuery, pagedPositionsQuery, allCompanies, updateOccupation} from './query'
  import utilsMixin from '../utils'
  import PositionsHireDialog from './HireDialog.vue'
  import PositionsFireDialog from './FireDialog.vue'
  import _ from 'lodash'
  import auth from '../../auth/auth'
  import HeaderFilter from '../HeaderFilter.vue'
  import IntegerField from '../IntegerField'

  export default {
    components: {
      IntegerField,
      HeaderFilter,
      PositionsFireDialog,
      PositionsHireDialog
    },
    name: 'Positions',
    mixins: [utilsMixin],
    props: ['user'],
    metaInfo () {
      let name = null
      if (this.$parent.$parent.user) {
        name = this.$parent.$parent.user.shortName ? 'Сотрудник - ' + this.$parent.$parent.user.shortName : 'Сотрудник'
      }
      return {
        title: this.getAll ? 'Список должностей' : name
      }
    },
    apollo: {
      positions: {
        fetchPolicy: 'cache-and-network',
        query: positionsQuery,
        variables () {
          return {
            userId: this.user.id
          }
        },
        loadingKey: 'loadingQueriesCount',
        skip () {
          return this.getAll
        }
      },
      positionsPagedData: {
        fetchPolicy: 'cache-and-network',
        query: pagedPositionsQuery,
        variables () {
          return {
            input: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              sortBy: this.pagination.sortBy,
              search: this.searchText
            },
            showFired: this.showFired,
            filters: {
              company: this.appliedFilters.company ? this.appliedFilters.company : {},
              position: this.appliedFilters.position
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.positionsPaged = JSON.parse(JSON.stringify(data.positionsPaged))
          return null
        },
        skip () {
          return !this.getAll
        }
      },
      companies: {
        query: allCompanies,
        skip () {
          return !this.getAll
        }
      }
    },
    data () {
      return {
        positions: [],
        positionsPaged: {
          positions: [],
          totalCount: 0
        },
        loadingQueriesCount: 0,
        selectedRowsData: [],
        rpp: [
          10, 25, {text: 'Все', value: -1}
        ],
        searchText: '',
        searchQuery: '',
        pagination: this.getValue('pagination', {
          rowsPerPage: 10,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'user'
        }),
        showFired: false,
        companies: [],
        appliedFilters: this.getValue('filters', {
          company: [],
          position: []
        }),
        auth: auth,
        tmp: null,
        tmp2: null
      }
    },
    methods: {
      fire () {
        this.selectedRowsData = []
        if (!this.getAll) {
          this.$apollo.queries.positions.refetch()
        } else {
          this.$apollo.queries.positionsPagedData.refetch()
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Сотрудник уволен'
          })
        }
      },
      hire () {
        this.selectedRowsData = []
        if (this.$apollo.queries.positionsPagedData) {
          this.$apollo.queries.positionsPagedData.refetch()
          this.$notify({
            group: 'commonNotification',
            duration: 5000,
            text: 'Сотрудник принят'
          })
        }
      },
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      changeSort (newValue) {
        if (this.pagination.sortBy === newValue) {
          this.pagination.descending = !this.pagination.descending
        } else {
          this.pagination.sortBy = newValue
          this.pagination.descending = false
        }
      },
      savePosition (position, cell) {
        const input = {
          occupationId: position.id
        }
        switch (cell) {
          case 'salary': {
            input.salary = this.tmp
            input.fraction = this.tmp2
            break
          }
          case 'advance': {
            input.advance = this.tmp
            break
          }
          case 'base': {
            input.base = this.tmp
            break
          }
          case 'byHours': {
            input.byHours = position.byHours
            break
          }
        }
        this.$apollo.mutate({
          mutation: updateOccupation,
          variables: {
            input: input
          }
        }).then(({data}) => {
          if (data.updateOccupation.occupation) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Обновлено успешно'
            })
          }
        })
      },
      clearFilters () {
        this.appliedFilters = {
          company: [],
          position: []
        }
        this.pagination = {
          rowsPerPage: 10,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'user'
        }
      }
    },
    computed: {
      selectedRows: {
        get: function () {
          return this.selectedRowsData
        },
        set: function (newRows) {
          this.selectedRowsData = newRows.filter(item => !item.fireDate)
        }
      },
      getAll () {
        return !this.user
      },
      headers () {
        const headers = [
          {text: 'Компания', value: 'company', sortable: this.getAll, align: 'left', filter: this.getAll},
          {text: 'Должность', value: 'position', sortable: this.getAll, align: 'left', filter: this.getAll},
          {text: 'Дата приёма', value: 'hireDate', sortable: this.getAll, align: 'center'},
          {text: 'Дата увольнения', value: 'fireDate', sortable: this.getAll, align: 'center'},
          {text: 'Ставка', value: 'salary', sortable: this.getAll, align: 'center'},
          {text: 'База', value: 'base', sortable: this.getAll, align: 'center'},
          {text: 'Аванс', value: 'advance', sortable: this.getAll, align: 'center'},
          {text: 'Почасовая', value: 'byHours', sortable: this.getAll, align: 'center'}
        ]
        if (this.getAll) {
          headers.splice(0, 0, {text: 'Сотрудник', value: 'user', sortable: this.getAll, align: 'left'})
        }
        return headers
      },
      filterPositions () {
        if (this.appliedFilters.company) {
          const item = this.companies.find(val => val.id === this.appliedFilters.company)
          return item ? item.positions : []
        } else {
          return []
        }
      }
    },
    watch: {
      searchQuery: function () {
        this.searchOperation()
      },
      appliedFilters: {
        handler: function (newVal) {
          this.$apollo.queries.positionsPagedData.refetch()
          this.storeValue('filters', newVal)
        },
        deep: true
      },
      pagination: {
        handler: function (newVal) {
          this.storeValue('pagination', newVal)
        },
        deep: true
      }
    }
  }
</script>

<style>
  .filter-padding {
    padding-left: 40px;
    padding-right: 40px
  }
</style>
