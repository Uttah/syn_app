<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span class="ma-0 headline">Склад</span>
        <v-spacer/>
        <header-filter class="pt-4" @clearFilters="clearFilters">
          <v-layout row wrap justify-center class="mt-3 pb-4">
            <v-flex xs11>
              <storage-select v-model="goodsFilter.storage" class="pr-2" hide-details clearable/>
            </v-flex>
            <v-flex xs11>
             <manufacturer-select v-model="goodsFilter.manufacturer" hide-details clearable class="pr-2"/>
            </v-flex>
            <v-flex xs11>
              <workers-select label="Ответственный" v-model="goodsFilter.responsible" class="pr-2" clearable hide-details/>
            </v-flex>
            <v-flex xs11>
              <projects-select label="Проект" v-model="goodsFilter.project" class="pr-2" clearable hide-details/>
            </v-flex>
            <v-flex xs11>
              <float-field label="Количество" v-model="goodsFilter.quantity" class="pr-2" hide-details/>
              <v-radio-group v-model="goodsFilter.quantityType">
                <v-radio label="Равно" value="equal"/>
                <v-radio label="Больше или равно" value="gte"/>
                <v-radio label="Меньше или равно" value="lte"/>
              </v-radio-group>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field
          label="Поиск (артикул, наименование, производитель)"
          append-icon="search"
          v-model="searchQuery"
          hide-details
        />
        <create-storage-item-dialog @created="created"/>
        <update-storage-item-dialog v-model="updDialog" :itemGood="itemGood" @updated="updated"
                                    @deleted="deleted"/>
      </v-toolbar>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="pagedGoods.goods"
      :total-items="pagedGoods.totalCount"
      :pagination.sync="pagination"
      :rows-per-page-items="rpp"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      rows-per-page-text="Строк на странице"
      no-data-text="Нет доступных данных"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr v-for="(row, i) in props.item.subRows" :class="{ target: props.item.goodKind.id === hoverItem }" class="tableLine trClass" style="height: 50px;"
            @click="updateDialog(row, props.item.goodKind)" @mouseover="tableHover(row, props.item.goodKind)">
          <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.goodGroup ? props.item.goodKind.goodGroup.name : '' }}</td><!--Группа товара-->
          <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.code ? props.item.goodKind.code : 'б/а' }}</td><!--Артикул-->
          <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.defect ? row.goodKind.name + ' (нек.)' : props.item.goodKind.name }}</td><!--Наименование-->
          <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.manufacturer.name }}</td><!--Приизводитель-->
          <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}" class="text-xs-left tdClass">
            <v-layout style="display: table;">
              <v-flex>
                <v-btn class="showBtn"
                       v-show="auth.hasPermission('warehouse.change_location')"
                       icon
                       @click.native.stop="openDialog(props.item.goodKind, row)"
                       title="Переместить"
                >
                  <v-icon>launch</v-icon>
                </v-btn>
              </v-flex>
              <v-flex style="display:table-cell!important; vertical-align:middle;">
                <span>{{ row.count }} {{row.unit.shortName}}</span><span v-if="row.defect"> (нек.)</span>
              </v-flex>
              <v-spacer/>
            </v-layout>
          </td><!--Количество-->
          <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">{{ row.location.name }}</td><!--Местонахождение-->
          <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">{{ row.responsible.shortName }}</td><!--Ответственный-->
          <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">{{ row.project ? pad(row.project.number, 5) : '' }}</td><!--Проект-->
          <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}" style="width: 50px; padding: 0;" class="pr-2">
            <v-btn v-show="row.note || hoverBtn(row.id)"
                   icon flat
                   @click.stop="openCommentDialog(row.note)"
                   title="Комментарий"
            >
              <v-icon>textsms</v-icon>
            </v-btn>
          </td><!--Примечание-->
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
    <move-dialog ref="moveDialog" @success="success"/>
    <comments-dialog ref="commentDialog"/>
  </v-card>
</template>

