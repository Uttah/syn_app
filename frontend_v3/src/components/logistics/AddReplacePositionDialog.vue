<template>
  <div>
    <v-dialog v-model="dialogConfirm" max-width="500px">
      <v-card>
        <v-card-text>
          <span v-if="!replacePosition">Вы действительно хотите добавить позицию?</span>
          <span v-if="replacePosition">Вы действительно хотите заменить позицию?</span>
          <v-form v-model="commentFormValid">
            <v-text-field v-if="replacePosition" label="Комментарий" v-model="comment" textarea :rules="nonEmptyField"/>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="dialogConfirm=false">Отмена</v-btn>
          <v-btn flat v-if="!replacePosition" @click="addPositionInLogisticsRequestFunc">Добавить</v-btn>
          <v-btn flat v-if="replacePosition" :disabled="!commentFormValid" @click="replacePositionInLogisticsRequestFunc">Заменить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog" max-width="1000px">
      <v-card>
        <v-card-title>
          <span v-if="!replacePosition" class="title">Добавление товара в заявку</span>
          <span v-if="replacePosition" class="title">Замена товара в заявке</span>
          <v-spacer/>
          <v-btn icon @click="dialog=false">
            <v-icon>close</v-icon>
          </v-btn>
          <v-form style="width: 100%" ref="form" v-model="formValid">
            <v-layout wrap>
              <v-flex xs4 class="pl-3 pr-3">
                <float-field label="Необходимое количество" v-model="input.count" :rules="nonEmptyField"/>
              </v-flex>
              <v-flex xs4 class="pl-3">
                <v-select
                  label="Единица измерения"
                  v-model="input.unitId"
                  :items="allUnitsData"
                  item-text="name"
                  item-value="id"
                  clearable
                  :rules="nonEmptyField"
                />
              </v-flex>
              <v-flex xs4 class="pl-3 pr-3">
                <date-picker label="Необходимая дата поставки" v-model="input.deadline" :rules="nonEmptyField"/>
              </v-flex>
            </v-layout>
          </v-form>
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
            <tr @click="selectGoodKind(props.item)" :class="{ new: props.item.new}">
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
    </v-dialog>
  </div>
</template>

<script>
  import {pagedGoodKinds, units} from '../storage/query'
  import {addPositionInLogisticsRequest, replacePositionInLogisticsRequest} from './query'
  import _ from 'lodash'
  import utilMixin from '../utils'
  import HeaderFilter from '../HeaderFilter'
  import ManufacturerSelect from '../ManufacturerSelect'
  import GoodGroupsSelect from '../GoodGroupsSelect'
  import FloatField from '../FloatField'
  import IntegerField from '../IntegerField'
  import DatePicker from '../DatePicker'

  export default {
    name: 'add-replace-position-dialog',
    props: [
      'value',
      'requestId',
      'replacePosition'
    ],
    components: {
      DatePicker,
      IntegerField,
      FloatField,
      HeaderFilter,
      ManufacturerSelect,
      GoodGroupsSelect
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
      },
      allUnitsData: {
        fetchPolicy: 'cache-and-network',
        query: units
      }
    },
    data () {
      return {
        dialog: false,
        dialogConfirm: false,
        formValid: false,
        allGoodKindsData: [],
        allUnitsData: [],
        commentFormValid: false,
        input: {
          requestId: this.requestId,
          goodKindId: null,
          count: null,
          unitId: null,
          deadline: null
        },
        comment: null,
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
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    watch: {
      value: function (val) {
        this.dialog = val
      },
      dialog: function (val) {
        this.$emit('input', val)
      },
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
      addPositionInLogisticsRequestFunc () {
        this.input.requestId = this.requestId
        delete this.input.comment
        delete this.input.positionId
        this.$apollo.mutate({
          mutation: addPositionInLogisticsRequest,
          variables: {
            input: this.input
          }
        }).then(({data}) => {
          if (data.addPositionInLogisticsRequest.result) {
            this.dialog = false
            this.dialogConfirm = false
            this.$emit('addPositionInLogisticsRequestSuccess')
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Позиция добавлена в заявку на закупку'
            })
          }
        })
      },
      replacePositionInLogisticsRequestFunc () {
        delete this.input.requestId
        this.input.positionId = Number(this.replacePosition.id)
        this.input.comment = this.comment
        this.$apollo.mutate({
          mutation: replacePositionInLogisticsRequest,
          variables: {
            input: this.input
          }
        }).then(({data}) => {
          if (data.replacePositionInLogisticsRequest.result) {
            this.dialog = false
            this.dialogConfirm = false
            this.$emit('addPositionInLogisticsRequestSuccess')
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Позиция заменена'
            })
          }
        })
      },
      selectGoodKind (item) {
        this.$refs.form.validate()
        this.input.goodKindId = item.id
        if (this.formValid) {
          this.dialogConfirm = true
        }
      },
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
      }, 500)
    }
  }
</script>

<style scoped>

</style>
