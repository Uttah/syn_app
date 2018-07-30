<template>
  <v-card>
    <v-data-table class="header"
                  :headers="headers"
                  :items="allCoefficientsData"
                  :rows-per-page-items="rpp"
                  :rows-per-page-text="'Строк на странице'"
                  :no-data-text="'Нет доступных данных'"
    >
      <template slot="items" slot-scope="props">
        <tr class="td-center">
          <td class="text-xs-left">{{ props.item.user.shortName }}</td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.general"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.general }}
              <float-field
                class="mt-2"
                slot="input"
                label="СМР общее"
                v-model="props.item.general"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.welding"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.welding }}
              <float-field
                slot="input"
                label="Навык сварочных работ"
                v-model="props.item.welding"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.experience"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.experience }}
              <float-field
                slot="input"
                label="Опыт работы в компании"
                v-model="props.item.experience"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.etech"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.etech }}
              <float-field
                slot="input"
                label="Знание основ электротехники"
                v-model="props.item.etech"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.schematic"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.schematic }}
              <float-field
                slot="input"
                label="Чтение схем"
                v-model="props.item.schematic"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.initiative"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.initiative }}
              <float-field
                slot="input"
                label="Инициативность"
                v-model="props.item.initiative"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>
            <v-edit-dialog lazy large :return-value.sync="props.item.discipline"
                           save-text="Сохранить" cancel-text="Отменить">
              {{ props.item.discipline }}
              <float-field
                slot="input"
                label="Дисциплина, прилежность"
                v-model="props.item.discipline"
                required
                autofocus
                :rules="inputRule"
              />
            </v-edit-dialog>
          </td>
          <td>{{ props.item.maxHour }}</td>
          <td>
            <v-btn flat icon title="Сохранить" @click="saveCoefficients(props.item)">
              <v-icon>save</v-icon>
            </v-btn>
          </td>
          <td>{{ props.item.avg }}</td>
          <td>{{ props.item.base }}</td>
        </tr>
      </template>
      <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
        С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {allCoefficients, updateCoefficients} from './query'
  import FloatField from '../FloatField'

  export default {
    name: 'Coefficients',
    components: {
      FloatField
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: allCoefficients,
        update (data) {
          this.allCoefficientsData = JSON.parse(JSON.stringify(data.allCoefficients))
        }
      }
    },
    data () {
      return {
        allCoefficientsData: [],
        headers: [
          {text: 'Сотрудник', align: 'center', value: 'user', sortable: false, class: 'number-header'},
          {text: 'СМР общее', align: 'center', value: 'general', sortable: false, class: 'number-header'},
          {text: 'Навык сварочных работ', align: 'center', value: 'welding', sortable: false, class: 'number-header'},
          {
            text: 'Опыт работы в компании',
            align: 'center',
            value: 'experience',
            sortable: false,
            class: 'number-header'
          },
          {
            text: 'Знание основ электротехники',
            align: 'center',
            value: 'etech',
            sortable: false,
            class: 'number-header'
          },
          {text: 'Чтение схем', align: 'center', value: 'schematic', sortable: false, class: 'number-header'},
          {text: 'Инициативность', align: 'center', value: 'initiative', sortable: false, class: 'number-header'},
          {
            text: 'Дисциплина, прилежность',
            align: 'center',
            value: 'discipline',
            sortable: false,
            class: 'number-header'
          },
          {
            text: 'Максимальная стоимость часа',
            align: 'center',
            value: 'maxHour',
            sortable: false,
            class: 'number-header'
          },
          {text: '', sortable: false, width: '60px'},
          {text: 'Среднее', align: 'center', value: 'AVG', sortable: false, class: 'number-header'},
          {text: 'База, р/час', align: 'center', value: 'base', sortable: false, class: 'number-header'}
        ],
        input: {},
        rpp: [
          10, 25, {text: 'Все', value: -1}
        ],
        inputRule: [
          text => {
            const i = parseFloat(text.replace(',', '.'))
            if (i < 0 || i > 1) {
              return 'от 0-1'
            }
            return true
          }
        ]
      }
    },
    methods: {
      saveCoefficients (wholeItem) {
        let input = JSON.parse(JSON.stringify(wholeItem))
        delete input.__typename
        delete input.avg
        delete input.base
        delete input.maxHour
        delete input.user

        const id = input.id
        delete input.id

        for (const value of Object.values(input)) {
          const f = parseFloat(value)

          if (f < 0 || f > 1) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Неправильный коэффициент ' + value,
              data: {
                error: true
              }
            })
            return
          }
        }
        input.id = id
        this.$apollo.mutate({
          mutation: updateCoefficients,
          variables: {
            input: input
          }
        }).then(({data}) => {
          if (data.updateCoefficients.coefficients) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Обновлено успешно'
            })
          }
        })
      }
    }
  }
</script>

<style>
  .number-header {
    width: 170px;
    max-width: 170px;
    word-wrap: break-word;
    white-space: normal !important;
  }

  .td-center {
    text-align: center;
  }
</style>
