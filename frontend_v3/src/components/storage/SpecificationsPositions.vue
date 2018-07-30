<template>
  <v-card>
    <v-card-title>
      <v-toolbar flat color="white">
        <span v-if="specificationData" class="ma-0 headline">
          {{pad(projectTitle, 5) + ' - ' + specificationData.pressmark}}
          <span v-if="specificationData.approved" class="grey--text">(утверждена)</span>
        </span>
        <v-spacer/>
        <v-btn @click="editSpecification">Основная надпись</v-btn>
        <c-r-u-d-specification ref="crud" @success="success" @reopen="reopen"/>
        <v-btn @click="createExcel(selectedSpecification)" :loading="loadingFile" :disabled="!selectedSpecification">
          Сгенерировать Excel
        </v-btn>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-progress-linear class="pa-0 ma-0 mb-3" height="2" :indeterminate="true" :active="loadingQueriesCount > 0"/>
      <table v-show="selectedSpecification" style="border-collapse: collapse; padding-left: 200px;">
        <thead>
        <tr>
          <td class="cell" style="width: 5%; max-width: 50px; font-weight:bold">Позиция</td>
          <td class="cell" style="width: 50%; max-width: 500px; font-weight:bold">Наименование и техническая
            характеристика
          </td>
          <td class="cell" style="width: 13%; min-width: 100px; font-weight:bold">Тип, марка, обозначение документа</td>
          <td class="cell" style="width: 7%; font-weight:bold">Ед. изм.</td>
          <td class="cell" style="width: 5%; min-width: 70px; font-weight:bold">Кол-во</td>
          <td class="cell" style="width: 10%; max-width: 100px; font-weight:bold">Масса единицы, кг</td>
          <td class="cell" style="width: 10%; max-width: 100px; font-weight:bold">Комментарий</td>
          <td style="width: 80px; min-width: 80px; max-width: 80px">
            <v-btn small disabled fab dark>
              <v-icon dark>add</v-icon>
            </v-btn>
          </td>
        </tr>
        </thead>
        <draggable style="width: 500px" v-model="specificationsPositions"
                   element="tbody"
                   :options="{animation: 100, filter:'.submit', preventOnFilter: false, sort: !specificationData.approved}"
                   @start="drag=true" @end="drag=false">
          <template v-for="element in specificationsPositions">
            <tr class="background-row" v-if="!element.groupingName" :key="element.id" @mouseover="onHoverRow = element.id"
                :class="{submit: editRowId === element.id, 'background-row-unapproved': element.goodKind.new }">
              <td v-if="editRowId !== element.id" class="cell" style="width: 5%; max-width: 50px;">
                {{element.positionalDesignation}}
              </td>
              <td v-else class="cell" style="width: 5%; max-width: 50px;">
                <v-text-field required v-model="editedPositionalDesignation" hide-details/>
              </td>
              <td v-if="editRowId !== element.id" class="cell" style="text-align: left; width: 50%; max-width: 500px;">
                {{ getSelectText(element.goodKind) }}
              </td>
              <td v-else class="cell" style="text-align: left; width: 50%; max-width: 500px;">
                <good-kind-select label="Вид товара" class="ellipsis" persistent v-model="editedGoodKindId"
                                  @mass="getEditedMass" readOnlyGoodKind hide-details/>
              </td>
              <td v-if="editRowId !== element.id" class="cell ellipsis"
                  style="text-align: left; width: 13%; max-width: 100px;">{{element.descriptionInfo}}
              </td>
              <td v-else class="cell" style="width: 13%; max-width: 100px;">
                <v-select
                  :items="editedDescriptionsInfo"
                  label="Тип"
                  :readonly="!editedGoodKindId" v-model="editedDescriptionInfo" combobox
                  class="ellipsis" hide-details/>
              </td>
              <td v-if="editRowId !== element.id" class="cell" style="width: 7%; max-width: 70px;">
                {{element.unit.shortName}}
              </td>
              <td v-else class="cell" style="width: 7%; max-width: 70px;">
                <v-select :items="allUnits" v-model="editedUnit" item-text="shortName" item-value="id" required
                          hide-details/>
              </td>
              <td v-if="editRowId !== element.id" class="cell" style="width: 5%; max-width: 70px;">{{String(element.count).replace('.', ',')}}
              </td>
              <td v-else class="cell" style="width: 5%; max-width: 70px;">
                <float-field v-model="editedCount" required hide-details/>
              </td>
              <td v-if="editRowId !== element.id" class="cell" style="width: 10%; max-width: 70px;">
                <span v-if="element.goodKind.mass">{{String(element.goodKind.mass).replace('.', ',') }}</span>
              </td>
              <td v-else class="cell" style="width: 10%; max-width: 70px;">
                <span v-if="editedMass">{{String(editedMass).replace('.', ',')}}</span>
              </td>

              <td v-if="editRowId !== element.id" class="cell" style="width: 10%; max-width: 100px;">
                {{element.note}}
              </td>
              <td v-else class="cell" style="width: 10%; max-width: 100px;">
                <v-text-field v-model="editedNote" hide-details/>
              </td>


              <td class="white-background" v-if="!specificationData.approved" style="width: 80px; min-width: 80px; max-width: 80px"
                  :class="{ white: editRowId === element.id}">
                <v-btn v-show="editRowId !== element.id && onHoverRow === element.id" class="py-0 ma-0" icon flat
                       title="Редактировать" @click="editRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon dark>edit</v-icon>
                </v-btn>
                <v-btn v-show="editRowId !== element.id && onHoverRow === element.id" class="py-0 ma-0" icon flat
                       title="Дублировать" @click="duplicateRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon dark>mdi-content-duplicate</v-icon>
                </v-btn>
                <v-btn v-show="editRowId === element.id" class="py-0 ma-0" icon flat title="Сохранить"
                       @click="updateRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon dark>save</v-icon>
                </v-btn>
                <v-btn v-show="editRowId === element.id" class="py-0 ma-0" title="Удалить" flat icon
                       @click="deleteRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon>delete_forever</v-icon>
                </v-btn>
              </td>
            </tr>

            <tr v-else :key="element.id" @mouseover="onHoverRow = element.id"
                :class="{submit: editRowId === element.id}">
              <td class="cell"></td>
              <td v-if="editRowId !== element.id" class="cell" style="text-decoration: underline; font-weight:bold">
                {{element.groupingName}}
              </td>
              <td v-else class="cell" style="text-decoration: underline; font-weight:bold">
                <v-text-field required v-model="editedGroupingName" :rules="nonEmptyField" hide-details/>
              </td>
              <td class="cell"></td>
              <td class="cell"></td>
              <td class="cell"></td>
              <td class="cell"></td>
              <td class="cell"></td>
              <td v-if="!specificationData.approved" style="width: 80px; min-width: 80px; max-width: 80px"
                  :class="{ white: editRowId === element.id}">
                <v-btn v-show="editRowId !== element.id && onHoverRow === element.id" class="py-0 ma-0" icon flat
                       title="Редактировать" @click="editRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon dark>edit</v-icon>
                </v-btn>
                <v-btn v-show="editRowId === element.id" class="py-0 ma-0" icon flat title="Сохранить"
                       @click="updateRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon dark>save</v-icon>
                </v-btn>
                <v-btn v-show="editRowId === element.id" class="py-0 ma-0" title="Удалить" flat icon
                       @click="deleteRowMethod(element.id)" :loading="loadingRowIcon">
                  <v-icon>delete_forever</v-icon>
                </v-btn>
              </td>
            </tr>
          </template>
        </draggable>

        <tr v-if="toggleMultiple.length === 3 && !specificationData.approved">
          <td class="cell" style="width: 5%; max-width: 50px;">
            <v-text-field v-model="newPositionalDesignation" hide-details/>
          </td>
          <td class="cell" style="width: 50%; max-width: 500px">
            <v-layout>
              <v-flex xs1>
                <v-btn-toggle class="mt-2" multiple v-model="toggleMultiple">
                  <v-btn @click="deleteGoodKind" small fab flat title="Группировка/Вид товара">
                    <v-icon>widgets</v-icon>
                  </v-btn>
                </v-btn-toggle>
              </v-flex>
              <v-flex xs11>
                <good-kind-select ref="goodKindSelect" label="Вид товара" class="ellipsis" persistent
                                  v-model="newGoodKindId" @mass="getMass" @allDataGoodKind="getAllGoodKindData"
                                  :readOnlyGoodKind="true" hide-details/>
              </v-flex>
            </v-layout>
          </td>
          <td class="cell" style="width: 13%; min-width: 100px">
            <v-select
              :items="descriptionsInfo"
              label="Тип"
              :readonly="!newGoodKindId" v-model="newDescriptionInfo" combobox
              class="ellipsis" hide-details/>
          </td>

          <td class="cell" style="width: 7%">
            <v-select :items="allUnits" v-model="newUnit" item-text="shortName" item-value="id" required hide-details/>
          </td>
          <td class="cell" style="width: 5%; min-width: 70px">
            <float-field v-model="newCount" required hide-details/>
          </td>
          <td class="cell" style="width: 10%; max-width: 100px">
            <span v-if="newMass">{{String(newMass).replace('.', ',')}}</span>
          </td>
          <td class="cell" style="width: 10%; max-width: 100px">
            <v-text-field v-model="newNote" hide-details/>
          </td>
          <td style="width: 80px; min-width: 80px; max-width: 80px">
            <v-btn @click="addNewPosition" small="" fab dark color="primary" title="Добавить позицию">
              <v-icon dark>add</v-icon>
            </v-btn>
          </td>
        </tr>

        <tr v-if="toggleMultiple.length === 2 && !specificationData.approved">
          <td class="cell" style="width: 5%; max-width: 50px">

          </td>
          <td class="cell" style="width: 50%; max-width: 500px">
            <v-layout>
              <v-flex xs1>
                <v-btn-toggle class="mt-2" multiple v-model="toggleMultiple">
                  <v-btn @click="deleteGroup" small fab flat title="Группировка">
                    <v-icon>widgets</v-icon>
                  </v-btn>
                </v-btn-toggle>
              </v-flex>
              <v-flex>
                <v-text-field label="Группировка" v-model="newGroupingName" hide-details/>
              </v-flex>
            </v-layout>
          </td>
          <td class="cell" style="width: 13%; min-width: 100px"></td>
          <td class="cell" style="width: 7%;"></td>
          <td class="cell" style="width: 5%; min-width: 70px;"></td>
          <td class="cell" style="width: 10%; max-width: 100px"></td>
          <td class="cell" style="width: 10%; max-width: 100px"></td>
          <td style="width: 80px; min-width: 80px; max-width: 80px">
            <v-btn @click="addNewPosition" small="" fab dark color="primary" title="Добавить позицию">
              <v-icon dark>add</v-icon>
            </v-btn>
          </td>
        </tr>
      </table>
    </v-card-text>
    <v-card-actions>
      <v-spacer/>
      <v-btn @click="changeSpecificationsPositions" v-show="selectedSpecification && !specificationData.approved"
             :disabled="disabled"
             :loading="loading" color="primary">Сохранить изменения
      </v-btn>
      <v-spacer/>
    </v-card-actions>
  </v-card>
