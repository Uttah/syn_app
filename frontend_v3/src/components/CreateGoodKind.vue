<template>
  <div>
    <v-dialog v-model="sumPositionWarehouseDialog" persistent scrollable lazy max-width="700px">
      <v-card>
        <v-card-title>
        <span class="subheading">
          Совпадение артикулов
        </span>
        </v-card-title>
        <v-card-title>
          <div class="px-3">
            <div>Редактированный: {{ goodKind.code }} {{goodKind.name}} ({{goodKind.manufacturerName}})</div>
            <div>Совпадающий: {{ existingGoodKind }}</div>
          </div>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="sumPositionWarehouseDialog = false">Отмена</v-btn>
          <v-btn flat :loading="loading" @click.native="action='editable';updateGoodKindExsistCodeFunc()">Использовать
            редактированный
          </v-btn>
          <v-btn flat :loading="loading" @click.native="action='coincidental';updateGoodKindExsistCodeFunc()">
            Использовать совпадающий
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmDeleteDialog" persistent scrollable lazy max-width="700px">
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите удалить этот вид товара?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="confirmDeleteDialog = false">Отмена</v-btn>
          <v-btn flat :loading="loading" @click.native="deleteGoodKindFunc">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmUpdateDialog" persistent scrollable lazy max-width="700px">
      <v-card>
        <v-card-title>
        <span class="subheading">
          Вы действительно хотите обновить этот вид товара?
        </span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click.native="confirmUpdateDialog = false">Отмена</v-btn>
          <v-btn flat :loading="loading" @click.native="updateGoodKindFunc">Обновить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-card overflow-y>
      <v-card-text>
        <v-layout wrap justify-center>
          <v-flex xs4 class="pl-3">
            <v-text-field
              :disabled="checkbox"
              label="Артикул"
              :readonly="readonly"
              v-model="goodKind.code"
            />
          </v-flex>
          <v-flex xs3 class="pl-3">
            <v-checkbox
              class="mt-3"
              label="Без артикула"
              v-model="checkbox"
            />
          </v-flex>
          <v-spacer/>

          <v-flex xs3>
            <v-select
              class="pr-3"
              label="Ед. измерения"
              :items="allUnits"
              item-text="shortName"
              item-value="id"
              v-model="goodKind.defaultUnit"
              hide-details
              required
            />
          </v-flex>

          <v-flex xs6 class="px-3">
            <manufacturer-select v-model="goodKind.manufacturerName" required editable always-return-name/>
          </v-flex>
          <v-flex xs6 class="px-3">
            <good-groups-select v-model="goodKind.goodGroupId" clearable autocomplete/>
          </v-flex>
          <v-flex xs12 class="px-3">
            <v-select
              label="Аналоги"
              v-model="goodKind.analogs"
              item-text="selectText"
              item-value="id"
              autocomplete
              multiple
              clearable
              :items="allGoodKindsData"
              :search-input.sync="searchGoodKind"
              :loading="loadingQueriesCount > 0 ? 'loading' : false"
            />
          </v-flex>
          <v-flex xs12 class="px-3">
            <v-text-field
              label="Наименование"
              :readonly="readonly"
              v-model="goodKind.name"
              required
              :rules="nonEmptyField"
            />
          </v-flex>
          <v-flex xs12 class="px-3">
            <v-card>
              <v-card-title class="title">Спецификации</v-card-title>
              <v-card-text class="pt-0">
                <v-flex xs12 class="px-3">
                  <float-field
                    label="Масса 1 ед. в кг."
                    v-model="goodKind.mass"
                  />
                </v-flex>
                <v-flex xs12 class="px-3">
                  <g-o-s-t-picker
                    ref="gostPicker"
                    label="Тип, марка, обозначение документа, опросного листа"
                    v-model="goodKind.gosts"
                    multiple
                  />
                </v-flex>
              </v-card-text>
            </v-card>
          </v-flex>
        </v-layout>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog">Отмена</v-btn>
        <v-btn v-if="updateDialog && deleteBtn" flat @click="confirmDeleteDialog = true">Удалить</v-btn>
        <v-btn v-if="updateDialog" flat :disabled="notValid" @click="confirmUpdateDialog = true">Обновить</v-btn>
        <v-btn v-if="updateDialog && goodKind.new && auth.hasPermission('warehouse.can_moderate')" flat
               @click="confirmGoodKindFunc">Подтвердить вид товара
        </v-btn>
        <v-btn v-if="!updateDialog" flat :loading="loading" :disabled="notValid" @click="sendNewKind">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
  import ManufacturerSelect from './ManufacturerSelect'
  import {
    createGoodKind,
    manufacturers,
    goodKinds,
    updateGoodKind,
    deleteGoodKind,
    updateGoodKindExsistCode,
    confirmGoodKind,
    allUnits
  } from './storage/query'
  import GoodGroupsSelect from './GoodGroupsSelect'
  import auth from '../auth/auth'
  import FloatField from './FloatField'
  import GOSTPicker from './storage/GOSTPicker'

  export default {
    name: 'CreateGoodKind',
    components: {
      GOSTPicker,
      FloatField,
      GoodGroupsSelect,
      ManufacturerSelect
    },
    props: {
      readonly: Boolean,
      updateDialog: Boolean,
      getGoodKind: Object
    },
    apollo: {
      query: {
        query: goodKinds,
        variables () {
          return {
            search: this.searchGoodKind,
            require: this.requiredGoodKind
          }
        },
        update (data) {
          data.allGoodKinds.forEach(item => {
            if (this.allGoodKindsData.findIndex(i => i.id === item.id) === -1) {
              item = JSON.parse(JSON.stringify(item))
              this.allGoodKindsData.push(item)
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
      },
      allUnits: {
        query: allUnits,
        fetchPolicy: 'cache-and-network'
      }
    },
    data () {
      return {
        auth: auth,
        confirmUpdateDialog: false,
        confirmDeleteDialog: false,
        sumPositionWarehouseDialog: false,
        loading: false,
        checkbox: false,
        goodKind: this.assignExternalGoodKind(this.getGoodKind),
        existingGoodKind: null,
        action: null,
        allGoodKindsData: [],
        allUnits: [],
        searchGoodKind: null,
        loadingQueriesCount: 0,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    watch: {
      'goodKind.code': function (val) {
        if (val) {
          this.goodKind.code = val.trim()
        }
      },
      getGoodKind: {
        handler: function (goodKind) {
          this.goodKind = this.assignExternalGoodKind(goodKind)
        },
        deep: true
      }
    },
    methods: {
      getSelectText (goodKind) {
        let code = goodKind.code ? goodKind.code : 'б/а'
        return code + ' - ' + goodKind.name + ' (' + goodKind.manufacturer.name + ')'
      },
      // Создание нового вида товара
      sendNewKind () {
        setTimeout(() => {
          this.loading = true
          this.$apollo.mutate({
            mutation: createGoodKind,
            variables: {
              input: this.goodKind
            },
            update: (store, {data: {createGoodKind}}) => {
              // Обновляем кеш новым производителем (если он был добавлен)
              try {
                const query = {query: manufacturers}
                const data = store.readQuery(query)
                const manufacturer = createGoodKind.goodKind.manufacturer
                if (!data.allManufacturerData.some(item => item.id === manufacturer.id)) {
                  data.allManufacturerData.push(manufacturer)
                  query.data = data
                  store.writeQuery(query)
                }
              } catch (e) {
              }
              // Обновляем кеш новым видом товара
              try {
                const query = {query: goodKinds}
                const data = store.readQuery(query)
                data.allGoodKinds.push(createGoodKind.goodKind)
                query.data = data
                store.writeQuery(query)
              } catch (e) {
              }
            }
          }).then(({data}) => {
            // Указываем селекту на id нового элемента
            this.$emit('selectGoodKind', data.createGoodKind.goodKind.id)
            this.loading = false
            this.closeDialog()
          }).catch(() => {
            this.loading = false
          })
        }, 100)
      },
      updateGoodKindFunc () {
        if (typeof this.goodKind.defaultUnit === 'object') {
          this.goodKind.defaultUnit = this.goodKind.defaultUnit.id
        }
        this.goodKind.goodGroupId = !Array.isArray(this.goodKind.goodGroupId) ? this.goodKind.goodGroupId : null
        setTimeout(() => {
          this.loading = true
          this.$apollo.mutate({
            mutation: updateGoodKind,
            variables: {
              input: {
                id: this.goodKind.id,
                code: this.goodKind.code,
                name: this.goodKind.name,
                manufacturerName: this.goodKind.manufacturerName,
                goodGroupId: this.goodKind.goodGroupId,
                analogs: this.goodKind.analogs,
                mass: this.goodKind.mass,
                gosts: this.goodKind.gosts,
                defaultUnit: this.goodKind.defaultUnit
              }
            }
          }).then(({data}) => {
            this.loading = false
            if (data.updateGoodKind.goodKind.id) {
              this.closeDialog()
              this.$emit('updated')
            }
          }).catch((error) => {
            if (error.message.indexOf('Производитель уже имеет такой артикул') !== -1) {
              this.confirmUpdateDialog = false
              this.existingGoodKind = error.message.slice(error.message.indexOf('(') + 1, error.message.indexOf(')') + 1)
              this.sumPositionWarehouseDialog = true
            }
            this.loading = false
          })
        }, 100)
      },
      deleteGoodKindFunc () {
        setTimeout(() => {
          this.loading = true
          this.$apollo.mutate({
            mutation: deleteGoodKind,
            variables: {
              input: {
                id: this.getGoodKind.id
              }
            }
          }).then(({data}) => {
            this.loading = false
            if (data.deleteGoodKind.result) {
              this.closeDialog()
              this.$emit('deleted')
            }
          }).catch(() => {
            this.loading = false
          })
        }, 100)
      },
      updateGoodKindExsistCodeFunc () {
        setTimeout(() => {
          this.loading = true
          this.$apollo.mutate({
            mutation: updateGoodKindExsistCode,
            variables: {
              input: {
                id: this.goodKind.id,
                code: this.goodKind.code,
                name: this.goodKind.name,
                manufacturerName: this.goodKind.manufacturerName,
                action: this.action,
                defaultUnit: this.goodKind.defaultUnit
              }
            }
          }).then(({data}) => {
            this.loading = false
            if (data.updateGoodKindExsistCode.goodKind.id) {
              this.closeDialog()
              this.$emit('updated')
            }
          }).catch(() => {
            this.loading = false
          })
        }, 100)
      },
      confirmGoodKindFunc () {
        setTimeout(() => {
          this.loading = true
          this.$apollo.mutate({
            mutation: confirmGoodKind,
            variables: {
              input: {
                id: this.goodKind.id
              }
            }
          }).then(({data}) => {
            this.loading = false
            if (data.confirmGoodKind.result) {
              this.closeDialog()
              this.$emit('confirm')
            }
          }).catch(() => {
            this.loading = false
          })
        }, 100)
      },
      // Закрытие диалога создания нового вида товара
      closeDialog () {
        this.confirmUpdateDialog = false
        this.confirmDeleteDialog = false
        this.sumPositionWarehouseDialog = false
        this.$emit('closeDialog')
      },
      assignExternalGoodKind (goodKind) {
        this.$nextTick(() => this.$refs.gostPicker.refresh())
        if (goodKind) {
          const gk = JSON.parse(JSON.stringify(goodKind))
          this.checkbox = !gk.code
          this.$nextTick(() => { // Исправляет проблему проставления галочки при первом открытии позиции с "code = null"
            this.checkbox = !gk.code
          })
          return gk
        } else {
          return {
            code: null,
            name: null,
            manufacturerName: null,
            goodGroupId: null,
            analogs: null,
            gosts: [],
            defaultUnit: null
          }
        }
      }
    },
    created () { // Для вызова "notValid"
      this.goodKind.name = this.goodKind.name ? this.goodKind.name : ''
      this.goodKind.manufacturerName = this.goodKind.manufacturerName ? this.goodKind.manufacturerName : ''
    },
    computed: {
      deleteBtn () {
        if (!this.goodKind.new) {
          return auth.hasPermission('warehouse.can_moderate')
        } else {
          return true
        }
      },
      // Хотя бы одно поле не заполнено
      notValid () {
        if (this.checkbox) {
          this.goodKind.code = null
          return this.goodKind.manufacturerName === '' || this.goodKind.name === '' || this.goodKind.defaultUnit === null
        }
        return this.goodKind.code === '' || this.goodKind.manufacturerName === '' || this.goodKind.name === '' || this.goodKind.defaultUnit === null
      },
      requiredGoodKind: function () {
        let goodKinds = []
        if (this.goodKind.analogs) {
          goodKinds = Array.isArray(this.goodKind.analogs) ? this.goodKind.analogs : [this.goodKind.analogs]
        }
        const notLoaded = goodKinds.filter(goodKind => {
          return this.allGoodKindsData.findIndex(item => item.id === Number(goodKind)) < 0
        })
        if (notLoaded.length > 0) {
          return notLoaded
        }
        return null
      }
    }
  }
</script>
