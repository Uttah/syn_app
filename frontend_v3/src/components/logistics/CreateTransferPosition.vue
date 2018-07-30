<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title class="title">
        Создание позиции перемещения
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-layout v-if="transferPositionData && !transferPositionData.needUnit.restrictSum">
            <float-field label="Количество" v-model="count" required :rules="rules"/>
          </v-layout>
          <div v-else-if="transferPositionData" style="text-align: center">
            <span>Выберите складскую позицию для перемещения:</span>
            <div>
              <!--<div v-if="!isRadio" style="vertical-align: middle">Позиции нужной длины не найдены!</div>-->
              <v-radio-group v-model="radioGroup" :rules="needSelect" row class="text-xs-center">
                <div style="display: flex; flex-wrap: wrap; align-content: flex-start;">
                  <v-radio
                    v-for="stock in transferPositionData.inStock"
                    v-if="stock.unit.id === transferPositionData.needUnit.id && stock.available > 0"
                    :key="stock.id"
                    :label="stock.available + ' ' + stock.unit.shortName"
                    :value="stock.id"
                    style="min-width: 80px; width: 80px;"
                    class="pa-0 ma-0"
                  />
                </div>
              </v-radio-group>

            </div>
          </div>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click="dialog=false">Отмена</v-btn>
        <v-btn flat :loading="loading" :disabled="!valid" @click="createTransferPositionFunc">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {createTransferPosition} from './query'
  import FloatField from '../FloatField'

  export default {
    components: {FloatField},
    name: 'create-transfer-position',
    props: {
      value: Boolean,
      transferPositionData: {
        type: Object,
        default: {
          inStock: [],
          needCount: 0,
          needUnit: {
            shortName: null,
            restrictSum: null
          }
        }
      },
      canDifferentTasks: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isRadio: false,
        radioGroup: null,
        currentAmount: null,
        dialog: false,
        valid: false,
        loading: false,
        count: 0,
        needSelect: [
          val => !!val || 'Нужно выбрать позицию'
        ],
        rules: [
          text => !!text || 'Поле не может быть пустым',
          text => {
            if (Number(text) <= 0) {
              return 'Число должно быть больше нуля'
            }
            return true
          },
          text => {
            if (this.transferPositionData && Number(text) > this.transferPositionData.needCount) {
              return 'Необходимое количество: ' + this.transferPositionData.needCount
            }
            return true
          },
          text => {
            if (this.transferPositionData && this.transferPositionData.inStock && this.transferPositionData.inStock[0].available < Number(text)) {
              return 'Всего доступно для перемещения: ' + this.transferPositionData.inStock[0].available
            }
            return true
          }
        ]
      }
    },
    watch: {
      value: function (val) {
        if (val && this.transferPositionData) {
          // this.isRadio = false
          this.count = this.transferPositionData.needCount
          this.radioGroup = null
          this.$refs.form.validate()
          // this.transferPositionData.inStock.some(stock => {
          //   if (stock.available >= this.transferPositionData.needCount) {
          //     this.isRadio = true
          //     return true
          //   }
          // })
        }
        this.dialog = val
      },
      dialog: function (val) {
        this.$emit('input', val)
      }
    },
    methods: {
      createTransferPositionFunc () {
        const inStock = this.transferPositionData.inStock.find(item => item.id === this.radioGroup)
        // Так как к id дописывается случайное ХХХ число, то обрезаем его:
        this.radioGroup = Number(String(this.radioGroup).slice(0, -3))
        // Проверить для чего это
        if (this.transferPositionData.needUnit && this.transferPositionData.needUnit.restrictSum) {
          this.count = this.radioGroup
        }
        const needCount = inStock ? Math.min(inStock.available, this.transferPositionData.needCount) : this.transferPositionData.needCount
        this.$apollo.mutate({
          mutation: createTransferPosition,
          variables: {
            input: {
              restrictSum: this.transferPositionData.needUnit.restrictSum,
              stockId: this.radioGroup,
              needCount: needCount,
              count: this.count,
              positionId: this.transferPositionData.positionId,
              canDifferentTasks: this.canDifferentTasks
            }
          }
        }).then(({data}) => {
          if (data.createTransferPosition.result) {
            this.loading = false
            this.$emit('createTransferPositionSuccess')
            this.dialog = false
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
