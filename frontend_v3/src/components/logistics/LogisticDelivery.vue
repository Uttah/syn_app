<template>
  <v-card>
    <v-card-title class="py-0">
      <div style="display: inline; width: 100%">
        <div style="width: 20%; float:left;" class="pt-4">
          <v-checkbox
            style="max-width: 200px; padding: 0"
            label="Опоздала поставка"
            v-model="logisticDeliveryFilter.lateDelivery"
            hide-details
          />
          <v-checkbox
            style="max-width: 200px; padding: 0"
            label="Просроченные"
            v-model="logisticDeliveryFilter.overdue"
            hide-details
          />
        </div>
        <v-spacer/>
        <v-checkbox
          class="pt-4"
          style="width: 15%; float:left; padding: 0"
          label="Готовые к перемещению"
          title="Готовые к перемещению"
          v-model="readyToGo"
        />
        <v-checkbox
          class="pt-4"
          style="width: 15%; float:left; padding: 0"
          label="Ожидающие моих действий"
          title="Ожидающие моих действий"
          v-model="myActions"
        />
        <v-checkbox
          class="pt-4"
          style="width: 175px; float:left; padding: 0"
          label="С моим участием"
          v-model="myPartic"
        />
        <header-filter class="pt-3 pr-2 mr-4" @clearFilters="clearFilters" style="max-width: 100px; float:left; padding: 0">
          <v-layout row wrap justify-center>
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-dates-picker v-model="logisticDeliveryFilter.expectedDate" label="Ожидаемая дата" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-dates-picker v-model="logisticDeliveryFilter.deadline" label="Необходимая дата" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding" style="padding-left: 0">
              <two-dates-picker v-model="logisticDeliveryFilter.orderDate" label="Дата заказа" hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <projects-select label="Проекты" v-model="logisticDeliveryFilter.projects" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Ответственный" v-model="logisticDeliveryFilter.responsible" multiple clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Исполнитель" v-model="logisticDeliveryFilter.workers" clearable hide-details/>
            </v-flex>
            <v-flex xs11 class="filter-padding">
              <workers-select label="Переместивший" v-model="logisticDeliveryFilter.moved" clearable hide-details/>
            </v-flex>
            <v-flex xs5 style="padding-left: 20px">
              <v-select :items="statuses" v-model="logisticDeliveryFilter.statusInStock"/>
            </v-flex>
            <v-flex xs5 style="padding-right: 20px">
              <v-text-field label="Кол-во на складе" v-model="logisticDeliveryFilter.countInStock"/>
            </v-flex>
          </v-layout>
        </header-filter>
        <v-text-field
          hide-details
          label="Поиск - № заявки, задачи, перемещения, товар"
          title="Поиск - № заявки, задачи, перемещения, товар"
          append-icon="search"
          v-model="searchQuery"
          style="width: 27%;"/>
      </div>
      <br/>
      <div v-if="auth.hasPermission('logistics.is_logist')" style="display: inline; width: 100%; text-align: center;">
        <v-btn style="width: 350px; padding: 0; display: inline-block;" class="primary" @click="createDialog = true" :disabled="!changeReadyToGoTransferRequestId || auth.user.id !== changeReadyToGoTransferRequestUserId">Создать заявку на перемещение</v-btn>
        <v-btn style="width: 350px; padding: 0; display: inline-block;" class="fired" @click="deleteDialog = true" :disabled="!changeReadyToGoTransferRequestId || auth.user.id !== changeReadyToGoTransferRequestUserId">Удалить заявку на перемещение</v-btn>
      </div>
    </v-card-title>


    <v-card-text style="padding: 0;">
      <v-data-table
        class="header elevation-1"
        :headers="headers"
        :items="logisticDeliveryItems.logisticsRequestPositions"
        :total-items="logisticDeliveryItems.totalCount"
        :pagination.sync="pagination"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        :rows-per-page-items="rpp"
        :rows-per-page-text="'Строк на странице'"
        :no-data-text="'Нет доступных данных'"
        must-sort
      >
        <template slot="items" slot-scope="props">
          <tr style="height: 50px" v-for="(row, i) in props.item.subRows" :class="{
           target: props.item.goodKind.id === hoverItem,

           locked: (row.task && row.task.responsible ? row.task.responsible.id !== auth.user.id : false)
            || (!row.task) || (!row.task.responsible)
            || (Number(savedLogisticRequestId) !== Number(row.request.id) && Number(savedLogisticRequestId) !== -1)
            || (row.inStock.length>0 && row.inStock[0].available <= 0)
            || (row.inStock.length===0)
            || (Number(savedProjectId) !== Number(row.request.goal.project.id) && Number(savedProjectId) !== -1),

            lockedText: (row.task && row.task.responsible ? row.task.responsible.id !== auth.user.id : false)
            || (!row.task) || (!row.task.responsible)
            || (Number(savedLogisticRequestId) !== Number(row.request.id) && Number(savedLogisticRequestId) !== -1)
            || (row.inStock.length>0 && row.inStock[0].available <= 0)
            || (row.inStock.length===0)
            || (Number(savedProjectId) !== Number(row.request.goal.project.id) && Number(savedProjectId) !== -1)}"
              class="tableLine trClass"
              @mouseover="tableHover(row, props.item.goodKind)">

            <td :class="{ fired: Date.parse(row.expectedDate) < Date.now() && row.expectedDate,
            background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem && (Date.parse(row.expectedDate) >= Date.now() || !row.expectedDate)}"
            class="py-0 px-1 text-xs-center">
              <span class="table-font-size">{{ formatDate(row.expectedDate) }}</span>
            </td><!--Ожидаемая дата поставки-->

              <td :class="{ fired: row.deadline && Date.parse(row.deadline) < today,
            background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem && (Date.parse(row.deadline) >= Date.now() || !row.deadline)}"
                class="table-font-size py-0 px-1 text-xs-center">
              <span class="table-font-size">{{ formatDate(row.deadline) }}</span>
            </td><!--Необходимая дата поставки-->

            <td class="py-0 px-1 text-xs-center" :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">
              <span class="table-font-size">{{ formatDate(row.orderDate) }}</span>
            </td><!--Дата заказа-->

            <td class="py-0 px-1 text-xs-left" v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">
              <span class="table-font-size">
                <span style="font-style: italic;">
                  {{ props.item.goodKind.goodGroup ? props.item.goodKind.goodGroup.name + ', ' : '' }}
                  {{ props.item.goodKind.code ? props.item.goodKind.code : 'б/а' }}
                </span>
                 - {{props.item.goodKind.name }}
              </span>
            </td><!--Товар-->

            <td class="py-0 px-1 text-xs-center" v-if="!i" :rowspan="props.item.subRows.length" :class="{ target: props.item.goodKind.id === hoverItemColor }">
              <span class="table-font-size">{{ props.item.goodKind.manufacturer ? props.item.goodKind.manufacturer.name : '' }}</span>
            </td><!--Приизводитель-->

            <td class="py-0 px-1 text-xs-center" :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">
              <span class="table-font-size">{{ row.count }} {{ row.unit.shortName }}</span>
            </td><!--Необходимое количество-->

            <td :class="{ checked: row.inStock.length>0 && row.inStock[0].available >= row.count - row.sumTransfer,
            background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem,
            fired: row.inStock.length>0 && row.inStock[0].available < row.count - row.sumTransfer}" class="text-xs-center py-0 px-1">
              <logistic-hint :position="row" :isTransfer="false"/>
            </td><!--Есть на складе-->

            <td class="py-0 px-1 text-xs-center" :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">


              <v-layout style="display: table;">
                <v-flex v-if="(row.inStock.length>0 && transferredOrReserved < row.count)
                && row.id === hoverItem && row.inStock[0].available > 0
                && (Number(savedLogisticRequestId) === Number(row.request.id) || Number(savedLogisticRequestId) === -1)
                && (row.task && row.task.responsible ? row.task.responsible.id === auth.user.id : false)">
                  <v-btn class="mx-0"
                         icon
                         @click.native.stop="openMoveDialog(props.item.goodKind, row)"
                         title="Переместить"
                  >
                    <v-icon>launch</v-icon>
                  </v-btn>
                </v-flex>

                <v-flex style="display:table-cell!important; vertical-align:middle;">
                  <logistic-hint :position="row" :isTransfer="true" :logisticDelivery="true"/>
                </v-flex>
                <v-spacer/>
              </v-layout>
            </td><!--Заявки на перемещение-->


            <td class="py-0 px-1 text-xs-center" :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">
              <div @click="openRequest(row.request.id)" style="text-decoration: underline; color: blue; cursor: pointer" class="table-font-size">{{ row.request.id }}</div>
              <div @click="openTask(row.request.id, row.task.id)" style="text-decoration: underline; color: blue; cursor: pointer" class="table-font-size">{{ row.task ? row.task.id : '' }}</div>
            </td><!--Заявка, задача-->
            <td class="pa-0 text-xs-center" :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}">
              <span class="table-font-size">{{ row.number }}</span>
            </td><!--№ пп-->
            <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}" style="text-decoration: underline; color: blue" class="py-0 px-1 text-xs-center">
              <v-menu open-on-hover open-delay="300" top offset-y>
                <span class="table-font-size" slot="activator">{{ row.request.goal.project ? '№ ' + pad(row.request.goal.project.number, 5) : '' }}</span>
                <v-card>
                  <v-card-text>
                    №{{pad(row.request.goal.project.number, 5)}} - {{row.request.goal.project.description}}
                  </v-card-text>
                </v-card>
              </v-menu>
            </td><!--Проект-->
            <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}"
                style="width: 180px; max-width: 180px; white-space: nowrap; overflow: hidden;" class="py-0 px-1 text-xs-center">
              <users-chip :users="row.request.responsible"/>
              <!--Временно отключил ссылку на пользователя-->
            </td><!--Ответственные-->

            <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}" class="pa-0">
              <users-chip v-if="row.task && row.task.responsible" :users="Array(row.task.responsible)"/>
              <!--Временно отключил ссылку на пользователя-->
            </td><!--Исполнитель задачи-->
            <td :class="{ background: props.item.goodKind.id === hoverItemColor && row.id !== hoverItem}" class="py-0 pa-1">
              <file-upload
                style="width: 100px; height: 100%; min-height: 70px;"
                v-if="row.task && row.task.files.length > 0"
                v-model="row.task.files"
                :clickable="false"
                readOnly
              />
            </td>
          </tr>
        </template>
        <template slot="pageText" slot-scope="{ pageStart, pageStop, itemsLength }">
          С {{ pageStart }} по {{ pageStop }} из {{ itemsLength }}
        </template>
      </v-data-table>
    </v-card-text>

    <create-transfer-position
      v-model="createTransferPositionDialogShow"
      :transferPositionData="transferPositionData"
      :canDifferentTasks="true"
      @createTransferPositionSuccess="reload"
    />

    <v-dialog v-model="createDialog" max-width="500px">
      <v-card>
        <v-card-title class="title">
          Создание заявки на перемещение
        </v-card-title>
        <v-card-text>
          Вы действительно хотите создать заявку на перемещение?
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="createDialog = false" :loading="loading" :disabled="loading">Отменить</v-btn>
          <v-btn flat @click="createTransferRequest" :loading="loading" :disabled="loading">Сохранить</v-btn>
        </v-card-actions>
      </v-card>

    </v-dialog>
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="title">
          Удаление заявки на перемещение
        </v-card-title>
        <v-card-text>
          Вы действительно хотите удалить заявку на перемещение?
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="deleteDialog = false" :loading="loading" :disabled="loading">Отменить</v-btn>
          <v-btn flat @click="deleteTransferRequest" :loading="loading" :disabled="loading">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>
