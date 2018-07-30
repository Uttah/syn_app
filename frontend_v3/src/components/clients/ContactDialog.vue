<template>
  <div>
    <v-dialog v-model="dialog" persistent max-width="800px">
      <v-card>
        <v-card-title>
          <span class="title">Контакт</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="valid">
            <v-layout wrap justify-space-between>
              <v-flex xs3>
                <v-text-field label="Фамилия" :readonly="readOnly" :rules="nonEmptyField" v-model="contactData.lastName"/>
              </v-flex>
              <v-flex xs3>
                <v-text-field label="Имя" :readonly="readOnly" :rules="nonEmptyField" v-model="contactData.firstName"/>
              </v-flex>
              <v-flex xs3>
                <v-text-field label="Отчество" :readonly="readOnly" v-model="contactData.patronum"/>
              </v-flex>
            </v-layout>
            <v-layout wrap justify-space-between>
              <v-flex xs5>
                <v-text-field label="Должность" :readonly="readOnly" v-model="contactData.position"/>
              </v-flex>
              <v-flex xs5>
                <v-text-field label="Телефон" :readonly="readOnly" mask="8 (###) ###-##-##" v-model="contactData.phoneNumber"/>
              </v-flex>
            </v-layout>
            <v-layout wrap justify-space-between>
              <v-flex xs4>
                <client-select label="Контрагент" :readonly="readOnly" :disabled="withClient" required
                  v-model="contactData.clientId"/>
              </v-flex>
              <v-spacer/>
            </v-layout>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn flat @click="closeDialog" :loading="loading">Отменить</v-btn>
          <v-btn flat @click="openDeleteDialog" v-if="contactData.id && !readOnly" :loading="loading">Удалить</v-btn>
          <v-btn flat @click="addChangeContact" v-if="!readOnly" :disabled="!valid" :loading="loading">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="deleteDialog" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="title">Подтвердите удаление контакта</span>
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
  import {createContact, editContact, deleteContact} from './query'
  import ClientSelect from '../ClientSelect'

  export default {
    name: 'ContactDialog',
    components: {
      ClientSelect
    },
    props: {
      withClient: Boolean,
      readOnly: Boolean,
      contact: {
        clientId: String,
        firstName: String,
        id: String,
        lastName: String,
        patronum: String,
        phoneNumber: String,
        position: String
      }
    },
    data () {
      return {
        dialog: false,
        loading: false,
        valid: false,
        deleteDialog: false,
        contactData: {
          id: null,
          lastName: null,
          firstName: null,
          patronum: null,
          position: null,
          phoneNumber: null,
          clientId: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ]
      }
    },
    methods: {
      openDialog () {
        this.dialog = true
        this.contactData = this.contact
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
      addChangeContact () {
        this.loading = true
        if (this.contactData.id) {
          // Редактирование контакта
          this.$apollo.mutate(
            {
              mutation: editContact,
              variables: {
                input: {
                  id: this.contactData.id,
                  lastName: this.contactData.lastName,
                  firstName: this.contactData.firstName,
                  patronum: this.contactData.patronum,
                  position: this.contactData.position,
                  phoneNumber: this.contactData.phoneNumber,
                  clientId: this.contactData.clientId
                }
              }
            }
          ).then(({data}) => {
            this.loading = false
            this.$emit('success')
            this.$emit('contactData', this.contactData)
            this.closeDialog()
          }).catch(() => {
            this.loading = false
          })
        } else {
          // Создание контакта
          this.$apollo.mutate(
            {
              mutation: createContact,
              variables: {
                input: {
                  lastName: this.contactData.lastName,
                  firstName: this.contactData.firstName,
                  patronum: this.contactData.patronum,
                  position: this.contactData.position,
                  phoneNumber: this.contactData.phoneNumber,
                  clientId: this.contactData.clientId
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
            mutation: deleteContact,
            variables: {
              input: {
                id: this.contactData.id
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
      contact: {
        handler: function (val) {
          this.contactData = val
        },
        deep: true
      }
    }
  }
</script>

