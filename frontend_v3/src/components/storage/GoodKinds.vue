<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Виды товаров</span>
        <v-spacer/>

        <header-filter @clearFilters="clearFilters">
          <v-layout row wrap justify-center>
            <v-flex xs11 class="filter-padding">
              <manufacturer-select hide-details clearable v-model="manufacturerId" multiple
                                   class="pr-2"/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <good-groups-select hide-details v-model="groupsId" multiple clearable autocomplete class="pr-2"/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <div class="mt-3" style="width: 165px;">
                <v-checkbox label="Только новые" v-model="onlyNew"/>
              </div>
            </v-flex>
          </v-layout>
        </header-filter>

        <v-text-field class="pr-3"
                      label="Поиск"
                      append-icon="search"
                      v-model="searchQuery"
        />
        <v-dialog v-model="createDialog" persistent scrollable lazy max-width="700px">
          <v-btn color="primary" slot="activator" v-show="hasPermCreateGoodKind">Создать</v-btn>
          <create-good-kind @closeDialog="createDialog = false" @selectGoodKind="created"/>
        </v-dialog>
        <v-dialog v-model="updateDialog" persistent scrollable lazy max-width="700px">
          <create-good-kind :updateDialog="updateDialog" :getGoodKind="goodKind" @closeDialog="updateDialog = false"
                            @updated="updated" @deleted="deleted" @confirm="confirm"/>
        </v-dialog>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      must-sort
      :pagination.sync="pagination"
      :headers="headers"
      :items="allGoodKindsData.goodKinds"
      :total-items="allGoodKindsData.totalCount"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      :rows-per-page-items="rpp"
      :rows-per-page-text="'Строк на странице'"
      :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr @click="openUpdateDialog(props.item)" :class="{ new: props.item.new}">
          <td>{{ props.item.code ? props.item.code: 'б/а' }}</td>
          <td>{{ props.item.name }}</td>
          <td class="text-xs-center">{{ props.item.manufacturer.name }}</td>
          <td class="text-xs-center" v-html="props.item.gosts.join(',<br/>')"></td>
          <td class="text-xs-center">{{ props.item.mass }}</td>
          <td class="text-xs-center">{{ props.item.confirmed ? props.item.confirmed.shortName : '' }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {pagedGoodKinds} from './query'
  import utilMixin from '../utils'
  import _ from 'lodash'
  import auth from '../../auth/auth'
  import CreateGoodKind from '../CreateGoodKind'
  import HeaderFilter from '../HeaderFilter'
  import ManufacturerSelect from '../ManufacturerSelect'
  import GoodGroupsSelect from '../GoodGroupsSelect'

  export default {
    name: 'good-kinds',
    components: {
      CreateGoodKind,
      HeaderFilter,
      ManufacturerSelect,
      GoodGroupsSelect
    },
    metaInfo: {
      title: 'Виды товаров'
    },
    mixins: [utilMixin],
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: pagedGoodKinds,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              sortBy: this.pagination.sortBy,
              search: this.searchText
            },
            filters: {
              manufacturerId: this.manufacturerId,
              groupsId: this.groupsId,
              onlyNew: this.onlyNew
            }
          }
        },
        update (data) {
          this.allGoodKindsData = data.pagedGoodKinds
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        auth: auth,
        createDialog: false,
        updateDialog: false,
        allGoodKindsData: [],
        hasPermCreateGoodKind: auth.hasPermission('warehouse.add_goodkind'),
        headers: [
          {text: 'Артикул', align: 'left', value: 'code'},
          {text: 'Наименование', align: 'center', value: 'name'},
          {text: 'Производитель', align: 'center', value: 'manufacturer'},
          {
            text: 'Тип, марка, обозначение документа, опросного листа',
            align: 'center',
            value: 'gosts',
            sortable: false
          },
          {text: 'Масса', align: 'center', value: 'mass', sortable: false},
          {text: 'Подтвержден', align: 'center', value: 'confirmed', sortable: false}
        ],
        pagination: this.getValue('pagination', {
          rowsPerPage: 10,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'code'
        }),
        searchText: this.getValue('searchGoodKinds', ''),
        searchQuery: this.getValue('searchGoodKinds', ''),
        onlyNew: this.getValue('onlyNewGoodKinds', false),
        manufacturerId: [],
        groupsId: [],
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0,
        goodKind: null
      }
    },
    watch: {
      groupsId: {
        handler: function () {
          this.pagination.page = 1
        }
      },
      manufacturerId: {
        handler: function () {
          this.pagination.page = 1
        }
      },
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchGoodKinds', val)
        }
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      onlyNew: function (val) {
        this.storeValue('onlyNewGoodKinds', val)
        this.pagination.page = 1
      }
    },
    methods: {
      clearFilters () {
        this.manufacturerId = []
        this.onlyNew = false
        this.pagination = {
          rowsPerPage: 25,
          descending: false,
          page: 1,
          totalItems: 0,
          sortBy: 'code'
        }
      },
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      created () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Вид товара создан'
        })
        this.$apollo.queries.query.refetch()
      },
      updated () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Вид товара обновлен'
        })
        this.$apollo.queries.query.refetch()
      },
      deleted () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Вид товара удален'
        })
        this.$apollo.queries.query.refetch()
      },
      confirm () {
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Вид товара подтвержден'
        })
        this.$apollo.queries.query.refetch()
      },
      openUpdateDialog (goodKind) {
        if (auth.hasPermission('warehouse.change_goodkind')) {
          this.goodKind = {}
          this.goodKind.id = goodKind.id
          this.goodKind.code = goodKind.code
          this.goodKind.name = goodKind.name
          this.goodKind.manufacturerName = goodKind.manufacturer.name
          this.goodKind.mass = goodKind.mass
          this.goodKind.goodGroupId = goodKind.goodGroup ? goodKind.goodGroup.id : []
          this.goodKind.analogs = goodKind.analogs ? goodKind.analogs.map(item => item.id) : []
          this.goodKind.gosts = goodKind.gosts ? goodKind.gosts : []
          this.goodKind.new = goodKind.new
          this.goodKind.defaultUnit = goodKind.defaultUnit
          this.updateDialog = true
        }
      }
    }
  }
</script>