</template>

<script>
  import utilMixin from '../utils'
  import _ from 'lodash'
  import gql from 'graphql-tag'
  import auth from '../../auth/auth'
  import {pagedLogisticsRequestPosition, changeReadyToGo, deleteTransferRequest} from './query'
  import HeaderFilter from '../HeaderFilter'
  import ProjectsSelect from '../ProjectsSelect'
  import StorageSelect from '../StorageSelect'
  import DatePicker from '../DatePicker'
  import TwoMonthsPicker from '../TwoMonthsPicker'
  import TwoDatesPicker from '../TwoDatesPicker'
  import WorkersSelect from '../WorkersSelect'
  import CreateTransferPosition from './CreateTransferPosition'
  import FileUpload from '../FileUpload'
  import LogisticHint from './LogisticHint'
  import UsersChip from '../UsersChip'

  export default {
    name: 'LogisticDelivery',
    metaInfo: {
      title: 'Ожидаемые товары'
    },
    components: {
      HeaderFilter,
      ProjectsSelect,
      StorageSelect,
      DatePicker,
      TwoMonthsPicker,
      WorkersSelect,
      CreateTransferPosition,
      FileUpload,
      TwoDatesPicker,
      LogisticHint,
      UsersChip
    },
    mixins: [utilMixin],
    data () {
      return {
        today: new Date().setHours(0, 0, 0, 0),
        valid: false,
        loading: false,
        createDialog: false,
        deleteDialog: false,
        // Логист задачи создающий заявку на перемещение
        changeReadyToGoTransferRequestUserId: null,
        // Id заявки на перемещение которую пользователь ещё не подтвердил
        changeReadyToGoTransferRequestId: null,
        createTransferPositionDialogShow: false,
        transferPositionData: {
          inSock: [],
          needCount: 0,
          needUnit: {
            shortName: null,
            restrictSum: null
          }
        },
        readyToGo: false,
        myActions: false,
        myPartic: false,
        hoverItemColor: null,
        hoverItem: null,
        radioItems: ['Готовые к перемещению', 'Ожидающие моих действий', 'С моим участием'],
        auth: auth,
        statuses: ['Меньше или равно', 'Равно', 'Больше или равно'],
        logisticDeliveryFilter: this.getValue('filter', {
          lateDelivery: false,
          overdue: false,
          rowStatus: null,
          expectedDate: {
            dateStart: null,
            dateEnd: null
          },
          deadline: {
            dateStart: null,
            dateEnd: null
          },
          orderDate: {
            dateStart: null,
            dateEnd: null
          },
          projects: [],
          responsible: [],
          workers: null,
          moved: null,
          countInStock: null,
          statusInStock: 'Меньше или равно'
        }),
        logisticDeliveryItems: [],
        goodLocationInfoData: [],
        searchText: '',
        searchQuery: '',
        loadingQueriesCount: 0,
        rpp: [25, 50, 100],
        pagination: this.getValue('pagination', {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'expectedDate'
        }),
        headers: [
          {text: 'Ожид. дата', align: 'center', value: 'expectedDate', class: 'px-1 block-width60'},
          {text: 'Необход. дата', align: 'center', value: 'deadline', class: 'px-1 block-width60'},
          {text: 'Дата заказа', align: 'center', value: 'orderDate', class: 'px-1 block-width60'},
          {text: 'Товар', align: 'center', sortable: false, value: 'good', class: 'px-1 block-width300'},
          {text: 'Производитель', align: 'center', value: 'manufacturer', class: 'px-1 block-width100'},
          {text: 'Необх. кол-во', align: 'center', sortable: false, class: 'px-1 block-width50'},
          {text: 'Есть на складе', align: 'center', sortable: false, class: 'px-1 block-width100'},
          {text: 'Заявки на перемещение', align: 'center', sortable: false, class: 'px-1 block-width100'},
          {text: 'Заявка Задача', align: 'center', sortable: false, class: 'px-1 block-width50'},
          {text: '№ п/п', align: 'center', sortable: false, value: 'number', class: 'px-1 block-width50'},
          {text: 'Проект', align: 'center', sortable: false, value: 'projects', class: 'px-1 block-width60'},
          {text: 'Ответственные', align: 'center', sortable: false, value: 'responsible', class: 'px-1 '},
          {text: 'Исполнитель задачи', align: 'center', sortable: false, value: 'workers', class: 'px-1 block-width100'},
          {text: 'Счета', align: 'center', sortable: false, value: 'status', class: 'px-1'}
        ],
        savedLogisticRequestId: null,
        savedProjectId: null,
        // Сумма ВСЕХ перемещений на выбранной строке(необходима для проверки кнопки "Переместить")
        transferredOrReserved: null
      }
    },
    apollo: {
      query: {
        fetchPolicy: 'network-only',
        pollInterval: 30000,
        query: pagedLogisticsRequestPosition,
        variables () {
          return {
            paged: {
              first: this.pagination.rowsPerPage,
              offset: this.pagination.rowsPerPage * (this.pagination.page - 1),
              desc: this.pagination.descending,
              search: this.searchText,
              sortBy: this.pagination.sortBy
            },
            filters: {
              lateDelivery: this.logisticDeliveryFilter.lateDelivery,
              overdue: this.logisticDeliveryFilter.overdue,
              rowStatus: this.logisticDeliveryFilter.rowStatus,
              expectedDate: this.logisticDeliveryFilter.expectedDate,
              deadline: this.logisticDeliveryFilter.deadline,
              orderDate: this.logisticDeliveryFilter.orderDate,
              projects: this.logisticDeliveryFilter.projects,
              responsible: this.logisticDeliveryFilter.responsible,
              worker: this.logisticDeliveryFilter.workers,
              moved: this.logisticDeliveryFilter.moved,
              countInStock: this.logisticDeliveryFilter.countInStock,
              statusInStock: this.logisticDeliveryFilter.statusInStock
            }
          }
        },
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.logisticDeliveryItems = JSON.parse(JSON.stringify(data.pagedLogisticsRequestPosition))
          this.changeReadyToGoMethod()
        }
      },
      query2: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            getLogisticsRequestId
          }`,
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.savedLogisticRequestId = JSON.parse(JSON.stringify(data.getLogisticsRequestId))
        }
      },
      query3: {
        fetchPolicy: 'cache-and-network',
        query: gql`
          query {
            getLogisticsRequestProjectId
          }`,
        loadingKey: 'loadingQueriesCount',
        update (data) {
          this.savedProjectId = JSON.parse(JSON.stringify(data.getLogisticsRequestProjectId))
        }
      }
    },
    methods: {
      changeReadyToGoMethod () {
        if (this.logisticDeliveryItems) {
          this.logisticDeliveryItems.logisticsRequestPositions.some((item) => {
            return item.subRows.some((subRow) => {
              if (subRow.transferpositionSet.length > 0) {
                return subRow.transferpositionSet.some((transferposition) => {
                  if (transferposition.transferRequest.readyToGo === false && transferposition.transferRequest.completed === false) {
                    this.changeReadyToGoTransferRequestUserId = transferposition.transferRequest.whoRequested.id
                    this.changeReadyToGoTransferRequestId = transferposition.transferRequest.id
                    return true
                  }
                })
              }
            })
          })
        }
      },
      createTransferRequest () {
        this.loading = true
        this.changeReadyToGoMethod()
        this.$apollo.mutate({
          mutation: changeReadyToGo,
          variables: {
            input: {
              requestId: this.savedLogisticRequestId,
              transferRequestId: this.changeReadyToGoTransferRequestId
            }
          }
        }).then(({data}) => {
          if (data.changeReadyToGo.result) {
            this.loading = false
            this.createDialog = false
            this.$apollo.queries.query.refetch()
            // Зануление changeReadyToGoTransferRequestId обязательно ниже query.refetch'а
            this.changeReadyToGoTransferRequestId = null
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Создана заявка на перемещение'
            })
          }
        }).catch(() => {
          this.loading = false
        })
      },
      deleteTransferRequest () {
        this.loading = true
        this.changeReadyToGoMethod()
        this.$apollo.mutate({
          mutation: deleteTransferRequest,
          variables: {
            input: {
              transferRequestId: this.changeReadyToGoTransferRequestId
            }
          }
        }).then(({data}) => {
          if (data.deleteTransferRequest.result) {
            this.loading = false
            this.deleteDialog = false
            this.$apollo.queries.query.refetch()
            this.$apollo.queries.query2.refetch()
            this.$apollo.queries.query3.refetch()
            // Зануление changeReadyToGoTransferRequestId обязательно ниже query.refetch'а
            this.changeReadyToGoTransferRequestId = null
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Перемещение отменено'
            })
          }
        })
      },
      reload () {
        this.$apollo.queries.query.refetch()
        this.$apollo.queries.query2.refetch()
        this.$apollo.queries.query3.refetch()
      },
      openMoveDialog (goodKind, subRow) {
        this.createTransferPositionDialogShow = true
        let transferredOrReserved = 0
        subRow.transferpositionSet.forEach(item => {
          if (item.transferred === null) {
            transferredOrReserved += item.count
          } else {
            transferredOrReserved += item.transferred
          }
        })
        this.transferPositionData = {positionId: subRow.id, whereId: subRow.request.goal.project.id, inStock: subRow.inStock, needUnit: subRow.unit, needCount: subRow.count - transferredOrReserved}
      },
      openRequest (val) {
        window.open('logistic_request/' + val).focus()
      },
      openTask (req, task) {
        window.open('logistic_request/' + req + '#task' + task).focus()
      },
      openUserProfile (val) {
        this.$router.push({
          name: 'user',
          params: {id: val}
        })
      },
      tableHover (val, val2) {
        if (val.task && val.task.responsible && val.task.responsible.id !== auth.user.id) {
          this.hoverItem = null
          this.hoverItemColor = null
        } else {
          this.hoverItem = val.id
          this.hoverItemColor = val2.id
        }
        let transferredOrReserved = 0
        val.transferpositionSet.forEach(item => {
          if (item.transferred === null) {
            transferredOrReserved += item.count
          } else {
            transferredOrReserved += item.transferred
          }
        })
        this.transferredOrReserved = transferredOrReserved
      },
      openRequisit (val) {
        this.$router.push({
          name: 'transfer_request',
          params: {id: val}
        })
      },
      clearFilters () {
        this.logisticDeliveryFilter = {
          lateDelivery: false,
          overdue: false,
          rowStatus: null,
          expectedDate: {
            dateStart: null,
            dateEnd: null
          },
          deadline: {
            dateStart: null,
            dateEnd: null
          },
          orderDate: {
            dateStart: null,
            dateEnd: null
          },
          projects: [],
          responsible: [],
          workers: null,
          moved: null,
          countInStock: null,
          statusInStock: 'Меньше или равно'
        }
        this.pagination = {
          rowsPerPage: 25,
          descending: true,
          page: 1,
          totalItems: 0,
          sortBy: 'expectedDate'
        }
      },
      searchOperation: _.debounce(function () {
        this.searchText = this.searchQuery
      }, 500)
    },
    watch: {
      pagination: {
        handler: function (val) {
          this.storeValue('pagination', val)
        },
        deep: true
      },
      logisticDeliveryFilter: {
        handler: function (val) {
          this.storeValue('filter', val)
          if (val.countInStock === '') {
            val.countInStock = null
          }
          this.$apollo.queries.query.refetch()
          this.pagination.page = 1
        },
        deep: true
      },
      searchQuery: function () {
        this.searchOperation()
      },
      readyToGo: {
        handler: function (val) {
          if (val) {
            this.logisticDeliveryFilter.rowStatus = 'Готовые к перемещению'
            this.myActions = false
            this.myPartic = false
          }
          if (this.readyToGo === false && this.myActions === false && this.myPartic === false) {
            this.logisticDeliveryFilter.rowStatus = null
          }
        }
      },
      myActions: {
        handler: function (val) {
          if (val) {
            this.logisticDeliveryFilter.rowStatus = 'Ожидающие моих действий'
            this.readyToGo = false
            this.myPartic = false
          }
          if (this.readyToGo === false && this.myActions === false && this.myPartic === false) {
            this.logisticDeliveryFilter.rowStatus = null
          }
        }
      },
      myPartic: {
        handler: function (val) {
          if (val) {
            this.logisticDeliveryFilter.rowStatus = 'С моим участием'
            this.myActions = false
            this.readyToGo = false
          }
          if (this.readyToGo === false && this.myActions === false && this.myPartic === false) {
            this.logisticDeliveryFilter.rowStatus = null
          }
        }
      }
    }
  }
</script>

<style>

  div.header table thead tr th {
    font-size: 80%;
    word-wrap: break-word;
    white-space: normal;
  }

  div table tbody th {
    padding: 0;
  }

  .filter-padding {
    padding-left: 40px;
    padding-right: 40px
  }

  .block-width50 {
    width: 50px;
    min-width: 50px;
    max-width: 50px;
  }

  .block-width60 {
    width: 60px;
    min-width: 60px;
    max-width: 60px;
  }

  .block-width100 {
    width: 100px;
    min-width: 100px;
    max-width: 100px;

  }

  .block-width300 {
    width: 300px;
    min-width: 300px;
    max-width: 300px;

  }

  .table-font-size {
    font-size: 80%;
  }

  .locked .background {
    background-color: #ebe8d8 !important;
  }

  .locked .checked.background {
    background-color: #b8f077 !important;
  }

  .fired.background {
    background-color: #ff8a80 !important;
  }

  .checked {
    background-color: #b8f077 !important;
  }
  .lockedText {
    color: dimgray;
  }
</style>
