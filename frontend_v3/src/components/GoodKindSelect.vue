<template>
  <div>
    <v-select
      :label="label"
      :required="required"
      :multiple="multiple"
      :disabled="disabled"
      :clearable="clearable"
      :readonly="readonly"
      :hide-details="hideDetails"
      autocomplete
      :search-input.sync="searchQuery"
      :rules="nonEmptyArrayField"
      v-model="goodKinds"
      :items="allGoodKindsData"
      :loading="loadingQueriesCount > 0 ? 'loading' : false"
      item-text="selectText"
      item-value="id"
    >
      <template slot="no-data">
        <span class="px-3 subheading">Ни одного вида товара не найдено.
          <v-btn @click="creationMenu = true" v-if="auth.hasPermission('warehouse.add_goodkind') && !readOnlyGoodKind">Создать новый</v-btn>
        </span>
      </template>
    </v-select>
    <v-dialog v-model="creationMenu" persistent scrollable lazy max-width="700px">
      <create-good-kind @closeDialog="closeDialog" @selectGoodKind="selectGoodKind"/>
    </v-dialog>
  </div>
</template>

<script>
  import CreateGoodKind from './CreateGoodKind'
  import {goodKinds} from './storage/query'
  import auth from '../auth/auth'
  import _ from 'lodash'

  export default {
    name: 'GoodKindSelect',
    components: {
      CreateGoodKind
    },
    props: {
      value: null,
      label: {
        type: String,
        default: 'Вид товара'
      },
      multiple: Boolean,
      required: Boolean,
      readonly: Boolean,
      clearable: Boolean,
      hideDetails: Boolean,
      disabled: Boolean,
      readOnlyGoodKind: Boolean,
      checked: Boolean
    },
    data () {
      return {
        goodKinds: [],
        allGoodKindsData: [],
        searchQuery: null,
        searchText: null,
        searchGoodKind: null,
        creationMenu: false,
        nonEmptyArrayField: [
          array => {
            if (this.required) {
              if (array && Array.isArray(array)) {
                return (array.length > 0 && array.each(item => item > 0)) || 'Поле не может быть пустым'
              } else {
                return (!!array && array > 0) || 'Поле не может быть пустым'
              }
            } else {
              return true
            }
          }
        ],
        auth: auth,
        loadingQueriesCount: 0
      }
    },
    mounted: function () {
      this.assignProduct(this.value)
    },
    apollo: {
      query: {
        query: goodKinds,
        variables () {
          return {
            search: this.searchText,
            require: this.requiredGoodKind,
            checked: this.checked
          }
        },
        update (data) {
          data.allGoodKinds.forEach(item => {
            if (this.allGoodKindsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allGoodKindsData.push(item)
            }
            if (!this.multiple) {
              if (item.id === this.goodKinds) {
                this.$emit('goodKindText', this.getSelectText(item))
                this.$emit('mass', item.mass)
                this.$emit('allDataGoodKind', item)
              }
            }
          })
          this.allGoodKindsData.forEach(item => {
            item.selectText = this.getSelectText(item)
          })
          if (this.allGoodKindsData.length <= 0) {
            this.allGoodKindsData.push({
              id: -1,
              selectText: ''
            })
          }
        },
        fetchPolicy: 'cache-and-network',
        loadingKey: 'loadingQueriesCount'
      }
    },
    methods: {
      // Собираем отображаемый текст
      getSelectText (goodKind) {
        let code = goodKind.code ? goodKind.code : 'б/а'
        return code + ' - ' + goodKind.name + ' (' + goodKind.manufacturer.name + ')'
      },
      // Закрываем диалог
      closeDialog () {
        this.creationMenu = false
      },
      selectGoodKind (val) {
        this.goodKinds = val
      },
      assignProduct (val) {
        if (val) {
          this.goodKinds = val
          if (this.multiple) {
            if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
              this.goodKinds = this.goodKinds.map(item => item.id)
            }
          } else {
            if (typeof val === 'object') {
              this.goodKinds = this.goodKinds.id
            }
          }
        }
      },
      clearMethod () {
        this.goodKinds = null
      },
      searchOperation: _.debounce(function () {
        this.searchText = this.searchQuery
      }, 500)
    },
    computed: {
      requiredGoodKind: function () {
        let goodKinds = []
        if (this.goodKinds) {
          goodKinds = Array.isArray(this.goodKinds) ? this.goodKinds : [this.goodKinds]
        }
        const notLoaded = goodKinds.filter(goodKind => {
          return this.allGoodKindsData.findIndex(item => item.id === Number(goodKind)) < 0
        })
        if (notLoaded.length > 0) {
          return notLoaded
        }
        return null
      }
    },
    watch: {
      value: function (val) {
        this.assignProduct(val)
      },
      goodKinds: function (val) {
        this.$emit('input', val)
      },
      searchQuery: function () {
        this.searchOperation()
      }
    }
  }
</script>
