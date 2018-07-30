<template>
  <div>
    <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition"
              persistent scrollable :overlay=false>
      <v-card>
        <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
          <v-btn icon @click.native="closeDialog" dark>
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Взаимодействие</v-toolbar-title>
          <v-spacer/>
          <v-toolbar-items>
            <v-btn flat @click="openDeleteDialog" v-if="dataClientHistory.id" :loading="loading">Удалить</v-btn>
            <v-btn flat @click="addChangeClientHistory" :disabled="!valid" :loading="loading">Сохранить</v-btn>
          </v-toolbar-items>
        </v-toolbar>
          <v-card-text class="mx-4">
          <v-form v-model="valid">
            <v-container>
              <v-layout wrap justify-space-between>
                <v-flex xs3>
                  <date-picker label="Дата" v-model="dataClientHistory.date" required :rules="nonEmptyField"/>
                </v-flex>
                <v-spacer/>
                <v-flex xs4>
                  <client-select label="Контрагент" v-model="dataClientHistory.client.id" :disabled="Boolean(dataClientHistory.id)" required :rules="nonEmptyField"/>
                </v-flex>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs12>
                  <v-text-field label="Что делал" v-model="dataClientHistory.interaction" multi-line required :rules="nonEmptyField"/>
                </v-flex>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs12>
                  <v-text-field label="Результат" v-model="dataClientHistory.result" multi-line required :rules="nonEmptyField"/>
                </v-flex>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs3>
                  <date-picker label="Дата следующего шага" v-model="dataClientHistory.nextStepDate" required :rules="nonEmptyField"/>
                </v-flex>
                <v-spacer/>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs12>
                  <v-text-field label="Следующий шаг" v-model="dataClientHistory.nextStep" multi-line required :rules="nonEmptyField"/>
                </v-flex>
              </v-layout>
            </v-container>
          </v-form>
          <v-card>
            <v-card-title>
              <span class="title">Контакты принимавшие участие во взаимодействии</span>
            </v-card-title>
            <v-card-text>
              <v-layout row class="mb-2">
                <v-spacer/>
              </v-layout>
              <contact-select @allContactsData="allContacts" :idClient="dataClientHistory.client.id" v-model="selectedContacts" clearable
              multiple/>
              <contact-dialog withClient @contactData="contactData" :readOnly="true" :contact="contact" ref="contactDialog"/>
              <v-data-table
                :headers="headers"
                :items="dataTable"
                hide-actions
                rows-per-page-text="Строк на странице"
                no-data-text="Нет доступных данных"
                class="elevation-1"
                must-sort
              >
                <template slot="items" slot-scope="props">
                  <tr @click="editContact(props.item)">
                    <td>{{ props.item.lastName }}</td>
                    <td>{{ props.item.firstName }}</td>
                    <td>{{ props.item.patronum }}</td>
                    <td>{{ props.item.position }}</td>
                    <td>{{ props.item.phoneNumber }}</td>
                  </tr>
                </template>
              </v-data-table>

            </v-card-text>
          </v-card>

        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="deleteDialog" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="title">Подтвердите удаление взаимодействия</span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDeleteDialog">Отменить</v-btn>
          <v-btn flat @click="deleteContact">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import {createClientHistory, deleteClientHistory, editClientHistory} from './query'
  import ClientSelect from '../ClientSelect'
  import ContactDialog from './ContactDialog'
  import ContactSelect from '../ContactSelect'
  import DatePicker from '../DatePicker'

  export default {
    name: 'ClientHistoryDialog',
    components: {
      ClientSelect,
      ContactDialog,
      ContactSelect,
      DatePicker
    },
    props: {
      clientHistory: Object
    },
    data () {
      return {
        dialog: false,
        loading: false,
        valid: false,
        deleteDialog: false,
        dataClientHistory: this.clientHistory, // Все данные выбранной Истории
        contact: { // Данные для просмотра Контакта
          id: null,
          lastName: null,
          firstName: null,
          patronum: null,
          position: null,
          phoneNumber: null,
          clientId: null
        },
        allContactsData: [], // Все контакты
        selectedContacts: [], // Выбранные контакты
        dataTable: [], // Контакты в таблице
        headers: [
          {text: 'Фамилия', value: 'lastName'},
          {text: 'Имя', value: 'firstName'},
          {text: 'Отчество', value: 'patronum'},
          {text: 'Должность', value: 'position'},
          {text: 'Телефон', sortable: false, value: 'phoneNumber'}
        ],
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      openDialog () {
        this.dialog = true
      },
      closeDialog () {
        this.dialog = false
      },
      openDeleteDialog () {
        this.deleteDialog = true
      },
      closeDeleteDialog () {
        this.deleteDialog = false
      },
      editContact (val) {
        this.contact = {
          id: val.id,
          lastName: val.lastName,
          firstName: val.firstName,
          patronum: val.patronum,
          position: val.position,
          phoneNumber: val.phoneNumber,
          clientId: this.dataClientHistory.client.id
        }
        this.$refs.contactDialog.openDialog()
      },
      // При изменении Контакта этот Контакт перезаписывается
      contactData (val) {
        this.dataClientHistory.contacts = this.dataClientHistory.contacts.map(function (item) {
          if (item.id === val.id) {
            item = val
          }
          return item
        })
      },
      // ВСЕ КОНТАКТЫ
      // По неизвестной причине срабатывает ДВАЖДЫ. 1 - старое значение, 2 - правильное
      allContacts (val) {
        this.allContactsData = val
      },
      // Тут получаем данные в таблицу Контактов dataTable
      fillTable () {
        if (this.allContactsData.length > 0) {
          // Обнуляем значения таблицы, для того чтобы занести заного
          this.dataTable = []
          let dataTable = []
          // dataTable получает ID элементов таблицы(dataTable - значения которые УЖЕ должны быть в таблице)
          this.selectedContacts.forEach(function (item) {
            dataTable.push(item)
          })
          if (dataTable.length > 0) {
            // Проходим по всем ID и записываем в this.dataTable всю информацию
            dataTable.forEach(function (item) {
              let result = this.allContactsData.find(function (val) {
                return val.id === item
              })
              if (result) {
                this.dataTable.push(result)
              }
            }.bind(this))
          }
        }
      },
      addChangeClientHistory () {
        this.loading = true
        if (this.clientHistory.id) {
          // Редактирование взаимодействия
          this.$apollo.mutate(
            {
              mutation: editClientHistory,
              variables: {
                input: {
                  id: this.dataClientHistory.id,
                  clientId: this.dataClientHistory.client.id,
                  contacts: this.selectedContacts,
                  date: this.dataClientHistory.date,
                  interaction: this.dataClientHistory.interaction,
                  result: this.dataClientHistory.result,
                  nextStepDate: this.dataClientHistory.nextStepDate,
                  nextStep: this.dataClientHistory.nextStep
                }
              }
            }
          ).then(({data}) => {
            this.loading = false
            this.$emit('success')
            this.closeDialog()
          }).catch(() => {
            this.loading = false
          })
        } else {
          // Создание взаимодействия
          this.$apollo.mutate(
            {
              mutation: createClientHistory,
              variables: {
                input: {
                  clientId: this.dataClientHistory.client.id,
                  contacts: this.selectedContacts,
                  date: this.dataClientHistory.date,
                  interaction: this.dataClientHistory.interaction,
                  result: this.dataClientHistory.result,
                  nextStepDate: this.dataClientHistory.nextStepDate,
                  nextStep: this.dataClientHistory.nextStep
                }
              }
            }
          ).then(({data}) => {
            this.loading = false
            this.$emit('success')
            this.closeDialog()
          }).catch(() => {
            this.loading = false
          })
        }
      },
      deleteContact () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: deleteClientHistory,
            variables: {
              input: {
                id: this.dataClientHistory.id
              }
            }
          }
        ).then(({data}) => {
          this.loading = false
          this.$emit('success')
          this.closeDialog()
          this.closeDeleteDialog()
        }).catch(() => {
          this.loading = false
        })
      }
    },
    watch: {
      allContactsData: {
        handler: function () {
          this.fillTable()
        }
      },
      // При открытии этого Диалога заполняет селектор selectedContacts уже выбранными Контактами
      clientHistory: {
        handler: function (val) {
          this.selectedContacts = []
          this.allContactsData = []
          this.dataClientHistory = val
          if (this.dataClientHistory.contacts) {
            this.dataClientHistory.contacts.forEach(function (item) {
              this.selectedContacts.push(item)
            }.bind(this))
          }
        }
      },
      // При изменении списка Контактов
      selectedContacts: {
        handler: function () {
          this.fillTable()
        },
        deep: true
      },
      // Срабатывает при любом закрытии диалога. Обновляет селект. Нужен в случае переоткрытия диалога этого же элемента.
      dialog: {
        handler: function (val) {
          if (!val) {
            this.selectedContacts = []
            if (this.dataClientHistory.contacts) {
              this.dataClientHistory.contacts.forEach(function (item) {
                this.selectedContacts.push(item)
              }.bind(this))
            }
          }
        }
      }
    }
  }
</script>

