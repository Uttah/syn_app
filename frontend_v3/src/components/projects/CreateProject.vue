<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="1000px">
    <v-btn color="primary" slot="activator">Создать проект</v-btn>
    <v-card overflow-y>
      <v-card-title>
        <span class="title">Создание проекта</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-space-between>
              <v-flex xs12>
                <v-text-field label="Описание" v-model="input.description"  required
                              :rules="descriptionRules" counter="70"/>
              </v-flex>
              <v-flex xs3>
                <workers-select label="Менеджер" v-model="input.managerId" clearable/>
              </v-flex>
              <v-flex xs3>
                <workers-select label="ГИП" v-model="input.gipId" clearable/>
              </v-flex>
              <v-flex xs4>
                <v-select :items="allStatesData" item-text="name" item-value="id" label="Этап" v-model="input.stateId"
                          required :disabled="true" :rules="nonEmptyArrayField"/>
              </v-flex>
              <v-flex xs8>
                <customer-select v-model="input.customerId" required/>
              </v-flex>
              <v-flex xs3>
                <integer-field label="Примерный бюджет" v-model="input.budget" suffix="руб."/>
              </v-flex>
              <v-flex xs12>
                <v-text-field label="Комментарий" v-model="input.comment" multi-line/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="!valid || loading" @click.native="createProject" :loading="loading">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import WorkersSelect from '../WorkersSelect'
  import {createProject} from './query'
  import IntegerField from '../IntegerField'
  import CustomerSelect from '../CustomerSelect'

  export default {
    name: 'CreateProjectDialog',
    components: {
      CustomerSelect,
      IntegerField,
      WorkersSelect
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        allStatesData: [
          {name: 'Э0: Заявка на проработку', id: 8},
          {name: 'Э1: Коммерческая проработка', id: 1}
        ],
        input: {
          gipId: null,
          description: null,
          stateId: 8,
          budget: null,
          customerId: null,
          managerId: null,
          comment: null
        },
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        descriptionRules: [
          text => !!text || 'Поле не может быть пустым',
          text => (typeof text === 'string' && text.length <= 70) || 'Максимальная длина описания - 70 символов',
          text => (typeof text === 'string' && text.length > 0 && text[0] !== '.') || 'Описание не может начинаться с «.»',
          text => (typeof text === 'string' && text.length > 0 && text[text.length - 1] !== '.') || 'Описание не может заканчиваться на «.»'
        ],
        nonEmptyArrayField: [
          array => {
            if (array && Array.isArray(array)) {
              return array.length > 0 || 'Поле не может быть пустым'
            } else {
              return !!array || 'Поле не может быть пустым'
            }
          }
        ],
        validNumber: [
          text => !!text || 'Поле не может быть пустым',
          text => {
            let result = /[^\d]/.test(text)
            if (result) {
              return 'Только цифры'
            }
            return true
          },
          text => {
            if (text && text.length > 5) {
              return 'Максимум 5 цифр'
            }
            return true
          }
        ]
      }
    },
    methods: {
      closeDialog () {
        this.dialog = false
      },
      createProject () {
        this.loading = true
        this.$apollo.mutate(
          {
            mutation: createProject,
            variables: {
              input: this.input
            }
          }
        ).then(({data}) => {
          this.loading = false
          if (data.createProject.project.id) {
            this.dialog = false
            this.$emit('created')
          }
        })
      }
    }
  }
</script>
