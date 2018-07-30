<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="headline">Финансовая информация</span>
        <v-icon class="mx-2">mdi-arrow-right</v-icon>
        <router-link :to="{name: 'financial_info_history'}" style="color: rgba(0,0,0,.54)">
          <span class="headline">История изменений</span>
        </router-link>
        <v-spacer/>
        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="pb-4">
            <v-flex xs11 class="filter-padding">
              <v-select
                class="pr-3"
                label="Основные компании"
                :items="companies"
                item-text="name"
                item-value="id"
                v-model="filters.companies"
                hide-details
                multiple
                clearable
              />
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <v-select
                class="pr-3"
                label="Должности"
                :items="positions"
                item-text="name"
                item-value="id"
                v-model="filters.positions"
                hide-details
                multiple
                clearable
              />
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field append-icon="search" label="Поиск по сотруднику" single-line hide-details
                      v-model="searchQuery" style="max-width: 25%"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table :headers="headers"
                  no-data-text="Нет доступных данных"
                  no-results-text="Нет данных, удовлетворяющих запросу"
                  rows-per-page-text="Строк на странице"
                  :items="pagedOccupations.occupations"
                  :loading="loadingQueriesCount > 0 ? 'loading' : false"
                  :rows-per-page-items="rpp"
                  :pagination.sync="pagination"
                  must-sort
                  :total-items="pagedOccupations.totalCount"
    >
      <template slot="items" slot-scope="props">
        <tr :class="{'inner-span-cursor': auth.hasPermission('users.change_occupation'), fired: props.item.user.fired}">
          <td>{{ props.item.user.shortName }}</td>
          <td>{{ props.item.mainCompany.client.name }}</td>
          <td v-html="props.item.user.positions.join('<br/>')"></td>
          <td class="text-xs-center">
            <span @click="openEditDialog($event, props.item, 'salary')">
              {{ combineSalaryLabel(props.item) }}
            </span>
          </td>
          <td class="text-xs-center">
            <span @click="openEditDialog($event, props.item, 'base')">
              {{ formatMoney(props.item.base) }} &#8381;
            </span>
          </td>
          <td class="text-xs-center">
            <span @click="openEditDialog($event, props.item, 'advance')">
              {{ formatMoney(props.item.advance) }} &#8381;
            </span>
          </td>
          <td class="text-xs-center">
            <span @click="openEditDialog($event, props.item, 'fixedHour')">
              {{ props.item.fixedHour === null ? 'нет' : formatMoney(props.item.fixedHour) + ' &#8381;' }}
            </span>
          </td>
          <td class="text-xs-center">
            <span @click="openEditDialog($event, props.item, 'transportation')">
              {{ props.item.transportation === 0 ? 'нет' : formatMoney(props.item.transportation) + ' &#8381;' }}
            </span>
          </td>
          <td class="text-xs-center">
            <v-checkbox v-if="auth.hasPermission('users.change_occupation')"
                        hide-details v-model="props.item.byHours"
                        @change="savePosition(null, props.item, 'byHours')"/>
            <v-icon v-else>{{ (props.item.byHours ? 'check_box' : 'check_box_outline_blank') }}</v-icon>
          </td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <v-menu offset-y absolute :close-on-content-click="false" max-width="450px"
            :position-x="editDialogX" :position-y="editDialogY" v-model="editDialog">
      <v-list v-if="auth.hasPermission('users.change_occupation')" class="px-3">
        <v-layout row wrap justify-space-between v-if="dialogContentType === 'salary'">
          <v-flex xs6>
            <integer-field label="Ставка, руб" v-model="editedItem.salary" ref="autofocus"/>
          </v-flex>
          <v-spacer/>
          <v-flex xs5>
            <integer-field label="Ставка, %" v-model="editedItem.fraction"/>
          </v-flex>
          <v-flex xs12 class="mb-2">
            <span>Для расчёта по коэффициентам оставьте поле ставки пустым</span>
          </v-flex>
        </v-layout>
        <integer-field label="База, руб" v-if="dialogContentType === 'base'" ref="autofocus"
                       v-model="editedItem.base"/>
        <integer-field label="Аванс, руб" v-if="dialogContentType === 'advance'" ref="autofocus"
                       v-model="editedItem.advance"/>
        <integer-field label="Фиксированный час, руб" v-if="dialogContentType === 'fixedHour'" ref="autofocus"
                       v-model="editedItem.fixedHour"/>
        <integer-field label="Проезд до офиса, руб" v-if="dialogContentType === 'transportation'" ref="autofocus"
                       v-model="editedItem.transportation"/>
        <v-layout>
          <v-spacer/>
          <v-btn @click="closeEditDialog" :disabled="loading">Отменить</v-btn>
          <v-btn @click="savePosition" color="submit" :loading="loading" :disabled="loading">Сохранить</v-btn>
        </v-layout>
      </v-list>
    </v-menu>
  </v-card>
