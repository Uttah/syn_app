<template>
  <v-card>
    <v-card-title>
      <div class="px-5" style="height: 50px; display: flex; width: 100%">
        <span class="body-2 pr-5">Номер заявки: {{transferRequest.transferRequest.id}}</span>
        <span class="body-2 pr-5">Основание: Проект {{transferRequest.transferRequest.where.project.number}} - {{transferRequest.transferRequest.where.project.description }}</span>
        <span class="body-2 pr-5">Запросил:
          <users-chip :users="Array(transferRequest.transferRequest.whoRequested)"/>
        </span>
        <v-spacer/>
        <span>
          <v-btn v-if="!readOnly && !canCompleted && transferRequest.transferRequest.worker ? transferRequest.transferRequest.worker.id === auth.user.id : false" @click="completed" color="primary">Заявка выполнена</v-btn>
        </span>
        <span>
          <v-btn v-if="!readOnly && canRefuse && transferRequest.transferRequest.worker ? transferRequest.transferRequest.worker.id === auth.user.id : false" @click="refuse" color="fired">Отказаться от выполнения</v-btn>
          <v-btn v-if="!transferRequest.transferRequest.worker && transferRequest.transferRequest.whoRequested.id === auth.user.id" @click="deteteRequest" color="fired">Удалить заявку</v-btn>
        </span>
      </div>
      <div class="px-5">
        <span class="body-2 pr-5">Дата заявки: {{ formatDate(transferRequest.transferRequest.creationDate)}}</span>
        <span class="body-2 pr-5">Куда: {{transferRequest.transferRequest.where.name}}, ящик проекта {{transferRequest.transferRequest.where.project.number}}</span>
        <span class="body-2">Исполнитель:
          <span v-if="transferRequest.transferRequest.worker">
            <users-chip :users="Array(transferRequest.transferRequest.worker)"/>
          </span>
          <span v-else>
             Нет исполнителя
          </span>
        </span>
      </div>
    </v-card-title>
    <v-card-text>
      <v-card>
        <v-card-text style="height: 150px">
          <v-layout v-if="transferRequest.transferRequest.worker ? transferRequest.transferRequest.worker.id === auth.user.id : false" style="height: 100%">
            <v-flex class="pt-4" xs1>
              <v-btn @click="setNumberBefore" :disabled="readOnly" flat depressed large icon>
                <v-icon size="150px">navigate_before</v-icon>
              </v-btn>
            </v-flex>
            <v-flex xs3 style="height: 90%">
              <v-btn @click="openDialog(hoverItem)" :loading="loading" :disabled="readOnly" color="primary" style="height: 100%; max-width: 300px;">
                <span style="word-wrap: break-word; padding: 10px;">Внести перемещённое количество</span></v-btn>
            </v-flex>
            <v-flex xs2 class="pt-4" style="font-size: large; text-align: center;">
              {{currentPosition.location}} Ящик проекта {{currentPosition.project}}
              <!--<span style="word-wrap: break-word; font-size: medium; padding: 10px;">Внести перемещённое количество</span>-->
            </v-flex>
            <v-flex xs3 class="pt-4" style="font-size: large; vertical-align: middle; text-align: center; overflow: hidden">
              {{currentPosition.goodGroup}} {{currentPosition.code}} {{currentPosition.name}}
            </v-flex>
            <v-flex xs1 class="pt-4" style="font-size: large; text-align: center;">
              {{currentPosition.count}} {{currentPosition.unit.shortName}}
            </v-flex>
            <v-spacer/>
            <v-flex class="pt-4" xs1>
              <v-btn @click="setNumberNext" :disabled="readOnly" flat large icon>
                <v-icon size="150px">navigate_next</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>

          <v-layout wrap justify-center v-if="transferRequest.transferRequest.worker === null" style="height: 100%">
            <v-spacer/>
            <v-flex xs2 style="height: 80%">
              <v-btn @click="takeRequisition" :loading="loading" color="primary" style="height: 100%; font-size: large">Взять заявку в работу</v-btn>
            </v-flex>
            <v-spacer/>
          </v-layout>

        </v-card-text>
      </v-card>
      <v-data-table
        :headers="headers"
        :items="transferRequest.transferPositions"
        :pagination.sync="pagination"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        :no-data-text="'Нет позиций перемещения'"
        must-sort
        hide-actions
        class="elevation-1"
        style="max-height: 300px; overflow-y: scroll"
      >
        <template slot="items" slot-scope="props">
          <tr :id="row.id" v-for="(row, i) in props.item.subRows" :class="{ target: props.item.goodKind.id === hoverItem }">
            <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.goodGroup ? props.item.goodKind.goodGroup.name : '' }}</td><!--Группа товара-->
            <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.code ? props.item.goodKind.code : 'б/а' }}</td><!--Артикул-->
            <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.name}}</td><!--Наименование-->
            <td v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">{{ props.item.goodKind.manufacturer.name }}</td><!--Приизводитель-->

            <td :class="{ target: props.item.goodKind.id === hoverItemColor && row.number === hoverItem,
            new: row.transfer < row.count, checked: String(row.transfer) === String(row.count) }">{{ row.serialNumber }}</td><!--Номер П/П-->

            <td :class="{ target: props.item.goodKind.id === hoverItemColor && row.number === hoverItem,
            new: row.transfer < row.count, checked: String(row.transfer) === String(row.count) }">
              <span>
                {{ row.location.name}} Ящик проекта {{ row.location.project.number }}
              </span>
              <span v-if="currentPosition.unit.restrictSum">
                 ({{row.allCount}} {{currentPosition.unit.shortName}})
              </span>

            </td><!--Местонахождение-->

            <td :class="{ target: props.item.goodKind.id === hoverItemColor && row.number === hoverItem,
            new: row.transfer < row.count, checked: String(row.transfer) === String(row.count) }">{{ row.project ? pad(row.project.number, 5) : '' }}</td><!--Проект-->

            <td :class="{ target: props.item.goodKind.id === hoverItemColor && row.number === hoverItem,
            new: row.transfer < row.count, checked: String(row.transfer) === String(row.count) }">{{ row.count }}</td><!--Количество-->

            <td :class="{ target: props.item.goodKind.id === hoverItemColor && row.number === hoverItem,
            new: row.transfer < row.count, checked: String(row.transfer) === String(row.count) }" @click="openDialog(row.number)">
              <v-text-field v-model="row.transfer" readonly hide-details/>
            </td><!--Перемещено-->

          </tr>
        </template>
      </v-data-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="title">Перемещение</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="valid">
            <v-text-field :label="'Необходимо переместить ' + currentPosition.count + ' ' + currentPosition.unit.shortName" v-model="currentPosition.transfer" :rules="numberOnly"/>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDialog" :loading="loading">Отмена</v-btn>
          <v-btn flat @click="checkCount" :loading="loading" :disabled="
          ((currentPosition.count > currentPosition.transfer && Number(currentPosition.transfer) !== 0) && currentPosition.unit.restrictSum)
          || (!currentPosition.unit.restrictSum && currentPosition.count < currentPosition.transfer)
          || (currentPosition.unit.restrictSum && allCountSaved < currentPosition.transfer)
          || !valid">Переместить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>