</template>

<script>
  import draggable from 'vuedraggable'
  import {
    specificationsPositions,
    allUnits,
    createSpecificationPosition,
    changeSpecificationsPositions,
    updateSpecificationPosition,
    deleteSpecificationPosition,
    duplicateSpecificationPosition,
    descriptionsInfo,
    createExcel,
    selectedSpecification
  } from './query'
  import SpecificationSelect from '../SpecificationSelect'
  import GoodKindSelect from '../GoodKindSelect'
  import CRUDSpecification from './CRUDSpecification'
  import utilsMixin from '../utils'
  import FloatField from '../FloatField'

  export default {
    name: 'SpecificationsPositions',
    mixins: [utilsMixin],
    components: {
      FloatField,
      draggable,
      SpecificationSelect,
      GoodKindSelect,
      CRUDSpecification
    },
    metaInfo () {
      return {
        title: this.title
      }
    },
    data () {
      return {
        loadingQueriesCount: 0,
        disabledButtonLogic: {
          startPositions: [],
          startSpecification: null
        },
        allSpecification: [],
        descriptionsInfo: [],
        sequence: [],
        loading: false,
        loadingFile: false,
        disabled: false,
        specificationsPositions: [],
        selectedSpecification: null,
        allUnits: [],
        // Работа с новой строкой таблицы
        newPositionalDesignation: '',
        newGoodKindId: null,
        newCount: null,
        newMass: null,
        newNote: null,
        newUnit: null,
        newGroupingName: null,
        newDescriptionInfo: null,
        // Работа с отображением колонок
        toggleMultiple: [0, 1, 2],
        onHoverRow: null,
        editRowId: null,
        loadingRowIcon: false,
        // Работа с редактированием записей колонк
        editedPositionalDesignation: null,
        editedGoodKindId: null,
        editedDescriptionsInfo: [],
        editedUnit: null,
        editedCount: null,
        editedMass: null,
        editedNote: null,
        editedGroupingName: null,
        editedDescriptionInfo: null,
        specificationData: {
          id: null,
          project: {
            id: null,
            number: null,
            description: null,
            state: {
              id: null,
              name: null,
              letter: null
            },
            gip: {
              id: null,
              shortName: null
            }
          },
          pressmark: null,
          documentName: null,
          objectName: null,
          organization: null,
          sectionName: null,
          state: null,
          dates: null,
          workersData: null,
          approved: null
        },
        projectTitle: '',
        validNumber: [
          text => {
            let result = /[^\d]/.test(text)
            // let result = /^([\d]+)(,?)([\d]*)$/.test(text)
            if (result) {
              return 'Только цифры'
            }
            return true
          }
        ],
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    computed: {
      title () {
        if (this.specificationData && this.specificationData.project && this.specificationData.pressmark) {
          return 'Спецификация ' + this.pad(this.specificationData.project.number, 5) + ' - ' + this.specificationData.pressmark
        } else {
          return 'Спецификация'
        }
      }
    },
    apollo: {
      // Позиции спецификации
      query: {
        query: specificationsPositions,
        fetchPolicy: 'cache-and-network',
        loadingKey: 'loadingQueriesCount',
        variables () {
          return {
            filters: this.selectedSpecification
          }
        },
        update (data) {
          this.specificationsPositions = JSON.parse(JSON.stringify(data.specificationsPositions))
        }
      },
      allUnits: {
        query: allUnits,
        fetchPolicy: 'cache-and-network'
      },
      descriptionsInfo: {
        query: descriptionsInfo,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            filters: this.newGoodKindId
          }
        },
        skip () {
          return !this.newGoodKindId
        }
      },
      editedDescriptionsInfo: {
        query: descriptionsInfo,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            filters: this.editedGoodKindId
          }
        },
        update (data) {
          this.editedDescriptionInfo = data.descriptionsInfo[0]
          return data.descriptionsInfo
        },
        skip () {
          return !this.editedGoodKindId
        }
      },
      // Данные спецификации
      query2: {
        query: selectedSpecification,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            specificationId: this.selectedSpecification
          }
        },
        update (data) {
          this.specificationData = (JSON.parse(JSON.stringify(data.selectedSpecification)))
          if (!this.projectTitle) {
            this.projectTitle = this.specificationData.project.number
          }
        }
      }
    },
    created () {
      // Id спецификации
      this.selectedSpecification = this.$route.params.id
    },
    methods: {
      success () {
        this.$apollo.queries.query2.refetch()
      },
      reopen (val) {
        setTimeout(() => {
          this.editSpecification()
        }, 500)
      },
      // Открытие спецификации
      editSpecification () {
        this.$refs.crud.openDialog(this.specificationData)
      },
      deleteGoodKind () {
        this.newGoodKindId = null
        this.newDescriptionInfo = null
        this.newCount = null
        this.newNote = null
        this.newUnit = null
        if (this.$refs.goodKindSelect) {
          this.$refs.goodKindSelect.clearMethod()
        }
      },
      deleteGroup () {
        this.newGroupingName = null
      },
      getMass (val) {
        this.newMass = val
      },
      getEditedMass (val) {
        this.editedMass = val
      },
      getAllGoodKindData (val) {
        this.newDescriptionInfo = val.gosts[0]
        this.newUnit = val.defaultUnit.id
      },
      addNewPosition () {
        // Необходимо для комбобокса "Тип, марка, ..."
        setTimeout(() => {
          this.$apollo.mutate({
            mutation: createSpecificationPosition,
            variables: {
              input: {
                specificationId: this.selectedSpecification,
                positionalDesignation: this.newPositionalDesignation,
                goodKindId: this.newGoodKindId,
                descriptionInfo: this.newDescriptionInfo,
                unitId: this.newUnit,
                count: this.newCount,
                note: this.newNote,
                groupingName: this.newGroupingName
              }
            }
          }).then(() => {
            this.$apollo.queries.query.refetch()
            this.newPositionalDesignation = ''
            this.newGoodKindId = null
            this.newDescriptionInfo = null
            this.newCount = null
            this.newMass = null
            this.newNote = null
            this.newUnit = null
            this.newGroupingName = null
            if (this.$refs.goodKindSelect) {
              this.$refs.goodKindSelect.clearMethod()
            }
          }).catch((err) => {
            console.log(err)
          })
        }, 100)
      },
      changeSpecificationsPositions () {
        this.loading = true
        this.$apollo.mutate({
          mutation: changeSpecificationsPositions,
          variables: {
            input: {
              specificationId: this.selectedSpecification,
              newSequence: this.sequence
            }
          }
        }).then(() => {
          this.loading = false
          this.$apollo.queries.query.refetch()
        }).catch((err) => {
          console.log(err)
          this.loading = false
        })
      },
      editRowMethod (val) {
        this.editRowId = val
        let row = this.specificationsPositions.filter(function (item) {
          if (item.id === val) {
            return item
          }
        })
        // Если будет не нужно - удалить
        this.$nextTick(() => {
          this.editedGroupingName = row[0].groupingName
          this.editedPositionalDesignation = row[0].positionalDesignation
          this.editedGoodKindId = row[0].goodKind ? row[0].goodKind.id : null
          this.editedDescriptionInfo = row[0].descriptionInfo
          this.editedUnit = row[0].unit ? row[0].unit.id : null
          this.editedCount = row[0].count
          this.editedMass = row[0].goodKind ? row[0].goodKind.mass : null
          this.editedNote = row[0] ? row[0].note : null
        })
      },
      // Дублирование строки спецификации
      duplicateRowMethod (val) {
        this.loadingRowIcon = true
        this.$apollo.mutate({
          mutation: duplicateSpecificationPosition,
          variables: {
            input: {
              id: val
            }
          },
          update: (store, {data: {duplicateSpecificationPosition}}) => {
            // Обновляем кеш новой позицией
            try {
              const query = {query: specificationsPositions, variables: {filters: this.selectedSpecification}}
              const data = store.readQuery(query)
              const newPosition = duplicateSpecificationPosition.result
              data.specificationsPositions.forEach(item => {
                if (item.positionInTable >= newPosition.positionInTable) {
                  item.positionInTable++
                }
              })
              data.specificationsPositions.push(newPosition)
              data.specificationsPositions.sort((a, b) => a.positionInTable - b.positionInTable)
              query.data = data
              store.writeQuery(query)
            } catch (e) {
            }
          }
        }).then(({data}) => {
          this.loadingRowIcon = false
          if (data.duplicateSpecificationPosition.result) {
            const newRow = data.duplicateSpecificationPosition.result
            this.$nextTick(() => {
              this.editRowMethod(newRow.id)
            })
          }
        }).catch(() => {
          this.loadingRowIcon = false
        })
      },
      // Сохранение изменения строки
      updateRowMethod (val) {
        this.loadingRowIcon = true
        // Необходимо для комбобокса "Тип, марка, ..."
        setTimeout(() => {
          this.$apollo.mutate({
            mutation: updateSpecificationPosition,
            variables: {
              input: {
                specificationPositionId: val,
                specificationId: this.selectedSpecification,
                positionalDesignation: this.editedPositionalDesignation,
                goodKindId: this.editedGoodKindId,
                descriptionInfo: this.editedDescriptionInfo,
                unitId: this.editedUnit,
                count: this.editedCount,
                note: this.editedNote,
                groupingName: this.editedGroupingName
              }
            }
          }).then(() => {
            this.loadingRowIcon = false
            this.editRowId = null
            this.$apollo.queries.query.refetch()

            this.editedPositionalDesignation = ''
            this.editedGoodKindId = null
            this.editedDescriptionInfo = null
            this.editedCount = null
            this.editedMass = null
            this.editedNote = null
            this.editedUnit = null
            this.editedGroupingName = null
          }).catch((err) => {
            console.log(err)
            this.loadingRowIcon = false
          })
        }, 100)
      },
      deleteRowMethod (val) {
        this.loadingRowIcon = true
        this.$apollo.mutate({
          mutation: deleteSpecificationPosition,
          variables: {
            input: {
              specificationPositionId: val
            }
          }
        }).then(() => {
          this.loadingRowIcon = false
          this.$apollo.queries.query.refetch()
        }).catch((err) => {
          console.log(err)
          this.loadingRowIcon = false
        })
      },
      getSelectText (goodKind) {
        let code = goodKind.code ? goodKind.code : 'б/а'
        return code + ' - ' + goodKind.name + ' (' + goodKind.manufacturer.name + ')'
      },
      createExcel (val) {
        this.loadingFile = true
        this.$apollo.mutate({
          mutation: createExcel,
          variables: {
            input: {
              specificatonId: val
            }
          }
        }).then(({data}) => {
          this.loadingFile = false
          window.location = data.createExcel.result
        }).catch(() => {
          this.loadingFile = false
        })
      },
      // Получаем все Спецификации
      getAllSpecification (val) {
        this.allSpecification = val
      }
    },
    watch: {
      specificationsPositions: {
        handler: function (val) {
          if (val) {
            this.sequence = []
            val.forEach(function (item, index) {
              this.sequence[index] = item.id
            }, this)
          }
        },
        deep: true
      }
    }
  }
</script>

<style scoped>
  .cell {
    border: 2px solid #282828;
    height: 40px;
    text-align: center;
  }

  .background-row:hover {
    background-color: #f0f0f0;
  }

  .background-row-unapproved {
    background-color: #f0ee34;
  }

  .white-background {
    background-color: #ffffff;
  }
</style>
