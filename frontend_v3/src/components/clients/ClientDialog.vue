<template>
  <div>
    <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition"
              persistent scrollable :overlay=false>
      <v-card>
        <v-toolbar style="flex: 0 0 auto;" color="primary" dense>
          <v-btn icon @click.native="closeDialog" dark>
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>Редактирование контрагента</v-toolbar-title>
          <v-spacer/>
          <v-toolbar-items>
            <v-btn color="darken-1" flat @click="deleteConfirmClient" :loading="loading">Удалить</v-btn>
            <v-btn color="darken-1" flat @click="saveClient" :disabled="!valid" :loading="loading">Сохранить</v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <v-form v-model="valid" xs12>
            <v-container>
              <v-layout v-if="client.kind==2" wrap justify-space-between>
                <v-flex xs5>
                  <v-text-field label="Имя" :rules="nonEmptyField" v-model="client.name"/>
                </v-flex>
                <v-flex xs5>
                  <v-text-field label="Полное имя" v-model="client.fullName"/>
                </v-flex>
              </v-layout>
              <v-layout v-else="client.kind==1" wrap justify-space-between>
                <v-flex xs5>
                  <client-name-picker v-model="client.name"/>
                </v-flex>
                <v-flex xs5>
                  <v-text-field label="Полное наименование" v-model="client.fullName"/>
                </v-flex>
              </v-layout>
              <v-layout wrap justify-space-between>
                <v-flex xs3>
                  <client-kind-select label="Тип контрагента" v-model="client.kind"/>
                </v-flex>
                <v-flex xs3>
                  <client-relation-select label="Взаимоотношения" v-model="client.relation"/>
                </v-flex>
                <v-flex xs3>
                  <v-text-field label="Номер телефона" mask="8 (###) ###-##-##" v-model="client.phoneNumber"/>
                </v-flex>
              </v-layout>

              <v-layout v-if="client.kind==1" wrap justify-space-between>
                <v-flex xs3 class="pr-3">
                  <v-text-field label="ИНН" mask="############" v-model="client.INN"/>
                </v-flex>
                <v-flex xs3 class="px-3">
                  <v-text-field label="КПП" mask="#########" v-model="client.KPP"/>
                </v-flex>
                <v-flex xs3 class="px-3">
                  <v-text-field label="ОКПО" mask="########" v-model="client.OKPO"/>
                </v-flex>
                <v-flex xs3 class="pl-3">
                  <v-text-field label="ОГРН" mask="#############" counter="13" v-model="client.OGRN"/>
                </v-flex>
              </v-layout>

              <v-layout v-if="client.kind==2" wrap justify-space-between>
                <v-flex xs4 class="pr-3">
                  <v-text-field label="ИНН" mask="############" v-model="client.INN"/>
                </v-flex>
                <v-flex xs4 class="px-3">
                  <v-text-field label="ОКПО" mask="########" v-model="client.OKPO"/>
                </v-flex>
                <v-flex xs4 class="pl-3">
                  <v-text-field label="ОГРН" mask="#############" counter="13" v-model="client.OGRN"/>
                </v-flex>
              </v-layout>

              <v-layout wrap>
                <v-flex xs12>
                  <v-text-field label="Юр. адрес" v-model="client.legalAddress"/>
                </v-flex>
              </v-layout>
              <v-layout wrap>
                <v-flex xs12>
                  <v-text-field label="Фактический адрес" v-model="client.streetAddress"/>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs12>
                  <v-text-field label="Другое" v-model="client.other" multi-line/>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs4>
                  <workers-select label="Менеджер" v-model="client.manager"/>
                </v-flex>
                <v-spacer/>
              </v-layout>
            </v-container>
          </v-form>
          <v-card>
            <v-card-title>
              <span class="title">Контакты</span>
            </v-card-title>
            <v-card-text>
              <v-layout row class="mb-2">
                <v-spacer/>
                <v-btn color="primary" dark @click="createContact">Добавить контакт</v-btn>
              </v-layout>
              <contact-dialog @success="success" withClient :contact="contact" ref="contactDialog"/>
              <v-data-table
                :headers="headers"
                :items="allContactsData"
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
    <v-dialog v-model="dialogDelete" max-width="400px">
      <v-card>
        <v-card-title>
          <span class="title">Подтвердите удаление</span>
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDialogDelete" :loading="loading">Отменить</v-btn>
          <v-btn flat @click="deleteClient" :loading="loading">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import gql from 'graphql-tag'
  import ClientKindSelect from '../ClientKindSelect'
  import ClientRelationSelect from '../ClientRelationSelect'
  import WorkersSelect from '../WorkersSelect'
  import ContactSelect from '../ContactSelect'
  import ClientNamePicker from '../ClientNamePicker'
  import ContactDialog from './ContactDialog'
  import {deleteClient, editClient} from './query'

  export default {
    name: 'ClientDialog',
    components: {
      ClientKindSelect,
      ClientRelationSelect,
      WorkersSelect,
      ContactSelect,
      ClientNamePicker,
      ContactDialog
    },
    data () {
      return {
        dialog: false,
        dialogDelete: false,
        loading: false,
        valid: false,
        client: {
          name: null
        },
        contact: {},
        selectedContacts: [],
        allContactsData: [],
        dataTable: [],
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
      // В начале при открытии диалога
      openDialog (val) {
        this.dialog = true
        this.client = val
      },
      closeDialog () {
        this.dialog = false
      },
      closeDialogDelete () {
        this.dialogDelete = false
      },
      deleteConfirmClient () {
        this.dialogDelete = true
      },
      deleteClient () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: deleteClient,
            variables: {
              input: {
                idClient: this.client.id
              }
            }
          }
        ).then(({data}) => {
          this.loading = false
          this.$emit('success')
          this.closeDialogDelete()
          this.closeDialog()
        }).catch(() => {
          this.loading = false
        })
      },
      saveClient () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: editClient,
            variables: {
              input: {
                idClient: this.client.id,
                name: this.client.name,
                kind: this.client.kind,
                relation: this.client.relation,
                fullName: this.client.fullName,
                INN: this.client.INN,
                KPP: this.client.KPP,
                OKPO: this.client.OKPO,
                OGRN: this.client.OGRN,
                legalAddress: this.client.legalAddress,
                streetAddress: this.client.streetAddress,
                phoneNumber: this.client.phoneNumber,
                manager: this.client.manager,
                other: this.client.other
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
      },
      createContact () {
        this.contact = {
          id: null,
          lastName: null,
          firstName: null,
          patronum: null,
          position: null,
          phoneNumber: null,
          clientId: this.client.id
        }
        this.$nextTick(() => {
          this.$refs.contactDialog.openDialog()
        })
      },
      editContact (val) {
        this.contact = {
          id: val.id,
          lastName: val.lastName,
          firstName: val.firstName,
          patronum: val.patronum,
          position: val.position,
          phoneNumber: val.phoneNumber,
          clientId: this.client.id
        }
        this.$refs.contactDialog.openDialog()
      },
      success () {
        this.$apollo.queries.query.refetch()
      }
    },
    apollo: {
      query: {
        query: gql`
          query ($filters: IntID) {
            allContacts (filters: $filters) {
              id
              lastName
              firstName
              patronum
              position
              phoneNumber
              client {
                id
              }
            }
          }`,
        fetchPolicy: 'cache-and-network',
        variables () {
          return {
            filters: this.client.id
          }
        },
        update (data) {
          this.allContactsData = data.allContacts
          return null
        }
      }
    }
  }
</script>