</template>

<script>
  import HeaderFilter from '../HeaderFilter'
  import IntegerField from '../IntegerField'
  import {tableQuery, allCompanies, updateOccupation} from './query'
  import utilsMixin from '../utils'
  import _ from 'lodash'
  import auth from '../../auth/auth'

  export default {
    name: 'financial-info',
    components: {
      HeaderFilter,
      IntegerField
    },
    metaInfo: {
      title: 'Финансовая информация сотрудников'
    },
    mixins: [
      utilsMixin
    ],
    apollo: {
      pagedOccupations: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
        variables () {
          return {
            input: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              sortBy: this.pagination.sortBy,
              search: this.searchText
            },
            filters: {
              companies: this.filters.companies,
              positions: this.filters.positions
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update ({pagedOccupations}) {
          return JSON.parse(JSON.stringify(pagedOccupations))
        }
      },
      query: {
        fetchPolicy: 'cache-and-network',
        query: allCompanies,
        update ({companies}) {
          this.companies = []
          this.positions = []
          companies.forEach(company => {
            this.companies.push({
              id: company.id,
              name: company.client.name
            })
            if (company.positionSet) {
              company.positionSet.forEach(position => {
                this.positions.push({
                  id: position.id,
                  name: `${company.shortName} - ${position.name}`
                })
              })
            }
          })
          return null
        }
      }
    },
    data () {
      return {
        rpp: [25, 50],
        loadingQueriesCount: 0,
        pagedOccupations: {
          totalCount: 0,
          occupations: []
        },
        companies: [],
        positions: [],
        searchText: '',
        searchQuery: '',
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'user'
        }),
        filters: this.getValue('filters', {
          companies: null,
          positions: null
        }),
        headers: [
          {text: 'Имя', value: 'user', align: 'left'},
          {text: 'Основная компания', value: 'mainCompany', align: 'left'},
          {text: 'Должности', value: 'positions', align: 'left'},
          {text: 'Зарплата', value: 'salary', align: 'center'},
          {text: 'База', value: 'base', align: 'center'},
          {text: 'Аванс', value: 'advance', align: 'center'},
          {text: 'Фиксированный час', value: 'fixedHour', align: 'center'},
          {text: 'Проезд', value: 'transportation', align: 'center'},
          {text: 'Почасовая', value: 'byHours', align: 'center'}
        ],
        auth: auth,
        tmp: null,
        tmp2: null,
        editDialog: false,
        editDialogX: null,
        editDialogY: null,
        dialogContentType: null,
        editedItem: null,
        loading: false
      }
    },
    methods: {
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchQuery = this.searchQuery.trim()
        this.searchText = this.searchQuery
      }, 500),
      clearFilters () {
        this.filters = {
          companies: null,
          positions: null
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'user'
        }
      },
      combineSalaryLabel (item) {
        if (item.salary === null) {
          return 'По коэффициентам'
        } else {
          return `${this.formatMoney(item.salary)} \u20BD (${item.fraction}%)`
        }
      },
      openEditDialog (event, item, type) {
        if (!this.auth.hasPermission('users.change_occupation') || this.editDialog) {
          return
        }
        this.editedItem = JSON.parse(JSON.stringify(item))
        this.dialogContentType = type

        this.editDialogX = event.clientX
        this.editDialogY = event.clientY
        this.editDialog = true

        setTimeout(() => {
          this.$refs.autofocus.focus()
        }, 200)
      },
      closeEditDialog () {
        if (!this.loading) {
          this.editDialog = false
          setTimeout(() => {
            this.dialogContentType = null
            this.editedItem = null
          }, 300)
        }
      },
      savePosition (event, item, type) {
        item = item || this.editedItem
        type = type || this.dialogContentType

        const input = {
          occupationId: item.id
        }
        switch (type) {
          case 'salary': {
            input.salary = item.salary
            input.fraction = item.fraction
            break
          }
          case 'advance': {
            input.advance = item.advance
            break
          }
          case 'base': {
            input.base = item.base
            break
          }
          case 'byHours': {
            input.byHours = item.byHours
            break
          }
          case 'fixedHour': {
            input.fixedHour = item.fixedHour
            break
          }
          case 'transportation': {
            input.transportation = item.transportation === null ? 0 : item.transportation
            break
          }
        }
        this.loading = true
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
            this.loading = false
            this.closeEditDialog()
          }
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      filters: {
        handler: function (val) {
          this.storeValue('filters', val)
          this.pagination.page = 1
        },
        deep: true
      },
      editDialog (newVal) {
        if (!newVal) {
          this.closeEditDialog()
        }
      },
      searchQuery: function () {
        this.searchOperation()
      }
    }
  }
</script>

<style>
  .inner-span-cursor td > span {
    cursor: pointer;
  }
</style>
