<template>
  <v-card>
    <v-card-title class="pa-0 pt-2">
      <div class="px-4" style="min-height: 36px">
        <span class="body-2 pr-5">Номер заявки: {{ logisticsRequestObject.id }}</span>
        <span class="body-2 pr-5">Проект: {{ logisticsRequestObject.project }}</span>
        <span class="body-2 pr-5">Цель закупки: <a :href="'/specification/' + logisticsRequestObject.reasonId"
                                                   target="_blank">{{ logisticsRequestObject.purpose }}</a></span>
        <span
          v-if="logisticsRequestObject.gipId === auth.user.id || logisticsRequestObject.responsible && logisticsRequestObject.responsible.length > 0"
          class="body-2">Ответственные:
          <users-chip :users="logisticsRequestObject.responsible"/>
          <v-btn v-if="logisticsRequestObject.gipId === auth.user.id" icon
                 @click="addResponsibleInLogisticsRequestDialogShow = true" class="my-0">
            <v-icon>add_circle</v-icon>
          </v-btn>
        </span>
      </div>
      <div class="px-4 py-2">
        <span class="body-2 pr-5">Дата создания: {{ formatDate(logisticsRequestObject.whenRequested) }}</span>
        <span class="body-2 pr-5">Крайний срок: {{ formatDate(logisticsRequestObject.deadline) }}</span>
        <span class="body-2">Запросил:
          <v-chip>
              <v-avatar>
                <img :src="formatURL(logisticsRequestObject.whoRequested.avatar)"/>
              </v-avatar>
              {{ logisticsRequestObject.whoRequested.shortName }}
          </v-chip>
        </span>
      </div>
      <div class="px-3" v-if="userIsResponsible">
        <v-btn :color="hasGroups ? 'deleted' : 'submit'"
               v-if="logisticsRequestPositionSetWithoutTasks.length > 0 || hasGroups"
               @click="createGroups(true)" small
        >
          {{ hasGroups ? 'Расформировать группы' : 'Сгруппировать позиции вне задач по производителям' }}
        </v-btn>
        <v-btn v-if="markedPositionWithoutTask" color="submit" @click="createTaskDialogShow = true" small>
          Создать задачу из выбранных позиций
        </v-btn>
        <v-btn small color="submit" title="Передать логистам"
               v-if="!logisticsRequestObject.readyForWork && userIsResponsible"
               @click="publishRequest">Передать в работу
        </v-btn>
        <v-btn color="submit" @click="addReplacePositionDialogShow = true; replacePosition=null" small>
          Добавить товар в заявку
        </v-btn>
      </div>


      <v-menu v-model="commentsDialogShow" :close-on-content-click="false" max-width="650px" max-height="800px">
        <v-card>
          <v-card-title class="title py-1 pr-1">
            Комментарии
            <v-spacer/>
            <v-btn icon @click="commentsDialogShow = false">
              <v-icon>close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text v-if="logisticsRequestObject.id" class="pt-0">
            <comments name="logistics.LogisticsRequest" :object-id="Number(logisticsRequestObject.id)"/>
          </v-card-text>
        </v-card>
        <v-btn large fab fixed bottom right color="secondary" slot="activator">
          <v-icon>comment</v-icon>
        </v-btn>
      </v-menu>

      <v-dialog v-model="addResponsibleInLogisticsRequestDialogShow" max-width="500px">
        <v-card>
          <v-card-title class="title">
            Добавление ответственного в заявку на закупку
          </v-card-title>
          <v-card-text>
            <workers-select label="Сотрудник" v-model="responsibleId"/>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn flat @click="addResponsibleInLogisticsRequestDialogShow = false">
              Отмена
            </v-btn>
            <v-btn flat @click="addResponsibleInLogisticsRequestFunc">Добавить</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="commonDialog" max-width="500px">
        <v-card>
          <v-card-title class="title">
            <span v-if="changeReadyToGoTransferRequestId">Создание заявки на перемещение</span>
            <span v-if="deleteTransferRequestId">Отмена перемещения</span>
            <span v-if="transferAllTaskId">Перемещение всего из наличия</span>
            <span v-if="disbandTaskId">Расформирование задачи</span>
            <span v-if="deletePositionFromTaskId">Удаление позиции из задачи</span>
            <span v-if="deletePositionFromLogisticsRequestId">Удаление позиции из заявки на закупку</span>
          </v-card-title>
          <v-card-text>
            <span v-if="changeReadyToGoTransferRequestId">Вы действительно хотите создать заявку на перемещение?</span>
            <span v-if="deleteTransferRequestId">Вы действительно хотите отменить перемещения?</span>
            <span v-if="transferAllTaskId">Вы действительно хотите переместить все из наличия?</span>
            <span v-if="disbandTaskId">Вы действительно хотите расформировать задачу?</span>
            <span v-if="deletePositionFromTaskId">Вы действительно хотите удалить позицию из задачи?</span>
            <span v-if="deletePositionFromLogisticsRequestId">Вы действительно хотите удалить позицию из заявки на закупку?</span>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn flat
                   @click="commonDialog=false; changeReadyToGoTransferRequestId=null;
                  deleteTransferRequestId=null; transferAllTaskId=null; disbandTaskId=null;
                  deletePositionFromTaskId=null; deletePositionFromLogisticsRequestId=null">
              Отмена
            </v-btn>
            <v-btn v-if="changeReadyToGoTransferRequestId" flat @click="changeReadyToGoFunc">Создать</v-btn>
            <v-btn v-if="deleteTransferRequestId" flat @click="deleteTransferRequestFunc">Отменить перемещение</v-btn>
            <v-btn v-if="transferAllTaskId" flat @click="transferAllFunc">Переместить</v-btn>
            <v-btn v-if="disbandTaskId" flat @click="disbandTaskFunc">Расформировать</v-btn>
            <v-btn v-if="deletePositionFromTaskId" flat @click="deletePositionFromTaskFunc">Удалить</v-btn>
            <v-btn v-if="deletePositionFromLogisticsRequestId" flat @click="deletePositionFromLogisticsRequestFunc">
              Удалить
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!--Диалог редактирования дат и количества-->
      <v-menu offset-y absolute :close-on-content-click="false" max-width="450px"
              :position-x="editDialogX" :position-y="editDialogY" v-model="editPositionDialogShow">
        <v-list class="px-3">

          <div>
            <span v-if="orderDateEdit || expectedDateEdit || deadlineDateEdit">Изменение даты</span>
            <span v-if="countUnitEdit">Изменение количества</span>
          </div>
          <div>
            <v-form v-model="editPositionFormValid">
              <date-picker v-if="orderDateEdit" label="Дата" v-model="orderDate" required :rules="nonEmptyField"/>
              <date-picker v-if="expectedDateEdit" label="Дата" v-model="expectedDate" required :rules="nonEmptyField"/>
              <date-picker v-if="deadlineDateEdit" label="Дата" v-model="deadline" required :rules="nonEmptyField"/>
              <float-field v-if="countUnitEdit" label="Количество" v-model="count" :rules="nonEmptyField"/>
              <v-select
                v-if="countUnitEdit"
                label="Единица измерения"
                v-model="unitId"
                :items="allUnitsData"
                item-text="name"
                item-value="id"
                clearable
                :rules="nonEmptyField"
              />
            </v-form>
          </div>
          <div>
            <v-btn flat @click="editPositionDialogShow=false; orderDateEdit=false; expectedDateEdit=false; deadlineDateEdit=false;
           countUnitEdit=false; orderDate=null; expectedDate=null; deadline=null; count=null; unitId=null">
              Отмена
            </v-btn>
            <v-btn flat :disabled="!editPositionFormValid" @click="editPositionFunc">Сохранить</v-btn>
          </div>
        </v-list>
      </v-menu>

      <!-- Окно для вывода позиций задачи списком -->
      <print-task-positions-dialog
        v-model="printTaskPositionsDialogShow"
        :positions="positionsToPrint"
      />

      <!--Меню изменения названия задач-->
      <v-menu offset-y absolute :close-on-content-click="false" max-width="450px"
              :position-x="editDialogX" :position-y="editDialogY" v-model="editTaskDialogShow">
        <v-list class="px-3">
          <v-form v-model="editTaskFormValid">
            <v-text-field label="Название задачи" v-model="editableTask.name" :rules="nonEmptyFieldTrim" required/>
          </v-form>
          <v-layout>
            <v-spacer/>
            <v-btn @click="closeEditTaskDialog" :disabled="loading">Отменить</v-btn>
            <v-btn @click="saveTaskName" color="submit" :loading="loading" :disabled="loading || !editTaskFormValid">
              Сохранить
            </v-btn>
          </v-layout>
        </v-list>
      </v-menu>

      <create-task-for-positions-dialog
        v-model="createTaskDialogShow"
        :positions="selectedPositions"
        @createTaskForPositionsSuccess="reload"
      />

      <add-replace-position-dialog
        v-model="addReplacePositionDialogShow"
        :request-id="logisticsRequestObject.id"
        :replace-position="replacePosition"
        @addPositionInLogisticsRequestSuccess="reload"
      />

      <create-transfer-position
        v-model="createTransferPositionDialogShow"
        :transferPositionData="transferPositionData"
        @createTransferPositionSuccess="reload"
      />
    </v-card-title>

    <v-card-text class="pa-0 pt-2">
      <v-data-table
        class="header-logistic-table"
        :headers="headers"
        :items="tasks"
        :loading="loadingQueriesCount > 0 ? 'loading' : false"
        :rows-per-page-text="'Строк на странице'"
        :no-data-text="'Нет доступных данных'"
        hide-actions
        :pagination.sync="pagination"
      >
        <template slot="items" slot-scope="props">
          <!--Шапка для позициций с задачами на закупку-->
          <tr
            :class="{procurementInfo: props.item.responsible, procurementWarning: !props.item.responsible, procurementComplete: props.item.taskCompleted}"
            style="height: 100px" v-if="props.item.id > 0">
            <td colspan="11" class="hover border-task">
              <table width="100%">
                <tr>
                  <!-- Кнопка разворачивания позиций задачи -->
                  <td style="width: 50px; padding: 0">
                    <v-btn icon v-if="props.item.show"
                           @click="props.item.show = false; openTasksId = openTasksId.filter(id => id !== props.item.id)">
                      <v-icon>arrow_drop_up</v-icon>
                    </v-btn>
                    <v-btn icon v-if="!props.item.show"
                           @click="props.item.show = true; openTasksId.push(props.item.id)">
                      <v-icon>arrow_drop_down</v-icon>
                    </v-btn>
                  </td>
                  <!-- Статус задачи -->
                  <td style="min-width: 130px; width: 130px">
                    <span class="body-2" v-if="props.item.responsible && !props.item.taskCompleted">В работе</span>
                    <span class="body-2"
                          v-if="!props.item.responsible && !props.item.workStarted && !props.item.taskCompleted">Сформирована</span>
                    <span class="body-2"
                          v-if="!props.item.responsible && props.item.workStarted && !props.item.taskCompleted">Не доработана</span>
                    <span class="body-2" v-if="props.item.taskCompleted">Выполнена</span>
                  </td>
                  <!-- Информация о задаче и действия с ней -->
                  <td :id="'task' + props.item.id" style="width: 50%;">
                    <!-- Верхняя полоса -->
                    <div>
                      <span class="body-2 pr-5">№ {{ props.item.id }}:
                        <span v-if="userIsResponsibleForTask(props.item)" style="cursor: pointer"
                              @click="openEditTaskDialog($event, props.item)">{{ props.item.name }}</span>
                        <template v-else>
                          {{ props.item.name }}
                        </template>
                      </span>
                      <span class="body-2 pr-5" v-if="props.item.responsible">Исполнитель:
                        <v-chip v-if="props.item.responsible">
                          <v-avatar>
                            <img :src="formatURL(props.item.responsible.avatar)"/>
                          </v-avatar>
                          {{ props.item.responsible.shortName }}
                        </v-chip>
                      </span>
                      <v-btn small color="submit"
                             v-if="auth.hasPermission('logistics.is_logist') && !props.item.responsible"
                             @click="takeTaskFunc(props.item.id)">
                        Взять в работу
                      </v-btn>
                      <v-btn small color="deleted"
                             v-if="props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                             @click="refuseTaskFunc(props.item.id)">
                        Отказаться
                      </v-btn>
                    </div>
                    <!-- Нижняя полоса -->
                    <div>
                      <span class="body-2 pr-5">Сформирована {{ formatDate(props.item.createdDate) }}</span>
                      <v-btn small color="deleted mr-3"
                             v-if="((props.item.responsible && auth.user.id === props.item.responsible.id) || ((!props.item.responsible && !props.item.workStarted) && (auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))))) && !props.item.workStarted
                       && props.item.files.length === 0 && !props.item.transferred && !props.item.replacement"
                             @click="commonDialog = true; disbandTaskId = props.item.id"
                      >
                        Расформировать задачу
                      </v-btn>
                      <v-btn small color="info"
                             v-if="props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                             @click.stop="printTask(props.item.id)">
                        Вывести позиции таблицей
                      </v-btn>
                    </div>
                  </td>
                  <!-- Кнопки перемещений -->
                  <td style="width: 286px; padding: 0;">
                    <div
                      v-if="!props.item.transferRequest && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted">
                      <v-btn small color="submit"
                             @click="commonDialog=true; transferAllTaskId=props.item.id"
                      >
                        Переместить все из наличия
                      </v-btn>
                    </div>
                    <div v-if="props.item.responsible && props.item.responsible.id === auth.user.id &&
                   props.item.transferredWithReadyToGoFalse && props.item.transferRequest && !props.item.transferRequest.readyToGo && !props.item.taskCompleted">
                      <v-btn small color="new"
                             @click="commonDialog=true; deleteTransferRequestId=props.item.transferRequest.id"
                      >
                        Отменить перемещения
                      </v-btn>
                    </div>
                    <div v-if="props.item.responsible && props.item.responsible.id === auth.user.id &&
                  props.item.transferRequest && !props.item.transferRequest.readyToGo && !props.item.taskCompleted">
                      <v-btn small color="new"
                             @click="commonDialog=true; changeReadyToGoTransferRequestId=props.item.transferRequest.id">
                        Создать заявку на перемещение
                      </v-btn>
                    </div>
                  </td>
                  <!-- Загрузка файла счета -->
                  <td>
                    <file-upload
                      style="width: 250px; height: 110px;"
                      caption="Счета"
                      :mutate="uploadIncomingOfferFile"
                      :variables="{taskId: props.item.id}"
                      :del-mutation="deleteIncomingOfferFile"
                      :read-result-from-data="data => data.deleteIncomingOfferFile.result"
                      :extractPath="result => result.uploadIncomingOfferFile.result"
                      v-model="props.item.files"
                      :max-num-files="1"
                      :clickable="((Boolean(props.item.responsible) && props.item.responsible.id === auth.user.id) || ((!props.item.responsible && !props.item.workStarted) && (auth.user.id === logisticsRequestObject.gipId || auth.user.id === logisticsRequestObject.whoRequested.id || Boolean(findLogisticsRequestResponsible(auth.user.id))))) && !props.item.taskCompleted"
                    />
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!--Позиции с задачей на закупку-->
          <template v-for="lrp in logisticsRequestObject.logisticsrequestpositionSet">
            <tr :class="{procurementComplete: lrp.transferred >= lrp.count}"
                v-if="lrp.task && props.item.id === lrp.task.id && props.item.show"
                @mouseover="positionWithTaskOverId = lrp.id"
                @mouseout="positionWithTaskOverId = null"
            >
              <template v-if="!lrp.replaced && !lrp.canceled">
                <td style="min-width: 133px" class="pr-0">
                  <v-icon v-if="positionWithTaskOverId !== lrp.id">subdirectory_arrow_right</v-icon>
                  <v-btn title="Замена позиции" class="mx-0 my-0" icon
                         v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || (!props.item.responsible && !props.item.workStarted && (auth.user.id === logisticsRequestObject.gipId || findLogisticsRequestResponsible(auth.user.id))))  && !props.item.taskCompleted"
                         @click="replacePosition = {id: lrp.id, taskId: props.item.id}; addReplacePositionDialogShow = true">
                    <v-icon>crop</v-icon>
                  </v-btn>
                  <v-btn title="Удаление позиции из задачи" class="mx-0 my-0" icon
                         v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || (!props.item.responsible && !props.item.workStarted && (auth.user.id === logisticsRequestObject.gipId || findLogisticsRequestResponsible(auth.user.id)))) && !props.item.taskCompleted"
                         @click="commonDialog = true; deletePositionFromTaskId=lrp.id">
                    <v-icon>delete</v-icon>
                  </v-btn>
                  <v-btn title="Удаление позиции из заявки" class="mx-0 my-0" icon
                         v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || (!props.item.responsible && !props.item.workStarted && (auth.user.id === logisticsRequestObject.gipId || findLogisticsRequestResponsible(auth.user.id)))) && !props.item.taskCompleted"
                         @click="commonDialog = true; deletePositionFromLogisticsRequestId=lrp.id">
                    <v-icon>delete_forever</v-icon>
                  </v-btn>
                </td>
                <td class="text-xs-center px-0 py-0">{{ lrp.number }}</td>
                <td width="400" class="px-0 py-0">
                  <span v-if="lrp.goodKind.goodGroup"><i>{{ lrp.goodKind.goodGroup.name }}</i>,</span>
                  <span v-if="lrp.goodKind.code"><i>{{ lrp.goodKind.code }}</i> -</span>
                  <span v-if="!lrp.goodKind.code">б/а -</span>
                  {{ lrp.goodKind.name }}
                </td>
                <td class="text-xs-center px-0 py-0">{{ lrp.goodKind.manufacturer.name }}</td>
                <td :class="{procurementWarning:lrp.deadline && Date.parse(lrp.deadline) < today}"
                    class="text-xs-center px-0 py-0">
                <span
                  v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"
                  @click="openEditDialog($event); editPositionId=lrp.id; editPositionDialogShow = true; deadlineDateEdit = true;"
                  style="cursor: pointer">{{ formatDate(lrp.deadline) }}</span>
                  <span v-else>{{ formatDate(lrp.deadline) }}</span>
                  <!--<v-btn title="Изменение необходимой даты поставки" icon-->
                  <!--v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"-->
                  <!--@click="editPositionDialogShow=true; editPositionId=lrp.id; deadlineDateEdit=true">-->
                  <!--<v-icon>edit</v-icon>-->
                  <!--</v-btn>-->
                </td>
                <td class="text-xs-center px-0 py-0">
                <span
                  v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"
                  @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; countUnitEdit=true;"
                  style="cursor: pointer">{{ lrp.count + ' ' + lrp.unit.shortName }}</span>
                  <span v-else>{{ lrp.count + ' ' + lrp.unit.shortName }}</span>
                  <!--<v-btn title="Изменение необходимого количества и единицы измерения" icon-->
                  <!--v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                  <!--@click="editPositionDialogShow=true; editPositionId=lrp.id; countUnitEdit=true">-->
                  <!--<v-icon>edit</v-icon>-->
                  <!--</v-btn>-->
                </td>
                <!--Есть на складе-->
                <td class="text-xs-center px-0 py-0">
                  <template v-for="is in removeUnitsDuplicatesForIteration(lrp.inStock, lrp.count)">
                    <logistic-hint
                      v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && is.unit.id === lrp.unit.id && is.available > 0 && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                      @click.native.stop="openMoveDialog(lrp.goodKind, lrp)" :position="lrp"/>
                    <logistic-hint v-else :position="lrp"/>
                  </template>
                  <!--<template v-for="is in removeUnitsDuplicatesForIteration(lrp.inStock, lrp.count)">-->
                  <!--<v-btn-->
                  <!--title="Перемещение"-->
                  <!--icon-->
                  <!--v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && is.unit.id === lrp.unit.id && is.available > 0 && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                  <!--@click.native.stop="openMoveDialog(lrp.goodKind, lrp)"-->
                  <!--&gt;-->
                  <!--<v-icon>launch</v-icon>-->
                  <!--</v-btn>-->
                  <!--</template>-->
                </td>
                <!--Перемещено-->
                <td class="text-xs-center px-0 py-0">
                  <logistic-hint :position="lrp" :isTransfer="true" :logisticRequest="true"/>
                </td>
                <td class="text-xs-center px-0 py-0">
                <span
                  v-if="!lrp.orderDate && lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                  @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; orderDateEdit=true"
                  style="cursor: pointer">-</span>
                  <span v-else-if="!lrp.orderDate">-</span>
                  <span
                    v-if="lrp.orderDate && lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; orderDateEdit=true"
                    style="cursor: pointer">{{ formatDate(lrp.orderDate) }}</span>
                  <span v-else-if="lrp.orderDate">{{ formatDate(lrp.orderDate) }}</span>
                  <!--<v-btn title="Изменение даты заказа" icon-->
                  <!--v-if="lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                  <!--@click="editPositionDialogShow=true; editPositionId=lrp.id; orderDateEdit=true">-->
                  <!--<v-icon>edit</v-icon>-->
                  <!--</v-btn>-->
                </td>
                <td
                  :class="{procurementWarning: Date.parse(today) > Date.parse(lrp.expectedDate) && lrp.count !== lrp.transferred}"
                  class="text-xs-center px-0 py-0">
                <span
                  v-if="!lrp.expectedDate && lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                  @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; expectedDateEdit=true"
                  style="cursor: pointer">-</span>
                  <span v-else-if="!lrp.expectedDate">-</span>
                  <span
                    v-if="lrp.expectedDate && lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; expectedDateEdit=true"
                    style="cursor: pointer">{{ formatDate(lrp.expectedDate) }}</span>
                  <span v-else-if="lrp.expectedDate">{{ formatDate(lrp.expectedDate) }}</span>
                  <!--<v-btn title="Изменение ожидаемой даты поставки" icon-->
                  <!--v-if="lrp.transferred < lrp.count && props.item.files.length > 0 && positionWithTaskOverId === lrp.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                  <!--@click="editPositionDialogShow=true; editPositionId=lrp.id; expectedDateEdit=true">-->
                  <!--<v-icon>edit</v-icon>-->
                  <!--</v-btn>-->
                </td>
                <td class="text-xs-center px-0 py-0">
                  <template v-if="!lrp.finishedDate">-</template>
                  <template v-if="lrp.finishedDate">{{ formatDate(lrp.finishedDate) }}</template>
                </td>
              </template>
              <template v-if="lrp.replaced || lrp.canceled">
                <td>
                  <v-icon v-if="positionWithTaskOverId !== lrp.id">subdirectory_arrow_right</v-icon>
                  <v-btn title="Замена позиции" class="mx-0 my-0" style="width: 36px" icon
                         v-if="positionWithTaskOverId === lrp.id
                       && ((props.item.responsible && props.item.responsible.id === auth.user.id)
                       || (!props.item.responsible && !props.item.workStarted && (auth.user.id === logisticsRequestObject.gipId
                       || findLogisticsRequestResponsible(auth.user.id)))) && !props.item.taskCompleted"
                         @click="replacePosition = {id: lrp.id, taskId: props.item.id}; addReplacePositionDialogShow = true">
                    <v-icon>crop</v-icon>
                  </v-btn>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <del>{{ lrp.number }}</del>
                </td>
                <td width="400" class="px-0 py-0">
                  <del>
                    <span v-if="lrp.goodKind.goodGroup"><i>{{ lrp.goodKind.goodGroup.name }}</i>,</span>
                    <span v-if="lrp.goodKind.code"><i>{{ lrp.goodKind.code }}</i> -</span>
                    <span v-if="!lrp.goodKind.code">б/а -</span>
                    {{ lrp.goodKind.name }}
                  </del>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <del>{{ lrp.goodKind.manufacturer.name }}</del>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <del>{{ formatDate(lrp.deadline) }}</del>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <del>{{ lrp.count + ' ' + lrp.unit.shortName }}</del>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <logistic-hint :position="lrp"/>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <logistic-hint :position="lrp" :isTransfer="true" :logisticRequest="true"/>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <template v-if="!lrp.orderDate">-</template>
                  <template v-if="lrp.orderDate">
                    <del>{{ formatDate(lrp.orderDate) }}</del>
                  </template>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <template v-if="!lrp.expectedDate">-</template>
                  <template v-if="lrp.expectedDate">
                    <del>{{ formatDate(lrp.expectedDate) }}</del>
                  </template>
                </td>
                <td class="text-xs-center px-0 py-0">
                  <template v-if="!lrp.finishedDate">-</template>
                  <template v-if="lrp.finishedDate">
                    <del>{{ formatDate(lrp.finishedDate) }}</del>
                  </template>
                </td>
              </template>
            </tr>

            <!--Новая Заменнённая позиция-->
            <template v-for="c in canceledPositions"
                      v-if="lrp.task && props.item.id === lrp.task.id && props.item.show">
              <template v-if="!c.replacement.canceled">
                <tr :class="{procurementComplete: c.replacement.transferred >= c.replacement.count}"
                    v-if="c.id === lrp.id" @mouseover="positionWithTaskOverId = c.replacement.id"
                    @mouseout="positionWithTaskOverId = null">
                  <td style="min-width: 133px" class="pr-0">
                    <v-icon class="ml-5" v-if="positionWithTaskOverId !== c.replacement.id">crop</v-icon>
                    <v-btn title="Удаление позиции из заявки" class="ml-5 my-0" icon
                           v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || (!props.item.responsible && !props.item.workStarted && (auth.user.id === logisticsRequestObject.gipId || findLogisticsRequestResponsible(auth.user.id)))) && !props.item.taskCompleted"
                           @click="commonDialog = true; deletePositionFromLogisticsRequestId=c.replacement.id">
                      <v-icon>delete_forever</v-icon>
                    </v-btn>
                  </td>
                  <td class="text-xs-center px-0 py-0">{{ c.replacement.number }}</td>
                  <td width="400" class="px-0 py-0">
                    <span
                      v-if="c.replacement.goodKind.goodGroup"><i>{{ c.replacement.goodKind.goodGroup.name }}</i>,</span>
                    <span v-if="c.replacement.goodKind.code"><i>{{ c.replacement.goodKind.code }}</i> -</span>
                    <span v-if="!c.replacement.goodKind.code">б/а -</span>
                    {{ c.replacement.goodKind.name }}
                  </td>
                  <td class="text-xs-center px-0 py-0">{{ c.replacement.goodKind.manufacturer.name }}</td>
                  <td
                    :class="{procurementWarning: c.replacement.deadline && Date.parse(c.replacement.deadline) < today}"
                    class="text-xs-center px-0 py-0">
                  <span
                    v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; deadlineDateEdit=true;"
                    style="cursor: pointer">{{ formatDate(c.replacement.deadline) }}</span>
                    <span v-else>{{ formatDate(c.replacement.deadline) }}</span>
                    <!--<v-btn title="Изменение необходимой даты поставки" icon-->
                    <!--v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; deadlineDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; countUnitEdit=true"
                    style="cursor: pointer">{{ c.replacement.count + ' ' + c.replacement.unit.shortName }}</span>
                    <span v-else>{{ c.replacement.count + ' ' + c.replacement.unit.shortName }}</span>
                    <!--<v-btn title="Изменение необходимого количества и единицы измерения" icon-->
                    <!--v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; countUnitEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <template
                      v-for="is in removeUnitsDuplicatesForIteration(c.replacement.inStock, c.replacement.count)">
                      <logistic-hint
                        v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && is.unit.id === c.replacement.unit.id && is.available > 0 && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                        @click.native.stop="openMoveDialog(c.replacement.goodKind, c.replacement)"
                        :position="c.replacement"/>
                      <logistic-hint v-else :position="c.replacement"/>
                    </template>
                    <!--<template v-for="is in removeUnitsDuplicatesForIteration(c.replacement.inStock, c.replacement.count)">-->
                    <!--<v-btn-->
                    <!--title="Перемещение"-->
                    <!--icon-->
                    <!--v-if="c.replacement.transferred < c.replacement.count && positionWithTaskOverId === c.replacement.id && is.unit.id === c.replacement.unit.id && is.available > 0 && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click.native.stop="openMoveDialog(c.replacement.goodKind, c.replacement)"-->
                    <!--&gt;-->
                    <!--<v-icon>launch</v-icon>-->
                    <!--</v-btn>-->
                    <!--</template>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <logistic-hint :position="c.replacement" :isTransfer="true" :logisticRequest="true"/>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="!c.replacement.orderDate && c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true"
                    style="cursor: pointer">-</span>
                    <span v-else-if="!c.replacement.orderDate">-</span>
                    <span
                      v-if="c.replacement.orderDate && c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                      @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true"
                      style="cursor: pointer">{{ formatDate(c.replacement.orderDate) }}</span>
                    <span v-else-if="c.replacement.orderDate">{{ formatDate(c.replacement.orderDate) }}</span>
                    <!--<v-btn title="Изменение даты заказа" icon-->
                    <!--v-if="c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td
                    :class="{procurementWarning: Date.parse(today) > Date.parse(c.replacement.expectedDate) && c.replacement.count !== c.replacement.transferred}"
                    class="text-xs-center px-0 py-0">
                  <span
                    v-if="!c.replacement.expectedDate && c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true"
                    style="cursor: pointer">-</span>
                    <span v-else-if="!c.replacement.expectedDate">-</span>
                    <span
                      v-if="c.replacement.expectedDate && c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                      @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true"
                      style="cursor: pointer">{{ formatDate(c.replacement.expectedDate) }}</span>
                    <span v-else-if="c.replacement.expectedDate">{{ formatDate(c.replacement.expectedDate) }}</span>
                    <!--<v-btn title="Изменение ожидаемой даты поставки" icon-->
                    <!--v-if="c.replacement.transferred < c.replacement.count && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <template v-if="!c.replacement.finishedDate">-</template>
                    <template v-if="c.replacement.finishedDate">{{ formatDate(c.replacement.finishedDate) }}</template>
                  </td>
                </tr>
              </template>
              <!-- Отмененная или замененная позиция -->
              <template v-if="c.replacement.canceled">
                <tr v-if="c.id === lrp.id" @mouseover="positionWithTaskOverId = c.replacement.id"
                    @mouseout="positionWithTaskOverId = null">
                  <td style="min-width: 133px" class="pr-0">
                    <v-icon class="ml-5" v-if="positionWithTaskOverId !== c.replacement.id">crop</v-icon>
                    <v-btn title="Удаление позиции из заявки" class="ml-5 my-0" icon
                           v-if="positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                           @click="commonDialog = true; deletePositionFromLogisticsRequestId=c.replacement.id">
                      <v-icon>delete_forever</v-icon>
                    </v-btn>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <del>{{ c.replacement.number }}</del>
                  </td>
                  <td width="400" class="px-0 py-0">
                    <del>
                      <span v-if="c.replacement.goodKind.goodGroup"><i>{{ c.replacement.goodKind.goodGroup.name }}</i>,</span>
                      <span v-if="c.replacement.goodKind.code"><i>{{ c.replacement.goodKind.code }}</i> -</span>
                      <span v-if="!c.replacement.goodKind.code">б/а -</span>
                      {{ c.replacement.goodKind.name }}
                    </del>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <del>{{ c.replacement.goodKind.manufacturer.name }}</del>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="positionWithTaskOverId === c.replacement.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; deadlineDateEdit=true"
                    style="cursor: pointer"><del>{{ formatDate(c.replacement.deadline) }}</del></span>
                    <span v-else><del>{{ formatDate(c.replacement.deadline) }}</del></span>
                    <!--<v-btn title="Изменение необходимой даты поставки" icon-->
                    <!--v-if="positionWithTaskOverId === c.replacement.id && ((props.item.responsible && props.item.responsible.id === auth.user.id) || auth.user.id === logisticsRequestObject.gipId || Boolean(findLogisticsRequestResponsible(auth.user.id))) && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; deadlineDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; countUnitEdit=true"
                    style="cursor: pointer"><del>{{ c.replacement.count + ' ' + c.replacement.unit.shortName }}</del></span>
                    <span v-else><del>{{ c.replacement.count + ' ' + c.replacement.unit.shortName }}</del></span>

                    <!--<v-btn title="Изменение необходимого количества и единицы измерения" icon-->
                    <!--v-if="positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; countUnitEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <logistic-hint :position="c.replacement"/>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <logistic-hint :position="c.replacement" :isTransfer="true" :logisticRequest="true"/>
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="!c.replacement.orderDate && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true"
                    style="cursor: pointer">-</span>
                    <span v-else-if="!c.replacement.orderDate">-</span>
                    <span
                      v-if="c.replacement.orderDate && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                      @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true"
                      style="cursor: pointer"><del>{{ formatDate(c.replacement.orderDate) }}</del></span>
                    <span v-else-if="c.replacement.orderDate"><del>{{ formatDate(c.replacement.orderDate) }}</del></span>
                    <!--<v-btn title="Изменение даты заказа" icon-->
                    <!--v-if="props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; orderDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                  <span
                    v-if="!c.replacement.expectedDate && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                    @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true"
                    style="cursor: pointer">-</span>
                    <span v-else-if="!c.replacement.expectedDate">-</span>
                    <span
                      v-if="c.replacement.expectedDate && props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"
                      @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true"
                      style="cursor: pointer"><del>{{ formatDate(c.replacement.expectedDate) }}</del></span>
                    <span v-else-if="c.replacement.expectedDate"><del>{{ formatDate(c.replacement.expectedDate) }}</del></span>
                    <!--<v-btn title="Изменение ожидаемой даты поставки" icon-->
                    <!--v-if="props.item.files.length > 0 && positionWithTaskOverId === c.replacement.id && props.item.responsible && props.item.responsible.id === auth.user.id && !props.item.taskCompleted"-->
                    <!--@click="editPositionDialogShow=true; editPositionId=c.replacement.id; expectedDateEdit=true">-->
                    <!--<v-icon>edit</v-icon>-->
                    <!--</v-btn>-->
                  </td>
                  <td class="text-xs-center px-0 py-0">
                    <template v-if="!c.replacement.finishedDate">-</template>
                    <template v-if="c.replacement.finishedDate">
                      <del>{{ formatDate(c.replacement.finishedDate) }}</del>
                    </template>
                  </td>
                </tr>
              </template>
            </template>
          </template>

          <!--Шапка для групп-->
          <tr style="height: 100px;" v-if="props.item.id < 0">
            <td colspan="11" class="hover">
              <table width="100%">
                <tr>
                  <td>
                    <v-btn icon v-if="props.item.show" @click="props.item.show = false">
                      <v-icon>arrow_drop_up</v-icon>
                    </v-btn>
                    <v-btn icon v-if="!props.item.show" @click="props.item.show = true">
                      <v-icon>arrow_drop_down</v-icon>
                    </v-btn>
                  </td>
                  <td>
                    <div>Группа по производителю: {{ props.item.manufacturer }}</div>
                    <div class="ml-5">
                      <v-btn class="submit" @click="createTaskForPositionsFromGroup(props.item.id)">Создать задачу
                      </v-btn>
                      <v-btn class="deleted" @click="deleteGroup(props.item.id)">Расформировать</v-btn>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!--Позиции для групп-->
          <template v-for="g in groups" v-if="props.item.id < 0 && props.item.show">
            <tr v-for="lrp in g.positions" v-if="g.id === props.item.id" @mouseover="groupPositionOverId = lrp.id"
                @mouseout="groupPositionOverId = 0">
              <td>
                <v-btn title="Удаление позиции из группировки" class="mx-0 my-0" v-if="groupPositionOverId === lrp.id"
                       icon @click="deletePositionFromGroup(g.id, lrp.id)">
                  <v-icon>delete</v-icon>
                </v-btn>
              </td>
              <td class="text-xs-center px-0 py-0">{{ lrp.number }}</td>
              <td width="400" class="px-0 py-0">
                <span v-if="lrp.goodKind.goodGroup"><i>{{ lrp.goodKind.goodGroup.name }}</i>,</span>
                <span v-if="lrp.goodKind.code"><i>{{ lrp.goodKind.code }}</i> -</span>
                <span v-if="!lrp.goodKind.code">б/а -</span>
                {{ lrp.goodKind.name }}
              </td>
              <td class="text-xs-center px-0 py-0">{{ lrp.goodKind.manufacturer.name }}</td>
              <td class="text-xs-center px-0 py-0">{{ formatDate(lrp.deadline) }}</td>
              <td class="text-xs-center px-0 py-0">{{ lrp.count + ' ' + lrp.unit.shortName }}</td>
              <td class="text-xs-center px-0 py-0">
                <logistic-hint :position="lrp"/>
              </td>
              <td class="text-xs-center px-0 py-0">-</td>
              <td class="text-xs-center px-0 py-0">
                <template v-if="!lrp.orderDate">-</template>
                <template v-if="lrp.orderDate">{{ formatDate(lrp.orderDate) }}</template>
              </td>
              <td class="text-xs-center px-0 py-0">
                <template v-if="!lrp.expectedDate">-</template>
                <template v-if="lrp.expectedDate">{{ formatDate(lrp.expectedDate) }}</template>
              </td>
              <td class="text-xs-center px-0 py-0">
                <template v-if="!lrp.finishedDate">-</template>
                <template v-if="lrp.finishedDate">{{ formatDate(lrp.finishedDate) }}</template>
              </td>
            </tr>
          </template>

          <!--Шапка для позициций без задач на закупку-->
          <tr class="procurementWarning" style="height: 50px;" v-if="props.item.id === 0">
            <td colspan="11" class="hover">
              <table width="100%">
                <tr>
                  <td width="20px">
                    <v-btn icon v-if="props.item.show" @click="props.item.show = false">
                      <v-icon>arrow_drop_up</v-icon>
                    </v-btn>
                    <v-btn icon v-if="!props.item.show" @click="props.item.show = true">
                      <v-icon>arrow_drop_down</v-icon>
                    </v-btn>
                  </td>
                  <td>
                    <div class="text-xs-center body-2">Позиции без задач на закупку</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!--Позиции без задач на закупку-->
          <tr v-for="lrp in logisticsRequestPositionSetWithoutTasks"
              v-if="!lrp.task && props.item.id === 0 && props.item.show"
              @mouseover="positionWithTaskOverId = lrp.id"
              @mouseout="positionWithTaskOverId = null">
            <td class="pr-0 pl-3 py-0">
              <div style="display: flex">
                <v-checkbox v-model="lrp.selected" title="Отметить для добавления в задачу" style="max-width: 36px"/>
              </div>
            </td>
            <td class="text-xs-center px-0 py-0">{{ lrp.number }}</td>
            <td width="400" class="px-0 py-0">
              <span v-if="lrp.goodKind.goodGroup"><i>{{ lrp.goodKind.goodGroup.name }}</i>,</span>
              <span v-if="lrp.goodKind.code"><i>{{ lrp.goodKind.code }}</i> -</span>
              <span v-if="!lrp.goodKind.code">б/а -</span>
              {{ lrp.goodKind.name }}
            </td>
            <td class="text-xs-center px-0 py-0">{{ lrp.goodKind.manufacturer.name }}</td>
            <td
              :class="{procurementWarning: lrp.deadline && Date.parse(lrp.deadline) < today}"
              class="text-xs-center px-0 py-0">
              <span
                v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && userIsResponsible"
                @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; deadlineDateEdit=true"
                style="cursor: pointer">{{ formatDate(lrp.deadline) }}</span>
              <span v-else>{{ formatDate(lrp.deadline) }}</span>
            </td>
            <td class="text-xs-center px-0 py-0">
              <span
                v-if="lrp.transferred < lrp.count && positionWithTaskOverId === lrp.id && userIsResponsible"
                @click="openEditDialog($event); editPositionDialogShow=true; editPositionId=lrp.id; countUnitEdit=true"
                style="cursor: pointer">{{ lrp.count + ' ' + lrp.unit.shortName }}</span>
              <span v-else>{{ lrp.count + ' ' + lrp.unit.shortName }}</span>
            </td>
            <td class="text-xs-center px-0 py-0">
              <logistic-hint :position="lrp"/>
            </td>
            <td class="text-xs-center px-0 py-0">-</td>
            <td class="text-xs-center px-0 py-0">
              <template v-if="!lrp.orderDate">-</template>
              <template v-if="lrp.orderDate">{{ formatDate(lrp.orderDate) }}</template>
            </td>
            <td class="text-xs-center px-0 py-0">
              <template v-if="!lrp.expectedDate">-</template>
              <template v-if="lrp.expectedDate">{{ formatDate(lrp.expectedDate) }}</template>
            </td>
            <td class="text-xs-center px-0 py-0">
              <template v-if="!lrp.finishedDate">-</template>
              <template v-if="lrp.finishedDate">{{ formatDate(lrp.finishedDate) }}</template>
            </td>
          </tr>

        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
  import {
    getLogisticsRequest,
    refuseTask,
    takeTask,
    disbandTask,
    renameTask,
    publishRequest,
    changeReadyToGo,
    deleteTransferRequest,
    transferAll,
    editPosition,
    uploadIncomingOfferFile,
    addResponsibleInLogisticsRequest,
    deletePositionFromTask,
    deletePositionFromLogisticsRequest,
    deleteIncomingOfferFile
  } from './query'
  import {units} from '../storage/query'
  import utilMixin from '../utils'
  import auth from '../../auth/auth'
  import FileUpload from '../FileUpload'
  import CreateTaskForPositionsDialog from './CreateTaskForPositionsDialog'
  import AddReplacePositionDialog from './AddReplacePositionDialog'
  import CreateTransferPosition from './CreateTransferPosition'
  import DatePicker from '../DatePicker'
  import WorkersSelect from '../WorkersSelect'
  import FloatField from '../FloatField'
  import Comments from '../comments/Comments'
  import StorageSelect from '../StorageSelect'
  import LogisticHint from './LogisticHint'
  import UsersChip from '../UsersChip'
  import printTaskPositionsDialog from './PrintTaskPositionsDialog'

  export default {
    components: {
      StorageSelect,
      Comments,
      FloatField,
      WorkersSelect,
      DatePicker,
      CreateTransferPosition,
      AddReplacePositionDialog,
      CreateTaskForPositionsDialog,
      FileUpload,
      LogisticHint,
      UsersChip,
      printTaskPositionsDialog
    },
    name: 'logistics-request',
    metaInfo () {
      return {
        title: this.title
      }
    },
    mixins: [utilMixin],
    apollo: {
      getLogisticsRequestQuery: {
        fetchPolicy: 'network-only',
        pollInterval: 30000,
        query: getLogisticsRequest,
        variables () {
          return {
            id: this.$route.params.id
          }
        },
        update (data) {
          this.tasks = []
          this.canceledPositions = []
          // Сохраняем выделенные позиции без задач на закупку
          const selectedPositionsWithoutTask = this.logisticsRequestPositionSetWithoutTasks.filter(i => i.selected)
          this.logisticsRequestPositionSetWithoutTasks = []
          this.logisticsRequestObject = JSON.parse(JSON.stringify(data.getLogisticsRequest))
          let withoutPosition = false
          this.logisticsRequestObject.logisticsrequestpositionSet.forEach(item => {
            if (!item.task) {
              withoutPosition = true
              let obj = JSON.parse(JSON.stringify(item))
              obj.selected = false
              this.logisticsRequestPositionSetWithoutTasks.push(obj)
            }
            if (item.task) {
              if (item.canceledPosition) {
                this.canceledPositions.push({id: item.canceledPosition.id, replacement: item})
              }
            }
            const find = this.tasks.find(task => item.task && task.id === item.task.id)
            if (!find && item.task) {
              let obj = JSON.parse(JSON.stringify(item.task))
              // "show" - значение, от которого зависит показ позиций
              if (this.openTasksId.find(id => id === obj.id)) {
                obj.show = true
              } else {
                obj.show = false
              }
              // Добавляем задачу, если ее еще нет
              this.tasks.push(obj)
            }
          })
          // Восстанавливаем выделенные позиции без задач на закупку
          this.logisticsRequestPositionSetWithoutTasks.forEach(i => {
            i.selected = selectedPositionsWithoutTask.some(item => item.id === i.id)
          })
          let array = []
          this.logisticsRequestObject.logisticsrequestpositionSet.forEach(lrp => {
            let value = false
            this.canceledPositions.forEach(c => {
              if (c.replacement.id === lrp.id) {
                value = true
              }
              if (c.id === lrp.id) {
                lrp.replaced = true
              }
            })
            if (!value) {
              array.push(lrp)
            }
          })
          this.logisticsRequestObject.logisticsrequestpositionSet = array
          // Шапка для позициций без задач на закупку
          if (withoutPosition) {
            this.tasks.push({id: 0, show: true})
          }
          // Чтобы сработал watch
          this.pagination.sortBy = 'deadline'
          // Якорь на задачу
          this.$nextTick(() => {
            let href = window.location.hash.replace('#', '')
            if (href) {
              document.getElementById(href).scrollIntoView({block: 'end'})
              let data = this.tasks.find(item => {
                return item.id === href.slice(4)
              })
              data.show = true
              this.openTasksId.push(href.slice(4))
            }
          })
          if (this.groups.length > 0) {
            this.createGroups()
          }
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
        title: 'Заявка на закупку № ' + this.$route.params.id,
        auth: auth,
        today: new Date().setHours(0, 0, 0, 0),
        createTaskDialogShow: false,
        addReplacePositionDialogShow: false,
        createTransferPositionDialogShow: false,
        commonDialog: false,
        editPositionDialogShow: false,
        addResponsibleInLogisticsRequestDialogShow: false,
        commentsDialogShow: false,
        printTaskPositionsDialogShow: false,
        positionsToPrint: null,
        uploadIncomingOfferFile: uploadIncomingOfferFile,
        deleteIncomingOfferFile: deleteIncomingOfferFile,
        headers: [
          {text: '', align: 'left', sortable: false},
          {text: '№ п/п', align: 'center', sortable: false},
          {text: 'Товар', align: 'center', sortable: false},
          {text: 'Производитель', align: 'center', value: 'manufacturer'},
          {text: 'Необходимая дата поставки', align: 'center', value: 'deadline'},
          {text: 'Необходимое количество', align: 'center', sortable: false},
          {text: 'Есть на складе', align: 'center', sortable: false},
          {text: 'Перемещено', align: 'center', sortable: false},
          {text: 'Заказано', align: 'center', sortable: false},
          {text: 'Ожидаемая дата поставки', align: 'center', sortable: false},
          {text: 'Фактическая дата поставки', align: 'center', sortable: false}
        ],
        pagination: {
          descending: false,
          sortBy: null,
          page: 1,
          rowsPerPage: 300
        },
        editPositionFormValid: false,
        groupPositionOverId: null,
        positionWithTaskOverId: null,
        replacePosition: null,
        transferPositionData: null,
        changeReadyToGoTransferRequestId: null,
        deleteTransferRequestId: null,
        deletePositionFromTaskId: null,
        deletePositionFromLogisticsRequestId: null,
        transferAllTaskId: null,
        disbandTaskId: null,
        editPositionId: null,
        allUnitsData: [],
        tasks: [],
        groups: [],
        canceledPositions: [],
        responsibleId: null,
        logisticsRequestObject: {
          id: null,
          project: null,
          purpose: null,
          responsible: null,
          whenRequested: null,
          deadline: null,
          whoRequested: {
            id: null,
            shortName: null
          },
          logisticsrequestpositionSet: null,
          goal: null,
          readyForWork: false
        },
        openTasksId: [],
        logisticsRequestPositionSetWithoutTasks: [],
        selectedPositions: [],
        loadingQueriesCount: 0,
        whereId: null,
        newLocationName: null,
        orderDate: null,
        expectedDate: null,
        deadline: null,
        count: null,
        unitId: null,
        orderDateEdit: false,
        expectedDateEdit: false,
        deadlineDateEdit: false,
        countUnitEdit: false,
        editDialogX: null,
        editDialogY: null,
        editableTask: {
          id: null,
          name: null
        },
        editTaskDialogShow: false,
        editTaskFormValid: false,
        loading: false,
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        nonEmptyFieldTrim: [
          text => {
            if (!text || !text.trim()) {
              return 'Поле не может быть пустым'
            } else {
              return true
            }
          }
        ]
      }
    },
    computed: {
      // Убирает или показывает кнопку "Создать задачу из выбранных позиций"
      markedPositionWithoutTask () {
        let value = false
        this.selectedPositions = []
        this.logisticsRequestPositionSetWithoutTasks.forEach(lrp => {
          if (lrp.selected) {
            this.selectedPositions.push(lrp.id)
            value = true
          }
        })
        return value
      },
      userIsResponsible () {
        return auth.user.id === this.logisticsRequestObject.gipId ||
          auth.user.id === this.logisticsRequestObject.whoRequested.id ||
          this.findLogisticsRequestResponsible(auth.user.id)
      },
      hasGroups () {
        return this.groups.length > 0
      }
    },
    watch: {
      'pagination.descending': function (val) {
        if (this.pagination.sortBy === 'manufacturer') {
          if (val) {
            this.logisticsRequestObject.logisticsrequestpositionSet.sort((a, b) => a.goodKind.manufacturer.name < b.goodKind.manufacturer.name)
          } else {
            this.logisticsRequestObject.logisticsrequestpositionSet.sort((a, b) => a.goodKind.manufacturer.name > b.goodKind.manufacturer.name)
          }
        }
        if (this.pagination.sortBy === 'deadline') {
          if (val) {
            this.logisticsRequestObject.logisticsrequestpositionSet.sort((a, b) => Date.parse(a.deadline) < Date.parse(b.deadline))
          } else {
            this.logisticsRequestObject.logisticsrequestpositionSet.sort((a, b) => Date.parse(a.deadline) > Date.parse(b.deadline))
          }
        }
        return val
      }
    },
    methods: {
      // Метод проверяющий ответственного за конкретную задачу:
      // Если ответственный в задаче есть, то права на редактирование (или что там у вас) только у него
      // Если ответственного в задаче нет, то проверяются ответственные за заявку
      userIsResponsibleForTask (task) {
        if (task.responsible) {
          return task.responsible.id === auth.user.id
        } else {
          return this.userIsResponsible
        }
      },
      // Метод открытия диалогов редактирования дат или количества
      openEditDialog (event) {
        this.editDialogX = event.clientX
        this.editDialogY = event.clientY
        // Зануление значений предыдущего вызова окна редактирования
        this.orderDateEdit = false
        this.expectedDateEdit = false
        this.deadlineDateEdit = false
        this.countUnitEdit = false
        this.orderDate = null
        this.expectedDate = null
        this.deadline = null
        this.count = null
        this.unitId = null
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
        this.transferPositionData = {
          positionId: subRow.id,
          whereId: this.logisticsRequestObject.goal.project.id,
          inStock: subRow.inStock,
          needUnit: subRow.unit,
          needCount: subRow.count - transferredOrReserved
        }
      },
      // Открывает диалог редактирования названия задач
      openEditTaskDialog (event, item) {
        this.editDialogX = event.clientX
        this.editDialogY = event.clientY
        this.editableTask.id = item.id
        this.editableTask.name = item.name
        this.editTaskDialogShow = true
      },
      // Закрывает диалог редактирования названия задач
      closeEditTaskDialog () {
        this.editableTaskName = null
        this.editTaskDialogShow = false
      },
      // Функция сохраняющуя введенное название задачи
      saveTaskName () {
        this.loading = true
        this.$apollo.mutate({
          mutation: renameTask,
          variables: {
            input: {
              taskId: this.editableTask.id,
              name: this.editableTask.name
            }
          }
        }).then(({data}) => {
          this.loading = false
          if (data.renameTask.result) {
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: `Задача № ${this.editableTask.id} переименована`
            })
            this.closeEditTaskDialog()
          }
        }).catch(() => {
          this.loading = false
        })
      },
      // Убирает дубликаты кнопок перемещения, если на складе есть несколько позиций с "restrict_sum=True"
      removeUnitsDuplicatesForIteration (array, count) {
        let newArray = []
        const sortedArray = array.slice(0).sort((a, b) => a.available - b.available)
        sortedArray.forEach(e => {
          let find = newArray.find(ne => ne.unit.id === e.unit.id)
          if (!find) {
            newArray.push(e)
          } else {
            let less = false
            if (find.available < count) {
              less = true
              newArray = newArray.filter(ne2 => ne2.unit.id !== find.unit.id)
            }
            // Убирает баг когда все позиции на складе меньше, чем требуемое количество
            // if (e.available >= count && less) {
            if (less) {
              newArray.push(e)
            }
          }
        })
        return newArray
      },
      findLogisticsRequestResponsible (id) {
        if (this.logisticsRequestObject.responsible) {
          return this.logisticsRequestObject.responsible.some(r => r.id === id)
        } else {
          return false
        }
      },
      reload () {
        this.$apollo.queries.getLogisticsRequestQuery.refetch()
      },
      createTaskForPositionsFromGroup (id) {
        this.groups.forEach(g => {
          if (g.id === id) {
            this.selectedPositions = g.positions.map(p => p.id)
          }
        })
        this.createTaskDialogShow = true
      },
      createGroups (disband) {
        // Расформировать группы если они сформированы
        if (this.hasGroups && !!disband) {
          while (this.groups.length) {
            this.deleteGroup(this.groups[0].id)
          }
          return
        }
        this.groups = []
        let positionsWithoutTasks = this.tasks.find(task => task.id === 0)
        if (positionsWithoutTasks) {
          this.tasks.pop()
        }
        this.logisticsRequestPositionSetWithoutTasks.forEach(item => {
          const find = this.tasks.find(task => task.manufacturer && task.manufacturer === item.goodKind.manufacturer.name)
          if (!find) {
            let positions = this.logisticsRequestPositionSetWithoutTasks.filter(itemF => itemF.goodKind.manufacturer.name === item.goodKind.manufacturer.name)
            let id = Math.random() * (-1000 - -1) + -1
            this.tasks.push({
              id: id,
              manufacturer: item.goodKind.manufacturer.name,
              show: false
            })
            this.groups.push({
              id: id,
              positions: positions
            })
            let lrpswt = []
            this.logisticsRequestPositionSetWithoutTasks.forEach(lrpwt => {
              let find = positions.find(p => p.id === lrpwt.id)
              if (!find) {
                lrpswt.push(lrpwt)
              }
            })
            this.logisticsRequestPositionSetWithoutTasks = lrpswt
          }
        })
        this.tasks.push(positionsWithoutTasks)
        if (this.logisticsRequestPositionSetWithoutTasks.length === 0) {
          this.tasks.pop()
        }
      },
      deleteGroup (id) {
        let group = this.groups.find(g => g.id === id)
        if (group) {
          group.positions.forEach(p => this.logisticsRequestPositionSetWithoutTasks.push(p))
        }
        this.groups = this.groups.filter(g => g.id !== id)
        this.tasks = this.tasks.filter(t => t.id !== id)
        let findTaskForPositionsWithoutTasks = this.tasks.find(task => task.id === 0)
        if (!findTaskForPositionsWithoutTasks) {
          this.tasks.push({id: 0, show: true})
        }
      },
      refuseTaskFunc (taskId) {
        this.$apollo.mutate({
          mutation: refuseTask,
          variables: {
            input: {
              taskId: taskId
            }
          }
        }).then(({data}) => {
          if (data.refuseTask.result) {
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Вы отказались от задачи'
            })
          }
        })
      },
      takeTaskFunc (taskId) {
        this.$apollo.mutate({
          mutation: takeTask,
          variables: {
            input: {
              taskId: taskId
            }
          }
        }).then(({data}) => {
          if (data.takeTask.result) {
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Задача взята в работу'
            })
          }
        })
      },
      disbandTaskFunc () {
        this.$apollo.mutate({
          mutation: disbandTask,
          variables: {
            input: {
              taskId: this.disbandTaskId
            }
          }
        }).then(({data}) => {
          if (data.disbandTask.result) {
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Задача расформирована'
            })
          }
        })
      },
      changeReadyToGoFunc () {
        this.$apollo.mutate({
          mutation: changeReadyToGo,
          variables: {
            input: {
              requestId: this.logisticsRequestObject.id,
              transferRequestId: this.changeReadyToGoTransferRequestId
            }
          }
        }).then(({data}) => {
          if (data.changeReadyToGo.result) {
            this.newLocationName = null
            this.whereId = null
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Создана заявка на перемещение'
            })
          }
        })
      },
      deleteTransferRequestFunc () {
        this.$apollo.mutate({
          mutation: deleteTransferRequest,
          variables: {
            input: {
              transferRequestId: this.deleteTransferRequestId
            }
          }
        }).then(({data}) => {
          if (data.deleteTransferRequest.result) {
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Перемещение отменено'
            })
          }
        })
      },
      transferAllFunc () {
        let positionsId = []
        this.logisticsRequestObject.logisticsrequestpositionSet.forEach(lrp => {
          if (lrp.task && lrp.task.id === this.transferAllTaskId) {
            let value = false
            this.canceledPositions.forEach(clrp => {
              if (lrp.id === clrp.id) {
                value = true
                positionsId.push(clrp.replacement.id)
              }
            })
            if (!value) {
              positionsId.push(lrp.id)
            }
          }
        })
        this.$apollo.mutate({
          mutation: transferAll,
          variables: {
            input: {
              requestId: this.logisticsRequestObject.id,
              positionsId: positionsId
            }
          }
        }).then(({data}) => {
          if (data.transferAll.result) {
            this.newLocationName = null
            this.whereId = null
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Создана заявка на перемещение'
            })
          }
        })
      },
      editPositionFunc () {
        this.$apollo.mutate({
          mutation: editPosition,
          variables: {
            input: {
              positionId: this.editPositionId,
              orderDate: this.orderDate,
              expectedDate: this.expectedDate,
              deadline: this.deadline,
              count: this.count,
              unitId: this.unitId
            }
          }
        }).then(({data}) => {
          if (data.editPosition.result) {
            this.editPositionDialogShow = false
            this.orderDate = null
            this.expectedDate = null
            this.deadline = null
            this.count = null
            this.unitId = null
            this.orderDateEdit = false
            this.expectedDateEdit = false
            this.deadlineDateEdit = false
            this.countUnitEdit = false
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Значение изменено'
            })
          }
        })
      },
      addResponsibleInLogisticsRequestFunc () {
        this.$apollo.mutate({
          mutation: addResponsibleInLogisticsRequest,
          variables: {
            input: {
              requestId: this.logisticsRequestObject.id,
              workerId: this.responsibleId
            }
          }
        }).then(({data}) => {
          if (data.addResponsibleInLogisticsRequest.result) {
            this.addResponsibleInLogisticsRequestDialogShow = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Ответственный добавлен'
            })
          }
        })
      },
      deletePositionFromTaskFunc () {
        this.$apollo.mutate({
          mutation: deletePositionFromTask,
          variables: {
            input: {
              positionId: this.deletePositionFromTaskId
            }
          }
        }).then(({data}) => {
          if (data.deletePositionFromTask.result) {
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Позиция удалена из задачи'
            })
          }
        })
      },
      deletePositionFromLogisticsRequestFunc () {
        this.$apollo.mutate({
          mutation: deletePositionFromLogisticsRequest,
          variables: {
            input: {
              positionId: this.deletePositionFromLogisticsRequestId
            }
          }
        }).then(({data}) => {
          if (data.deletePositionFromLogisticsRequest.result) {
            this.changeReadyToGoTransferRequestId = null
            this.deleteTransferRequestId = null
            this.transferAllTaskId = null
            this.disbandTaskId = null
            this.deletePositionFromTaskId = null
            this.deletePositionFromLogisticsRequestId = null
            this.commonDialog = false
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Позиция удалена из заявки на закупку'
            })
          }
        })
      },
      deletePositionFromGroup (gId, lrpId) {
        let arrayG = []
        this.groups.forEach(g => {
          if (g.id === gId) {
            let lrp = g.positions.filter(p => p.id === lrpId)
            if (lrp.length !== 0) {
              this.logisticsRequestPositionSetWithoutTasks.push(lrp[0])
            }
            g.positions = g.positions.filter(p => p.id !== lrpId)
          }
          if (g.positions.length !== 0) {
            arrayG.push(g)
          }
          if (g.positions.length === 0) {
            this.tasks = this.tasks.filter(t => t.id !== g.id)
          }
        })
        this.groups = arrayG
        let findTaskForPositionsWithoutTasks = this.tasks.find(task => task.id === 0)
        if (!findTaskForPositionsWithoutTasks) {
          this.tasks.push({id: 0, show: true})
        }
      },
      publishRequest () {
        this.$apollo.mutate({
          mutation: publishRequest,
          variables: {
            input: {
              requestId: this.logisticsRequestObject.id
            }
          }
        }).then(({data}) => {
          if (data.publishRequest.result) {
            this.$apollo.queries.getLogisticsRequestQuery.refetch()
            this.$notify({
              group: 'commonNotification',
              duration: 5000,
              text: 'Заявка передана логистам'
            })
          }
        })
      },
      printTask (taskId) {
        this.positionsToPrint = this.logisticsRequestObject.logisticsrequestpositionSet.filter(position => {
          if (position.task) {
            return position.task.id === taskId
          } else {
            return false
          }
        })
        this.printTaskPositionsDialogShow = true
      }
    }
  }
</script>

<style>
  .border-task {
    border: black solid 1px;
    border-bottom-width: 0;
  }

  div.header-logistic-table table thead th {
    width: 170px;
    max-width: 170px;
    word-wrap: break-word;
    white-space: normal;
  }

  .hover:hover {
    background: #EEEEEE;
  }

  .del {
    text-decoration: line-through red;
  }

  .procurementComplete .procurementWarning {
    background-color: #C8E6C9 !important;
  }

  tr .show-on-hover {
    visibility: hidden;
  }

  tr:hover .show-on-hover {
    visibility: initial;
  }
</style>
