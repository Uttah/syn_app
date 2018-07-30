<template>
  <v-dialog v-model="dialog" persistent scrollable lazy max-width="1000px">
    <v-card>
      <v-card-title>
        <span class="title">Изменение проекта</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" xs12>
          <v-container>
            <v-layout wrap justify-space-between>
              <v-flex xs12>
                <v-text-field :readonly="!hasPermission()" label="Описание" v-model="input.description"
                              :rules="descriptionRules" counter="70" required/>
              </v-flex>
              <v-flex xs3>
                <workers-select :readonly="!hasPermission()" label="Менеджер" v-model="input.managerId" clearable/>
              </v-flex>
              <v-flex xs3>
                <workers-select :readonly="!hasPermission()" label="ГИП" v-model="input.gipId" clearable/>
              </v-flex>
              <v-flex xs4>
                <v-select :readonly="!hasPermissionChangeState()" :items="allStatesData" item-text="name" item-value="id"
                          label="Этап" v-model="input.stateId" required :rules="nonEmptyArrayField"/>
              </v-flex>
              <v-flex xs8>
                <customer-select :readonly="!hasPermission()" v-model="input.customerId" required/>
              </v-flex>
              <v-flex xs3>
                <integer-field :readonly="!hasPermission()" label="Примерный бюджет" v-model="input.budget" suffix="руб."/>
              </v-flex>
              <v-flex xs12>
                <v-text-field :readonly="!hasPermission()" label="Комментарий" v-model="input.comment" multi-line/>
              </v-flex>
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn flat @click.native="closeDialog" :disabled="loading">Отмена</v-btn>
        <v-btn flat :disabled="!valid || !hasPermission() || loading" @click.native="updateProject" :loading="loading">
          Обновить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
  import WorkersSelect from '../WorkersSelect'
  import IntegerField from '../IntegerField'
  import {allForFillSelect, deleteProject, updateProject} from './query'
  import auth from '../../auth/auth'
  import CustomerSelect from '../CustomerSelect'
  import ClientSelect from '../ClientSelect'

  export default {
    name: 'UpdateDeleteProjectDialog',
    props: [
      'input'
    ],
    components: {
      IntegerField,
      WorkersSelect,
      CustomerSelect,
      ClientSelect
    },
    apollo: {
      query: {
        fetchPolicy: 'cache-and-network',
        query: allForFillSelect,
        update (data) {
          this.allStatesData = data.allStates
        }
      }
    },
    data () {
      return {
        dialog: false,
        valid: false,
        loading: false,
        allStatesData: [],
        nonEmptyField: [
          text => !!text || 'Поле не может быть пустым'
        ],
        descriptionRules: [
          text => !!text || 'Поле не может быть пустым',
          text => (typeof text === 'string' && text.length <= 70) || 'Максимальная длина описания - 70 символов',
          text => (typeof text === 'string' && text.length >= 1 && text[0] !== '.') || 'Описание не может начинаться с «.»'
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
            if (text.length > 5) {
              return 'Максимум 5 цифр'
            }
            return true
          }
        ]
      }
    },
    watch: {
      input: {
        handler: function () {
          this.dialog = true
          this.input.gipId = this.input.gip.id
          this.input.stateId = this.input.state.id
          this.input.managerId = this.input.manager ? this.input.manager.id : null
          this.input.customerId = this.input.customer ? this.input.customer.id : null
          this.$nextTick(() => this.$refs.form.validate())
        },
        deep: true
      }
    },
    methods: {
      hasPermission () {
        let userCreated = (this.input.userCreated && this.input.userCreated.id) ? this.input.userCreated.id : 0
        return auth.hasPermission('user.change_project') || auth.user.id === userCreated
      },
      hasPermissionChangeState () {
        return auth.hasPermission('projects.change_project_state')
      },
      closeDialog () {
        this.dialog = false
      },
      deleteProject () {
        this.loading = true
        this.$apollo.mutate({
          mutation: deleteProject,
          variables: {
            input: {id: this.input.id}
          }
        }).then(({data}) => {
          this.loading = false
          if (data.deleteProject.result === true) {
            this.dialog = false
            this.$emit('deleted')
          }
        }).catch(() => {
          this.loading = false
        })
      },
      updateProject () {
        this.loading = true
        let input = {}
        input.id = this.input.id
        input.gipId = (this.input.gipId && this.input.gipId.id) ? this.input.gipId.id : this.input.gipId
        input.stateId = this.input.stateId.id ? this.input.stateId.id : this.input.stateId
        input.budget = this.input.budget
        input.managerId = (this.input.managerId && this.input.managerId.id) ? this.input.managerId.id : this.input.managerId
        input.customerId = (this.input.customerId && this.input.customerId.id) ? this.input.customerId.id : this.input.customerId
        input.description = this.input.description
        input.comment = this.input.comment
        this.$apollo.mutate({
          mutation: updateProject,
          variables: {
            input: input
          }
        }).then(({data}) => {
          this.loading = false
          if (data.updateProject.project.id) {
            this.dialog = false
            this.$emit('updated')
          }
        }).catch(() => {
          this.loading = false
        })
      }
    }
  }
</script>