<script>
  import {tableQuery} from './query'
  import utilMixin from '../utils'
  import _ from 'lodash'
  import auth from '../../auth/auth'
  import CreateStorageItemDialog from './CreateStorageItemDialog.vue'
  import ManufacturerSelect from '../ManufacturerSelect'
  import UpdateStorageItemDialog from './UpdateStorageItemDialog'
  import MoveDialog from './MoveDialog'
  import StorageSelect from '../StorageSelect'
  import CommentsDialog from './CommentsDialog'
  import HeaderFilter from '../HeaderFilter'
  import WorkersSelect from '../WorkersSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import FloatField from '../FloatField'

  export default {
    name: 'storage',
    metaInfo: {
      title: 'Склад'
    },
    mixins: [utilMixin],
    components: {
      FloatField,
      ProjectsSelect,
      WorkersSelect,
      UpdateStorageItemDialog,
      CreateStorageItemDialog,
      ManufacturerSelect,
      MoveDialog,
      StorageSelect,
      CommentsDialog,
      HeaderFilter
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: tableQuery,
        variables () {
          return {
            paged: {
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              first: this.pagination.rowsPerPage,
              sortBy: this.pagination.sortBy,
              desc: this.pagination.descending,
              search: this.searchText
            },
            filters: {
              storage: Array.isArray(this.goodsFilter.storage) && this.goodsFilter.storage.length === 0 ? null : this.goodsFilter.storage,
              manufacturer: Array.isArray(this.goodsFilter.manufacturer) && this.goodsFilter.manufacturer.length === 0 ? null : this.goodsFilter.manufacturer,
              responsible: this.goodsFilter.responsible,
              project: Array.isArray(this.goodsFilter.project) && this.goodsFilter.project.length === 0 ? null : this.goodsFilter.project,
              quantity: this.goodsFilter.quantity,
              quantityType: this.goodsFilter.quantityType
            }
          }
        },
        update (data) {
          this.pagedGoods = data.pagedGoods
        },
        loadingKey: 'loadingQueriesCount'
      }
    },
    data () {
      return {
        pagedGoods: [],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'code'
        }),
        searchText: this.getValue('searchStorage', ''),
        searchQuery: this.getValue('searchStorage', ''),
        goodsFilter: this.getValue('filters', {
          manufacturer: [],
          storage: [],
          responsible: null,
          project: [],
          quantity: null,
          quantityType: null
        }),
        headers: [
          {text: 'Группа товаров', align: 'center', sortable: true, value: 'goodGroup'},
          {text: 'Артикул', align: 'center', sortable: true, value: 'code'},
          {text: 'Наименование', align: 'center', value: 'name'},
          {text: 'Производитель', align: 'center', value: 'manufacturer'},
          {text: 'Количество', align: 'center', sortable: false, value: 'count'},
          {text: 'Местонахождение', align: 'center', sortable: false, value: 'warehouse'},
          {text: 'Ответственный', align: 'center', sortable: false, value: 'responsible'},
          {text: 'Проект', align: 'center', sortable: false, value: 'project'},
          {text: ' ', align: 'center', sortable: false, value: 'note'}
        ],
        rpp: [
          25, 50, 100
        ],
        loadingQueriesCount: 0,
        itemGood: {
          count: null,
          unitId: null,
          note: null,
          goodKindId: null,
          locationId: null,
          defect: false,
          projectId: null,
          responsibleId: null
        },
        updDialog: false,
        hoverItem: null,
        hoverItemColor: null,
        auth: auth
      }
    },
    methods: {
      openCommentDialog (val) {
        this.$refs.commentDialog.openDialog(val)
      },
      // При создании нового товара Обновление таблицы
      created () {
        this.$apollo.queries.query.refetch()
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Товар принят'
        })
      },
      updated () {
        this.$apollo.queries.query.refetch()
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Товар обновлен'
        })
      },
      deleted () {
        this.$apollo.queries.query.refetch()
        this.$notify({
          group: 'commonNotification',
          duration: 5000,
          text: 'Товар удален'
        })
      },
      // Изменение поля Поиска с задержкой
      searchOperation: _.debounce(function () {
        this.pagination.page = 1
        this.searchText = this.searchQuery
      }, 500),
      updateDialog (subRow, goodKind) {
        this.itemGood.id = subRow.id
        this.itemGood.count = subRow.count
        this.itemGood.defect = subRow.defect
        this.itemGood.goodKindId = goodKind.id
        this.itemGood.note = subRow.note
        this.itemGood.unitId = subRow.unit.id
        this.itemGood.locationId = subRow.location.id
        this.itemGood.projectId = subRow.project ? subRow.project.id : []
        this.itemGood.responsibleId = subRow.responsible.id
        this.updDialog = true
      },
      tableHover (val, val2) {
        this.hoverItem = val.id
        this.hoverItemColor = val2.id
      },
      hoverBtn (val) {
        return val === this.hoverItem
      },
      success () {
        this.updated()
      },
      openDialog (goodKind, subRow) {
        this.$refs.moveDialog.openDialog(goodKind, subRow)
      },
      clearFilters () {
        this.goodsFilter = {
          manufacturer: [],
          storage: [],
          responsible: null,
          project: [],
          quantity: null,
          quantityType: null
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'code'
        }
      }
    },
    watch: {
      // Изменение поля Поиска
      searchQuery: {
        handler: function (val) {
          this.searchOperation()
          this.storeValue('searchStorage', val)
        }
      },
      goodsFilter: {
        handler: function (val) {
          this.$apollo.queries.query.refetch()
          this.storeValue('filters', val)
          this.pagination.page = 1
        },
        deep: true
      },
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      'goodsFilter.quantity': function (val) {
        if (val && !this.goodsFilter.quantityType) {
          this.goodsFilter.quantityType = 'equal'
        }
        if (!val && this.goodsFilter.quantityType) {
          this.goodsFilter.quantityType = null
        }
      }
    }
  }
</script>

<style scoped>
  .tableLine td {
    width: 250px;
    max-width: 250px;
    word-wrap: break-word;
  }
  .showBtn {
    visibility: hidden;
  }
  button {
    transition-delay: 0ms;
    transition-duration: 0ms;
  }
  .trClass:hover .tdClass .showBtn {
    visibility: visible;
  }
</style>
