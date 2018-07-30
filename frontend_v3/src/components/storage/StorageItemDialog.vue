<template>
  <v-form v-model="validInner" @submit.prevent="submit">
    <v-container class="pa-0">
      <v-layout wrap justify-center>
        <v-flex xs12>
          <good-kind-select ref="goodKind" persistent v-model="item.goodKindId" required
                            :readonly="disabled" @goodKindText="getGoodKindText"/>
        </v-flex>
        <v-flex xs3>
          <storage-select ref="warehouse" v-model="item.locationId" required :readonly="disabled" check-state/>
        </v-flex>
        <v-flex xs3 class="pl-3">
          <workers-select label="Ответственный" required v-model="item.responsibleId" :readonly="disabled"/>
        </v-flex>
        <v-flex xs3 class="px-3">
          <integer-field label="Количество" required v-model="item.count" :rules="numberOnly" :readonly="disabled"/>
        </v-flex>
        <v-flex xs3>
          <v-select
            label="Ед. изм." v-model="item.unitId"
            :readonly="disabled"
            :items="allUnitsData"
            item-text="name" item-value="id"
            required
            autocomplete
            :rules="nonEmptyField"/>
        </v-flex>
        <v-flex xs3>
          <v-checkbox
            class="mt-3 ml-5"
            label="Некондиция"
            v-model="item.defect"
            :disabled="disabled"
          />
        </v-flex>
        <v-flex xs9>
          <projects-select
            label="Проект"
            v-model="item.projectId"
            clearable
            :readonly="disabled"
          >
          </projects-select>
        </v-flex>
        <v-flex xs12 class="pr-3">
          <v-text-field
            label="Примечание"
            :readonly="disabled"
            v-model="item.note"
            multi-line
          />
        </v-flex>
      </v-layout>
    </v-container>
  </v-form>
</template>


<script>
  import FloatField from '../FloatField.vue'
  import {units} from '../storage/query'
  import utilMixin from '../utils'
  import IntegerField from '../IntegerField'
  import StorageSelect from '../StorageSelect'
  import ManufacturerSelect from '../ManufacturerSelect'
  import GoodKindSelect from '../GoodKindSelect'
  import ProjectsSelect from '../ProjectsSelect'
  import WorkersSelect from '../WorkersSelect'

  export default {
    name: 'StorageItemDialog',
    mixins: [utilMixin],
    props: {
      value: null,
      valid: Boolean,
      disabled: Boolean
    },
    components: {
      WorkersSelect,
      ProjectsSelect,
      IntegerField,
      FloatField,
      StorageSelect,
      ManufacturerSelect,
      GoodKindSelect
    },
    apollo: {
      allUnitsData: {
        query: units,
        fetchPolicy: 'cache-and-network',
        update (data) {
          return data.allUnitsData.map((item) => {
            return {
              id: item.id,
              name: item.name + ` (${item.shortName})`
            }
          })
        }
      }
    },
    data () {
      return {
        validInner: this.valid,
        allUnitsData: [],
        item: this.value,
        // Проверка на ввод числа
        numberOnly: [
          text => text > 0 || 'Число должно быть положительным'
        ],
        // Проверка на пустое поле
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        itemGoodText: {
          goodKindText: null,
          warehouseText: null,
          unitText: null
        }
      }
    },
    watch: {
      value: function (val) {
        this.item = val
      },
      item: {
        handler: function (val) {
          this.$emit('input', val)
        },
        deep: true
      },
      validInner: function (val) {
        this.$emit('update:valid', val)
      },
      'item.goodKindId': function (val) {
        const goodKindObj = this.$refs.goodKind._data.allGoodKindsData.find(item => {
          return item.id === val
        })
        if (goodKindObj) {
          this.itemGoodText.goodKindText = goodKindObj.selectText
        }
      },
      'item.locationId': function (val) {
        const warehouseObj = this.$refs.warehouse._data.allStorageData.find(item => {
          return item.id === val
        })
        if (warehouseObj) {
          this.itemGoodText.warehouseText = warehouseObj.name
        }
      },
      'item.unitId': function (val) {
        const unitObj = this.allUnitsData.find(item => {
          return item.id === val
        })
        if (unitObj) {
          this.itemGoodText.unitText = unitObj.name.slice(unitObj.name.indexOf('(') + 1, -1)
        }
      },
      itemGoodText: {
        handler: function (val) {
          this.$emit('itemGoodText', val)
        },
        deep: true
      }
    },
    methods: {
      getGoodKindText (selectText) {
        this.itemGoodText.goodKindText = selectText
      },
      forceValidate () {
        this.$nextTick(() => this.$refs.form.validate())
      }
    }
  }
</script>

<style>
  .container .layout .flex {
    padding: 0;
  }
</style>