</template>

<script>
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import {transferRequest, addWorkerInTransferRequest, workerRefuseInTransferRequest, updateTransferPositions, completedTransferRequest, deleteTransferRequestInTransfer} from './query'
  import UsersChip from '../UsersChip'

  export default {
    name: 'TransferRequest',
    metaInfo: {
      title: 'Заявка на перемещение'
    },
    components: {
      UsersChip
    },
    mixins: [utilMixin],
    data () {
      return {
        allCountSaved: null,
        readOnly: false,
        valid: false,
        dialog: false,
        currentPosition: {
          goodGroup: null,
          code: null,
          name: null,
          location: null,
          project: null,
          count: null,
          transfer: null
        },
        canRefuse: false,
        loading: false,
        hoverItem: 1,
        hoverItemColor: null,
        auth: auth,
        transferRequest: [],
        loadingQueriesCount: 0,
        moveCounter: 0,
        pagination: {
          rowsPerPage: 10,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'goodGroup'
        },
        headers: [
          {text: 'Группа товаров', align: 'left', value: 'goodGroup'},
          {text: 'Артикул', align: 'left', value: 'article'},
          {text: 'Наименование', align: 'left', value: 'name'},
          {text: 'Производитель', align: 'left', value: 'manufacturer'},
          {text: '№ п/п', align: 'left', sortable: false, value: 'position'},
          {text: 'Местонахождение', align: 'left', sortable: false, value: 'location'},
          {text: 'Проект', align: 'left', sortable: false, value: 'project'},
          {text: 'Кол-во', align: 'left', sortable: false, value: 'count'},
          {text: 'Перемещено', align: 'left', sortable: false, value: 'transferred'}
        ],
        // Проверка на ввод числа
        numberOnly: [
          text => text > -1 || 'Число должно быть положительным'
        ]
      }
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: transferRequest,
        variables () {
          return {
            requestId: this.$route.params.id,
            sortBy: this.pagination.sortBy,
            desc: this.pagination.descending
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.transferRequest = JSON.parse(JSON.stringify(data.transferRequest))
          this.readOnly = this.transferRequest.transferRequest.completed
          // Получаем поля первой строки таблицы для отображения в шапке при загрузке страницы
          if (this.transferRequest.transferPositions) {
            this.currentPosition = {
              id: this.transferRequest.transferPositions[0].subRows[0].id,
              goodGroup: this.transferRequest.transferPositions[0].goodKind.goodGroup ? this.transferRequest.transferPositions[0].goodKind.goodGroup.name : '',
              code: this.transferRequest.transferPositions[0].goodKind.code,
              name: this.transferRequest.transferPositions[0].goodKind.name,
              location: this.transferRequest.transferPositions[0].subRows[0].location.name,
              project: this.transferRequest.transferPositions[0].subRows[0].location.project ? this.transferRequest.transferPositions[0].subRows[0].location.project.number : '',
              count: this.transferRequest.transferPositions[0].subRows[0].count,
              transfer: this.transferRequest.transferPositions[0].subRows[0].transfer,
              unit: this.transferRequest.transferPositions[0].subRows[0].unit
            }
            this.hoverItemColor = this.transferRequest.transferPositions[0].goodKind.id
          }
        }
      }
    },
    methods: {
      checkCount () {
        this.transferRequest.transferPositions.some((item) => {
          let row = item.subRows.find(myData => myData.number === this.hoverItem)
          if (row) {
            row.transfer = this.currentPosition.transfer
          }
          return row
        })
        if (this.currentPosition.id && this.currentPosition.transfer) {
          this.updateTable()
        }
        this.closeDialog()
      },
      closeDialog () {
        this.dialog = false
      },
      // Метод открывает диалог ввода количествы и делает hoverItem актуальной
      openDialog (val) {
        this.transferRequest.transferPositions.some((item) => {
          let row = item.subRows.find(myData => myData.number === val)
          if (row) {
            this.allCountSaved = row.allCount
          }
          return row
        })
        this.hoverItem = val
        if (this.transferRequest.transferRequest.worker && this.transferRequest.transferRequest.worker.id === auth.user.id && !this.readOnly) {
          this.dialog = true
        }
      },
      getGoodKindId () {
        return this.transferRequest.transferPositions.find((item) => {
          return item.subRows.find(dataItem => dataItem.number === this.hoverItem)
        }).goodKind.id
      },
      // Рекурсивный метод. Работает совместно с setNumberBefore
      // Проверяет строку count = transfer и переходит к следующей
      myBeforeMethod () {
        this.moveCounter += 1
        let data = this.transferRequest.transferPositions.some((item) => {
          let data = item.subRows.find(dataItem => dataItem.number === this.hoverItem - this.moveCounter)
          if (data) {
            if (String(data.count) === String(data.transfer)) {
              return data
            } else {
              this.hoverItem -= this.moveCounter
              this.hoverItemColor = this.getGoodKindId()
              this.moveCounter = 0
            }
          }
        })
        if (data) {
          this.setNumberBefore()
        }
      },
      setNumberBefore () {
        if (this.hoverItem - this.moveCounter > 1) {
          this.myBeforeMethod()
        } else {
          this.moveCounter = 0
        }
      },
      // Рекурсивный метод. Работает совместно с setNumberNext
      // Проверяет строку count = transfer и переходит к следующей
      myNextMethod () {
        this.moveCounter += 1
        let data = this.transferRequest.transferPositions.some((item) => {
          let data = item.subRows.find(dataItem => dataItem.number === this.hoverItem + this.moveCounter)
          if (data) {
            if (String(data.count) === String(data.transfer)) {
              return data
            } else {
              this.hoverItem += this.moveCounter
              this.hoverItemColor = this.getGoodKindId()
              this.moveCounter = 0
            }
          }
        })
        if (data) {
          this.setNumberNext()
        }
      },
      setNumberNext () {
        let data = this.transferRequest.transferPositions[this.transferRequest.transferPositions.length - 1].subRows
        if (this.hoverItem + this.moveCounter < data[data.length - 1].number) {
          this.myNextMethod()
        } else {
          this.moveCounter = 0
        }
      },
      completed () {
        this.$apollo.mutate({
          mutation: completedTransferRequest,
          variables: {
            input: {
              transferRequest: this.transferRequest.transferRequest.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$router.push({name: 'transfer_requests_list'})
        }).catch((error) => {
          console.log(error)
        })
      },
      deteteRequest () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deleteTransferRequestInTransfer,
          variables: {
            input: {
              transferRequest: this.transferRequest.transferRequest.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$router.push({name: 'reports'})
        }).catch(() => {
          this.loading = false
        })
      },
      updateTable () {
        this.$apollo.mutate({
          mutation: updateTransferPositions,
          variables: {
            input: {
              transferPositionId: this.currentPosition.id,
              transfer: this.currentPosition.transfer
            }
          }
        }).catch((error) => {
          console.log(error)
        })
      },
      takeRequisition () {
        this.loading = true
        this.$apollo.mutate({
          mutation: addWorkerInTransferRequest,
          variables: {
            input: {
              worker: auth.user.id,
              transferRequest: this.transferRequest.transferRequest.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$apollo.queries.query.refetch()
        }).catch(() => {
          this.loading = false
        })
      },
      refuse () {
        this.loading = true
        this.$apollo.mutate({
          mutation: workerRefuseInTransferRequest,
          variables: {
            input: {
              worker: this.transferRequest.transferRequest.worker.id,
              transferRequest: this.transferRequest.transferRequest.id
            }
          }
        }).then(({data}) => {
          this.loading = false
          this.$apollo.queries.query.refetch()
        }).catch(() => {
          this.loading = false
        })
      }
    },
    computed: {
      // Если хоть одна позиция равна null(для блокировки кнопки "заявка выполнена")
      // ошибка при загрузке страницы
      canCompleted: function () {
        return this.transferRequest.transferPositions.some((item) => {
          return item.subRows.some((dataItem) => {
            return dataItem.transfer === null
          })
        })
      }
    },
    watch: {
      transferRequest: {
        handler: function (val) {
          // Проверка есть ли хоть одно поле с перемещениями
          this.canRefuse = !this.transferRequest.transferPositions.some((item) => {
            return item.subRows.some((dataItem) => {
              return dataItem.transfer !== null
            })
          })
        },
        deep: true
      },
      hoverItem: {
        handler: function (val) {
          this.hoverItemColor = this.getGoodKindId()
          let data = null
          this.transferRequest.transferPositions.some((item) => {
            data = item.subRows.find(dataItem => dataItem.number === val)
            if (data) {
              this.currentPosition = {
                id: data.id,
                goodGroup: item.goodKind.goodGroup ? item.goodKind.goodGroup.name : '',
                code: item.goodKind.code,
                name: item.goodKind.name,
                location: data.location.name,
                project: data.location.project ? data.location.project.number : '',
                count: data.count,
                transfer: data.transfer,
                unit: data.unit
              }
              // Находим текущую строку в DOM'е и скроллим экран до неё
              document.getElementById(data.id).scrollIntoView({block: 'end'})
            }
            return data
          })
        }
      }
    }
  }
</script>
